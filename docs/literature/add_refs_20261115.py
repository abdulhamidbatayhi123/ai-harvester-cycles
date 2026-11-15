"""Append the references added in the final review round (2026-11-15) to docs/literature/T-P4-6_references.bib from
their live Crossref records (no e-mail, no key), in the format of that file, and save the raw records next to it
(docs/literature/add_refs_20261115.json). Entries already in the .bib are skipped.

usage: python -I docs/literature/add_refs_20261115.py
"""
import json
import os
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
BIB = os.path.join(HERE, "T-P4-6_references.bib")
NEW = {  # key: (DOI, verification note)
    "Bezrukov2024Rapid": ("10.1016/j.chempr.2024.01.011", "status B: abstract and public code read (review 2026-11-15)"),
    "Eaby2025Ultramicroporous": ("10.1021/jacs.4c13797", "status A: full text read (Europe PMC PMC11744747, review 2026-11-15)"),
    "Shabangu2025One": ("10.1021/acsmaterialslett.4c02019", "status A: full text read (Europe PMC PMC11795622, review 2026-11-15)"),
    "Kong2026Regeneration": ("10.1002/anie.6095254", "status A: full text read (Europe PMC PMC13725610, review 2026-11-15)"),
    "Ma2025Microscopic": ("10.1021/acs.nanolett.5c00343", "status B: abstract read (review 2026-11-15)"),
    "Frandsen2025Systematic": ("10.1002/aic.70045", "status B: abstract read (review 2026-11-15)"),
}


def crossref(doi):
    req = urllib.request.Request("https://api.crossref.org/works/" + doi,
                                 headers={"User-Agent": "p4-reference-check/1.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["message"]


def tex(s):
    return s.replace("&", "\\&").replace("%", "\\%")


def entry(key, m, note):
    names = " and ".join(f"{a['family']}, {a['given']}" if a.get("given") else a.get("family", a.get("name", ""))
                         for a in m.get("author", []))
    year = (m.get("published-print") or m.get("published-online") or m.get("issued"))["date-parts"][0][0]
    f = [f"  author = {{{names}}}", f"  title = {{{{{tex(m['title'][0])}}}}}",
         f"  journal = {{{tex(m['container-title'][0])}}}", f"  year = {{{year}}}"]
    if m.get("volume"):
        f.append(f"  volume = {{{m['volume']}}}")
    if m.get("issue"):
        f.append(f"  number = {{{m['issue']}}}")
    page = m.get("page") or m.get("article-number")
    if page:
        f.append(f"  pages = {{{page.replace('-', '--')}}}")
    f += [f"  doi = {{{m['DOI']}}}", f"  note = {{Verification {note}}}"]
    return f"@article{{{key},\n" + ",\n".join(f) + "\n}\n"


def main():
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    bib = open(BIB, encoding="utf-8").read()
    raw, add = {}, []
    for key, (doi, note) in NEW.items():
        if "{" + key + "," in bib:
            print("skip (present):", key)
            continue
        m = crossref(doi)
        raw[key] = m
        add.append(entry(key, m, note))
        print(key, "|", m["title"][0][:70], "|", m["container-title"][0], m.get("volume"), m.get("page") or m.get("article-number"))
    if add:
        with open(BIB, "a", encoding="utf-8", newline="\n") as f:
            f.write("\n" + "\n".join(add))
        with open(os.path.join(HERE, "add_refs_20261115.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(raw, f, indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
