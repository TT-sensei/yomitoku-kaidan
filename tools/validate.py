# 文章データ（site/texts/）の検証。使い方: python3 tools/validate.py
import json, os, re, sys
base = os.path.join(os.path.dirname(__file__), "..", "texts")
idx = json.load(open(os.path.join(base, "index.json"), encoding="utf-8"))
errs = []
def plain(s): return re.sub(r"《[^》]*》", "", s or "")
total_q = 0
for f in idx["files"]:
    t = json.load(open(os.path.join(base, f), encoding="utf-8"))
    for k in ["id", "grade", "kind", "title", "sentences", "questions"]:
        if k not in t: errs.append(f"{f}: フィールド {k} がない")
    if len(t["questions"]) != 7: errs.append(f"{f}: 問題数が7でない ({len(t['questions'])})")
    for i, q in enumerate(t["questions"]):
        total_q += 1
        tag = f"{f} q{i+1}({q.get('type')})"
        if "q" not in q or "explain" not in q: errs.append(f"{tag}: q/explain がない")
        if q["type"] in ("evidence", "yousu", "youshi", "kousei", "zuhyou"):
            if q.get("answer") not in (q.get("choices") or []): errs.append(f"{tag}: answer が choices にない")
            if len(q.get("choices") or []) != 3: errs.append(f"{tag}: choices が3つでない")
        if q["type"] in ("evidence", "yousu"):
            ev = q.get("evidence")
            if not isinstance(ev, int) or not (0 <= ev < len(t["sentences"])): errs.append(f"{tag}: evidence の範囲がおかしい")
        if q["type"] == "shiji":
            if q.get("word") not in plain(t["sentences"][q["sentence"]]): errs.append(f"{tag}: word が対象文にない")
            if not q.get("accept"): errs.append(f"{tag}: accept が空")
        if q["type"] in ("shiji", "typein"):
            if not q.get("accept"): errs.append(f"{tag}: accept が空")
            for g in (q.get("keys") or []):
                if not isinstance(g, list) or not g: errs.append(f"{tag}: keys のグループが空")
print(f"texts={len(idx['files'])} questions={total_q} errors={len(errs)}")
for e in errs: print("ERROR:", e)
sys.exit(1 if errs else 0)
