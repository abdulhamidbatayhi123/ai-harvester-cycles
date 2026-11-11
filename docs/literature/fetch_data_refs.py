"""Fetch the metadata of the datasets the paper cites from the DataCite REST API (live; no e-mail, no key).

Writes docs/literature/data_refs.json: for each DOI the creators, title, publisher, year and version as
DataCite returns them, plus the fetch date. paper/tex/make_refs_master.py builds the dataset references
from this file, so no dataset reference is typed by hand.

usage: python -I docs/literature/fetch_data_refs.py
"""
import datetime
import json
import os
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = {  # key: DOI (sources in DATA_SOURCES.md)
    "Bezrukov2023Data": "10.5281/zenodo.6631711",
}


def fetch(doi):
    req = urllib.request.Request("https://api.datacite.org/dois/" + doi,
                                 headers={"User-Agent": "p4-reference-check/1.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        a = json.load(r)["data"]["attributes"]
    return {"doi": a["doi"].lower(),
            "creators": [{"family": c.get("familyName"), "given": c.get("givenName"), "name": c.get("name")}
                         for c in a["creators"]],
            "title": a["titles"][0]["title"], "publisher": a.get("publisher"),
            "year": a.get("publicationYear"), "version": a.get("version"),
            "rights": [x.get("rightsIdentifier") for x in a.get("rightsList", [])]}


def main():
    out = {"fetched": datetime.date.today().isoformat(), "source": "api.datacite.org/dois/<doi>",
           "records": {k: fetch(d) for k, d in DATA.items()}}
    with open(os.path.join(HERE, "data_refs.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
