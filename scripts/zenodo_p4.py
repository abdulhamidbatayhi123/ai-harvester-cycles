"""Create the Zenodo record for the Paper 4 code-and-results archive and reserve its DOI (copied 2026-11-12 from
ai-isotherm-thermo/scripts/zenodo_draft_p3a.py, itself adapted from pinn-machining/zenodo_upload_paperA_api.py,
verified against the live API on 2026-11-09/10). It publishes only with --publish <record id>, which must equal the
record in the state file (the author approved publishing this record on 2026-11-12). (Note, 2026-11-11: the token on this machine, ZENODO_TOKEN in the process or Windows user
environment, never printed, turned out to allow the publish action, contrary to earlier notes; the record 24120765 was
published that day with the author's explicit permission by a separate call to
POST /api/records/<id>/draft/actions/publish. Published records cannot change their files: a later snapshot needs a
new version.)

    python scripts/zenodo_draft_p3a.py                 # create the draft (once) and reserve the DOI
    python scripts/zenodo_draft_p3a.py --upload FILE   # upload FILE (e.g. the git archive of the submitted commit)
    python scripts/zenodo_draft_p3a.py --metadata      # set the full metadata (version, keywords, links) and read it back

State (no token): docs/submission/ZENODO_STATE.json
"""
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = "https://zenodo.org/api"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "docs", "submission", "ZENODO_STATE.json")
UA = "ai-harvester-cycles-deposit/1.0"
OTHER_PROJECT_DRAFTS = {"23661737", "24087443", "24088038", "24101894", "24120765"}   # other projects: never touch

TITLE = ("Code, results and pre-registration for: No detectable gain from predicting water-uptake rate constants "
         "from half-loading humidity: a pre-registered test")
DESC = ("<p>Archive of the repository github.com/abdulhamidbatayhi123/ai-harvester-cycles for the manuscript "
        "\"No detectable gain from predicting water-uptake rate constants from half-loading humidity: a "
        "pre-registered test\" (submitted to AIChE Journal). It contains the pre-registration frozen at git tag "
        "prereg-p4-freeze with its manifest (SHA-256 of the protocol, code and derived data) and its corrections "
        "history, the analysis package (data handling, dry-mass rules, physics models, learned models, confirmatory "
        "runner, decision rule and verdict) with unit tests, the synthetic harnesses and their full records, the "
        "independent re-implementation of the decision rule, every confirmatory, secondary and exploratory result "
        "file with run logs, the figure scripts with provenance, and the manuscript build that checks every number "
        "in the text against its source file. The measurement data (Bezrukov et al., Zenodo 10.5281/zenodo.6631711, "
        "CC BY 4.0) are not redistributed; the README gives the download, checksum and conversion steps. The git "
        "history was filtered once before publication to remove three private documents; COMMIT_MAP.tsv maps old "
        "to new commit hashes.</p>")


VERSION = "v1.0.0"
KEYWORDS = ["metal-organic frameworks", "water sorption kinetics", "linear driving force", "dynamic vapour sorption",
            "atmospheric water harvesting", "held-out validation", "pre-registration", "grey-box machine learning"]


def full_metadata():
    """Metadata set with --metadata (the creation call only set the minimum needed to reserve the DOI)."""
    return {
        "title": TITLE,
        "version": VERSION,
        "description": DESC,
        "creators": [{"person_or_org": {"type": "personal", "given_name": "Abdulhamid", "family_name": "Batayhi",
                                        "name": "Batayhi, Abdulhamid",
                                        "identifiers": [{"scheme": "orcid", "identifier": "0009-0007-0374-6755"}]},
                      "affiliations": [{"name": "Department of Mechatronics Engineering, Faculty of Mechanical "
                                                "Engineering, Yildiz Technical University"}]}],
        "subjects": [{"subject": k} for k in KEYWORDS],
        "languages": [{"id": "eng"}],
        "related_identifiers": [
            {"identifier": "https://github.com/abdulhamidbatayhi123/ai-harvester-cycles", "scheme": "url",
             "relation_type": {"id": "isderivedfrom"}, "resource_type": {"id": "software"}},
            {"identifier": "10.5281/zenodo.6631711", "scheme": "doi",
             "relation_type": {"id": "references"}, "resource_type": {"id": "dataset"}},
        ],
    }


class FileBody:
    def __init__(self, p):
        self.f = open(p, "rb")
        self.n = os.path.getsize(p)

    def read(self, k=-1):
        return self.f.read(k)

    def __len__(self):
        return self.n


