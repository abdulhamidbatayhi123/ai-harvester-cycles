"""Fetch the metadata of the datasets the paper cites from the DataCite REST API (live; no e-mail, no key).

Writes docs/literature/data_refs.json: for each DOI the creators, title, publisher, year and version as
DataCite returns them, plus the fetch date. paper/tex/make_refs_master.py builds the dataset references
from this file, so no dataset reference is typed by hand.

usage: python -I docs/literature/fetch_data_refs.py
"""
import datetime
import json
import os
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = {  # key: DOI (sources in DATA_SOURCES.md)
    "Bezrukov2023Data": "10.5281/zenodo.6631711",
    # the paper's own code-and-results archive (Wiley data policy: shared data are cited in the reference list);
    # until the record is published and registered at DataCite, its metadata is read from the Zenodo draft
    "Batayhi2026Archive": "10.5281/zenodo.24148229",
}
ROOT = os.path.dirname(os.path.dirname(HERE))


def zenodo_draft(doi):
    """Metadata of this project's own Zenodo draft (id from docs/submission/ZENODO_STATE.json), read live through
    the API with the machine's token (never printed). Used only for the project's own record before publication."""
    st = json.load(open(os.path.join(ROOT, "docs", "submission", "ZENODO_STATE.json"), encoding="utf-8"))
    assert st["doi"].lower() == doi.lower(), "not this project's record"
    tok = os.environ.get("ZENODO_TOKEN", "").strip().strip('"')
    req = urllib.request.Request(f"https://zenodo.org/api/records/{st['id']}/draft",
                                 headers={"Authorization": f"Bearer {tok}", "User-Agent": "p4-reference-check/1.0",
                                          "Accept": "application/vnd.inveniordm.v1+json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        m = json.load(r)["metadata"]
    return {"doi": doi.lower(),
            "creators": [{"family": c["person_or_org"].get("family_name"), "given": c["person_or_org"].get("given_name"),
                          "name": c["person_or_org"].get("name")} for c in m["creators"]],
            "title": m["title"], "publisher": m.get("publisher", "Zenodo"),
            "year": int(m["publication_date"][:4]), "version": m.get("version"),
            "rights": [x.get("id") for x in m.get("rights", [])], "source": "Zenodo draft API (not yet published)"}


def fetch(doi):
    req = urllib.request.Request("https://api.datacite.org/dois/" + doi,
                                 headers={"User-Agent": "p4-reference-check/1.0", "Accept": "application/json"})
    try:
        r = urllib.request.urlopen(req, timeout=60)
    except urllib.error.HTTPError as e:
        if e.code == 404 and doi.lower() == DATA["Batayhi2026Archive"]:
            return zenodo_draft(doi)
        raise
    with r:
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
