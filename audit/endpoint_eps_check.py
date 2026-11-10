import sys, os, numpy as np
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.join(os.getcwd(), "audit"))
import harness_b2 as H
from p4.dataset import build_groups
from p4.run_study import endpoint_eps, endpoint_oracle_E, physics_E, simulate_b0
real = [g for g in build_groups("data_derived/bezrukov2023") if g["sorbent"] in H.PRIMARY8 or g["sorbent"].endswith("_composite")]
k = H.fit_k2([g for g in real if g["sorbent"] in H.PRIMARY8], metric=False)
syn, info, _ = H.synthesise(real, k, "S0")
est = endpoint_eps(syn)
for (s, T), v in sorted(est.items()):
    print(f"{s:20s} {T} true {info[s+'|'+T]['eps']:+.4f} est {v:+.4f}")
te = [g for g in syn if g["sorbent"] == "MOF-303"]
print("E_B0", np.nanmedian(physics_E(te, simulate_b0, k, False)), "E_eq", np.nanmedian(endpoint_oracle_E(te, k, False, est)))