def req(method, url, token, body=None, data=None, ctype="application/json", ok=(200, 201, 202, 204)):
    h = {"Authorization": f"Bearer {token}", "User-Agent": UA, "Accept": "application/vnd.inveniordm.v1+json"}
    if body is not None:
        data = json.dumps(body).encode()
    if data is not None:
        h["Content-Type"] = ctype
        if isinstance(data, FileBody):
            h["Content-Length"] = str(data.n)
    for attempt in range(5):
        if isinstance(data, FileBody):
            data.f.seek(0)
        r = urllib.request.Request(url, data=data, method=method, headers=h)
        try:
            with urllib.request.urlopen(r, timeout=3600) as resp:
                txt = resp.read().decode() or "{}"
                return json.loads(txt) if txt.strip().startswith(("{", "[")) else {}
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:600]
            if e.code in (429, 502, 503, 504) and attempt < 4:
                time.sleep(10 * (attempt + 1))
                continue
            raise SystemExit(f"HTTP {e.code} on {method} {url.split('?')[0]}: {msg}")
        except (urllib.error.URLError, TimeoutError):
            if attempt < 4:
                time.sleep(10 * (attempt + 1))
                continue
            raise


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def token():
    t = (os.environ.get("ZENODO_TOKEN") or "").strip().strip('"')
    if not t:
        import winreg
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment")
        t = winreg.QueryValueEx(k, "ZENODO_TOKEN")[0].strip().strip('"')
    return t


def save(st):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(STATE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(st, f, indent=1)


def main():
    tk = token()
    st = json.load(open(STATE, encoding="utf-8")) if os.path.exists(STATE) else {}
    rid = st.get("id")
    if rid in OTHER_PROJECT_DRAFTS:
        raise SystemExit(f"refusing: {rid} belongs to another project")
    if not rid:
        meta = {"metadata": {
            "resource_type": {"id": "software"},
            "title": TITLE,
            "publication_date": time.strftime("%Y-%m-%d"),
            "creators": [{"person_or_org": {"type": "personal", "given_name": "Abdulhamid", "family_name": "Batayhi",
                                            "identifiers": [{"scheme": "orcid",
                                                             "identifier": "0009-0007-0374-6755"}]},
                          "affiliations": [{"name": "Yildiz Technical University"}]}],
            "description": DESC,
            "rights": [{"id": "mit"}],
            "publisher": "Zenodo",
        }, "access": {"record": "public", "files": "public"}, "files": {"enabled": True}}
        d = req("POST", f"{API}/records", tk, meta)
        rid = d["id"]
        st = {"id": rid, "created": time.strftime("%Y-%m-%d %H:%M:%S")}
        save(st)
        print("draft created:", rid)
    if not st.get("doi"):
        d = req("POST", f"{API}/records/{rid}/draft/pids/doi", tk, {})
        st["doi"] = d["pids"]["doi"]["identifier"]
        save(st)
    print("reserved DOI:", st["doi"])
    if "--metadata" in sys.argv:              # full metadata on the existing draft (idempotent: replaces, never appends)
        cur = req("GET", f"{API}/records/{rid}/draft", tk)
        m = cur["metadata"]
        m.update(full_metadata())
        req("PUT", f"{API}/records/{rid}/draft", tk, {"metadata": m, "access": cur.get("access"),
                                                     "files": cur.get("files"), "pids": cur.get("pids")})
        back = req("GET", f"{API}/records/{rid}/draft", tk)["metadata"]
        def bare(x):                          # the server adds display titles to vocabulary entries
            if isinstance(x, dict):
                return {a: bare(b) for a, b in x.items() if a not in ("title", "props")}
            return [bare(y) for y in x] if isinstance(x, list) else x
        for k in ("version", "subjects", "related_identifiers", "creators", "languages"):
            if bare(back.get(k)) != bare(m.get(k)):
                raise SystemExit(f"metadata field {k} did not round-trip: {back.get(k)!r}")
        print("metadata set and read back:", ", ".join(sorted(full_metadata())))
    if "--upload" in sys.argv:
        p = sys.argv[sys.argv.index("--upload") + 1]
        n = os.path.basename(p)
        local = md5(p)
        have = {e["key"]: e for e in req("GET", f"{API}/records/{rid}/draft/files", tk).get("entries", [])}
        for k in have:                       # one snapshot only: replace any earlier upload
            req("DELETE", f"{API}/records/{rid}/draft/files/{k}", tk)
        req("POST", f"{API}/records/{rid}/draft/files", tk, [{"key": n}])
        req("PUT", f"{API}/records/{rid}/draft/files/{n}/content", tk, data=FileBody(p),
            ctype="application/octet-stream")
        c = req("POST", f"{API}/records/{rid}/draft/files/{n}/commit", tk)
        if c.get("checksum") != f"md5:{local}":
            raise SystemExit(f"CHECKSUM MISMATCH {n}: zenodo {c.get('checksum')} local md5:{local}")
        st["file"] = {"name": n, "md5": local, "bytes": os.path.getsize(p)}
        save(st)
        print(f"uploaded {n}, md5 verified")
    if "--publish" in sys.argv:
        want = sys.argv[sys.argv.index("--publish") + 1]
        if str(want) != str(rid) or rid in OTHER_PROJECT_DRAFTS or not st.get("file"):
            raise SystemExit(f"refusing to publish: asked {want}, state {rid}, file uploaded: {bool(st.get('file'))}")
        d = req("POST", f"{API}/records/{rid}/draft/actions/publish", tk, {})
        st["published"] = time.strftime("%Y-%m-%d %H:%M:%S")
        save(st)
        print("PUBLISHED:", d.get("links", {}).get("self_html") or f"https://zenodo.org/records/{rid}")
        return
    print("NOT PUBLISHED. Draft:", f"https://zenodo.org/uploads/{rid}")


if __name__ == "__main__":
    main()
