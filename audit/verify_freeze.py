"""Check FREEZE_MANIFEST.json against the working tree: the SHA-256 of every listed file (text files with line endings
converted to LF, as the manifest was written; keys written with Windows backslashes are read as '/'), and the combined
hash of data_derived/ (which is git-ignored and must first be rebuilt with audit/extract_dvs.py).

Recipe of data_derived.combined_sha256: over the files of data_derived/bezrukov2023 sorted by their path
'data_derived/bezrukov2023/<file>', feed for each file the UTF-8 bytes of that path, one NUL byte and the file's raw
32-byte SHA-256 digest (files hashed as stored, no line-ending conversion).

usage: python -I audit/verify_freeze.py            (prints one line per file; exit 1 on any unexplained mismatch)
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXT = (".py", ".md", ".json", ".jsonl", ".txt", ".tsv", ".csv", ".tex", ".bat", ".ps1", ".sh", ".cff", ".ini")
# changed after the freeze and disclosed (manuscript Section 2.10, README): figure appearance and figure-data export
DISCLOSED = {"p4/figstyle.py"}


def sha_lf(path):
    b = open(path, "rb").read()
    if path.endswith(TEXT):
        b = b.replace(b"\r\n", b"\n")
    return hashlib.sha256(b).hexdigest()


def combined(folder_rel):
    h = hashlib.sha256()
    folder = os.path.join(ROOT, folder_rel)
    paths = sorted(f"{folder_rel}/{f}" for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)))
    for p in paths:
        h.update(p.encode("utf-8") + b"\0" + hashlib.sha256(open(os.path.join(ROOT, p), "rb").read()).digest())
    return h.hexdigest(), len(paths)


def main():
    m = json.load(open(os.path.join(ROOT, "FREEZE_MANIFEST.json"), encoding="utf-8"))
    bad = 0
    for key, want in m["files"].items():
        rel = key.replace("\\", "/")
        p = os.path.join(ROOT, rel)
        got = sha_lf(p) if os.path.exists(p) else "missing"
        ok = got == want
        note = "ok" if ok else ("changed after the freeze (disclosed)" if rel in DISCLOSED else "MISMATCH")
        bad += (not ok) and rel not in DISCLOSED
        print(f"{note:38s} {rel}")
    dd = m.get("data_derived")
    if dd:
        folder = "data_derived/bezrukov2023"
        if os.path.isdir(os.path.join(ROOT, folder)):
            got, n = combined(folder)
            ok = got == dd.get("combined_sha256")
            bad += not ok
            print(f"{'ok' if ok else 'MISMATCH':38s} {folder}/ combined over {n} files")
        else:
            print(f"{'skipped (not rebuilt)':38s} {folder}/")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
