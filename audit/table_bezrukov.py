"""Build the per-sorbent table of section 2.3 from results/bezrukov_inventory.jsonl."""
import json, sys, collections
sys.stdout.reconfigure(encoding="utf-8")
recs = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8")]
kind = lambda r: "iso" if len(r["rh_target_values"]) >= 6 else ("cyc" if "eatmap" in r["file"] else "step")
g = collections.defaultdict(list)
for r in recs:
    parts = r["file"].split("/")
    if parts[1] in ("27C", "60C"):
        g[(parts[0], parts[1], kind(r))].append(r)
def cell(rs, show_mass=True):
    if not rs: return "none"
    m = sorted(r["initial_mass_mg"] for r in rs if r["initial_mass_mg"] == r["initial_mass_mg"])
    h = sum(r["duration_min"] for r in rs) / 60
    ms = (f", {m[0]:.0f} to {m[-1]:.0f} mg" if round(m[0]) != round(m[-1]) else f", {m[0]:.0f} mg") if m else ""
    return f"{len(rs)} file{'s' if len(rs) > 1 else ''}{ms}, {h:.0f} h"
def iso(mat):
    out = []
    for T in ("27C", "60C"):
        rs = g.get((mat, T, "iso"), [])
        for r in rs: out.append(f"{r['temp_target_values'][0]:.0f} °C")
    return ", ".join(out)
print("| Sorbent | Isotherms (set temperature) | Step runs 27 °C | Step runs 60 °C | Cycling 27 °C |")
print("|---|---|---|---|---|")
for mat in ["ROS-037","ROS-039","ROS-040","MOF-303","MIL-160","CAU-10","Al-fumarate","Syloid","ROS-037_composite","ROS-039_composite"]:
    print(f"| {mat} | {iso(mat)} | {cell(g.get((mat,'27C','step'),[]))} | {cell(g.get((mat,'60C','step'),[]))} | {cell(g.get((mat,'27C','cyc'),[]))} |")
for r in recs:
    if r["file"].startswith("100_cycles"): print(r["file"], r["sample"], r["duration_min"]/60, r["rh_target_up_steps"])
