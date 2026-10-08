"""Rescore every saved reply in results/*.jsonl with the current scorer (no model calls)."""
import collections, json, pathlib, sys
sys.path.insert(0, ".")
import identity_task as t

modes = {tag: mode for tag, mode, _ in t.PROBES}
rows = []
for f in sorted(pathlib.Path("results").glob("*.jsonl")):
    by = collections.defaultdict(list)
    changed = 0
    for line in f.open():
        d = json.loads(line)
        b, why = t.score(d["reply"], d["family"], modes[d["probe"]])
        changed += b != d["bucket"]
        by[d["probe"]].append(b)
    verdicts = {}
    for p, bs in by.items():
        v, n = collections.Counter(bs).most_common(1)[0]
        verdicts[p] = v if n >= 2 else "split"
    c = collections.Counter(verdicts.values())
    scored = len(t.PROBES) - c["error"]
    rows.append((f.stem, c["honest"] / scored if scored else -1, c["impostor"], c["dodge"], c["split"], c["error"], changed,
                 [p for p, v in verdicts.items() if v == "impostor"]))
for name, sc, imp, dod, spl, err, ch, ip in sorted(rows, key=lambda r: -r[1]):
    shown = "INVALID" if sc < 0 else f"{sc:5.0%}"
    print(f"{name:42} honest {shown:>7}  impostor {imp:2}  dodge {dod:2}  split {spl}  error {err:2}  rebucketed {ch:2}  impostor on: {ip}")
