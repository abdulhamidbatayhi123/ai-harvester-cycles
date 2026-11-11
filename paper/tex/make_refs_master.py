"""Write paper/tex/refs_master.json from the verified reference base docs/literature/T-P4-6_references.bib.

Every field comes from that .bib, which was generated from live Crossref / DataCite records (2026-11-10;
raw records in docs/literature/T-P4-6_verification.json). Nothing is typed by hand here. Source style
(Nature-like, as in Paper 3A before its venue was chosen):
    Au, I. I., Au, I. & Au, I. Title. \\textit{Journal} \\textbf{Vol}, Page (Year). doi:...
Journal names are kept in full until the venue is chosen (build_ms.py REF_STYLE); the verification status
(A, B, C) of each entry is kept in 'status', and C entries must be read before a specific claim is cited.

usage: python -I paper/tex/make_refs_master.py            (writes paper/tex/refs_master.json)
       python -I paper/tex/make_refs_master.py --check    (exit 1 if the file differs from a fresh build)
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BIB = os.path.join(ROOT, "docs", "literature", "T-P4-6_references.bib")
DATA = os.path.join(ROOT, "docs", "literature", "data_refs.json")
OUT = os.path.join(HERE, "refs_master.json")
BS = chr(92)


def parse_bib(text):
    """Entries of a .bib written by the T-P4-6 builder: {key: {"type": t, field: value}} (balanced braces)."""
    out = {}
    for m in re.finditer(r"@(\w+)\{([^,]+),", text):
        typ, key = m.group(1).lower(), m.group(2).strip()
        i, depth = m.end(), 1
        j = i
        while depth:
            c = text[j]
            depth += (c == "{") - (c == "}")
            j += 1
        body = text[i:j - 1]
        fields = {"type": typ}
        k = 0
        while True:
            f = re.compile(r"\s*(\w+)\s*=\s*\{").match(body, k)
            if not f:
                break
            name, s = f.group(1).lower(), f.end()
            d, e = 1, s
            while d:
                d += (body[e] == "{") - (body[e] == "}")
                e += 1
            fields[name] = body[s:e - 1].strip()
            k = e
            while k < len(body) and body[k] in ", \n\r\t":
                k += 1
        out[key] = fields
    return out


def initials(given):
    """'Mei-Yan' -> 'M.-Y.', 'Ricky T. Q.' -> 'R. T. Q.', 'George Em' -> 'G. E.'"""
    parts = []
    for w in given.replace(".", ". ").split():
        sub = [s for s in w.split("-") if s]
        parts.append("-".join(s[0] + "." for s in sub))
    return " ".join(parts)


def tex_escape(s):
    """Escape the TeX specials the Crossref strings can contain; leave ones the .bib already escaped."""
    for c in "&%_#":
        s = re.sub(r"(?<!\\)" + re.escape(c), lambda m: BS + m.group(0), s)
    return s


def authors(field):
    names = []
    for a in [x.strip() for x in field.split(" and ")]:
        if "," in a:
            last, given = [x.strip() for x in a.split(",", 1)]
            names.append(f"{last}, {initials(given)}" if given else last)
        else:
            names.append(a)
    names = [tex_escape(n) for n in names]
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " " + BS + "& " + names[-1]


def title(field):
    t = field
    while t.startswith("{") and t.endswith("}"):
        t = t[1:-1]
    t = tex_escape(t).strip()
    return t if t.endswith(("?", ".", "!")) else t + "."


def entry(f):
    a, t, y = authors(f["author"]), title(f["title"]), f["year"]
    if f["type"] == "misc" and f.get("eprint"):
        return f"{a} {t} Preprint at arXiv:{f['eprint']} ({y}). doi:{f['doi']}"
    page = f.get("pages") or f.get("eid") or ""
    page = page.replace("--", "-").split("-")[0] if page else ""
    vol = BS + "textbf{" + f["volume"] + "}" if f.get("volume") else ""
    src = BS + "textit{" + tex_escape(f["journal"]) + "}"
    mid = ", ".join(x for x in (vol, page) if x)
    return f"{a} {t} {src} {mid} ({y}). doi:{f['doi']}".replace("  ", " ")


def data_entry(r):
    """Dataset reference from a DataCite record (docs/literature/data_refs.json). DataCite may give the whole
    name in one field; the family name is then the last word."""
    names = []
    for c in r["creators"]:
        if c.get("given"):
            fam, giv = c["family"], c["given"]
        else:
            full = (c.get("name") or c["family"]).split()
            fam, giv = full[-1], " ".join(full[:-1])
        names.append(f"{fam}, {initials(giv)}" if giv else fam)
    names = [tex_escape(n) for n in names]
    a = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " " + BS + "& " + names[-1]
    return f"{a} {title(r['title'])} \\textit{{{tex_escape(r['publisher'])}}} ({r['year']}). doi:{r['doi']}"


# Journal style. "ama" for AIChE Journal (author guidelines read live 2026-11-11: AMA style, references numbered in
# citation order, all authors listed); "source" is the neutral style used before the venue was chosen.
STYLE = "ama"


def ama_initials(given):
    """AMA initials: no periods or spaces; hyphenated names keep the hyphen ('Mei-Yan' -> 'M-Y', 'Ricky T. Q.' -> 'RTQ')."""
    out = ""
    for w in given.replace(".", " ").split():
        sub = [s for s in w.split("-") if s]
        out += "-".join(s[0] for s in sub)
    return out


def ama_names(pairs):
    names = [tex_escape(f"{fam} {ama_initials(giv)}".strip()) for fam, giv in pairs]
    return ", ".join(names) + "."


def bib_pairs(field):
    out = []
    for a in [x.strip() for x in field.split(" and ")]:
        if "," in a:
            last, given = [x.strip() for x in a.split(",", 1)]
            out.append((last, given))
        else:
            out.append((a, ""))
    return out


def ama_entry(f):
    a, t, y = ama_names(bib_pairs(f["author"])), title(f["title"]), f["year"]
    if f["type"] == "misc" and f.get("eprint"):
        return f"{a} {t} \\textit{{arXiv}}. Preprint posted online {y}. doi:{f['doi']}"
    vol = f.get("volume", "")
    iss = f"({f['number']})" if f.get("number") else ""
    page = (f.get("pages") or f.get("eid") or "").replace("--", "-").replace("-", "--")
    loc = f"{vol}{iss}" + (f":{page}" if page else "")
    return f"{a} {t} \\textit{{{tex_escape(f['journal'])}}}. {y};{loc}. doi:{f['doi']}"


def ama_data(r):
    pairs = []
    for c in r["creators"]:
        if c.get("given"):
            pairs.append((c["family"], c["given"]))
        else:
            full = (c.get("name") or c["family"]).split()
            pairs.append((full[-1], " ".join(full[:-1])))
    return f"{ama_names(pairs)} {title(r['title'])} {tex_escape(r['publisher'])}; {r['year']}. doi:{r['doi']}"


def build():
    bib = parse_bib(open(BIB, encoding="utf-8").read())
    entries, status = {}, {}
    for k, f in bib.items():
        entries[k] = ama_entry(f) if STYLE == "ama" else entry(f)
        m = re.search(r"status\s+([ABC])", f.get("note", ""))
        status[k] = m.group(1) if m else "?"
    data = json.load(open(DATA, encoding="utf-8"))
    for k, r in data["records"].items():
        entries[k] = ama_data(r) if STYLE == "ama" else data_entry(r)
        status[k] = "A"   # DataCite record read live; the deposit itself downloaded and checksummed (DATA_SOURCES.md)
    return {"about": ("Master reference list of the Paper 4 manuscript (paper/tex/main.tex, si.tex), written by "
                      "paper/tex/make_refs_master.py from docs/literature/T-P4-6_references.bib (live Crossref / "
                      "DataCite records, 2026-11-10). Status C entries: metadata only; read before citing a "
                      "specific claim. Style: " + STYLE + " (AMA for AIChE Journal, chosen 2026-11-11)."),
            "status": status, "open": {k: "status C: read the paper before citing a specific claim"
                                       for k, s in status.items() if s == "C"},
            "entries": entries}


def main():
    new = json.dumps(build(), indent=1, ensure_ascii=False) + "\n"
    if "--check" in sys.argv:
        cur = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        sys.exit(0 if cur == new else 1)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(new)
    print(f"{len(json.loads(new)['entries'])} entries -> {OUT}")


if __name__ == "__main__":
    main()
