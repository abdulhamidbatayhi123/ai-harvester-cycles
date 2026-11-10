"""T-P4-5 helper part 2: alternative criterion-4 thresholds with an explicit fold-dependence allowance.
Writes null_dependence_extra.json."""
import json, os
import numpy as np
from scipy.stats import binom, beta, betabinom
from scipy.optimize import brentq
OUT = os.path.dirname(os.path.abspath(__file__))
cp = lambda k, n: float(beta.ppf(0.95, k + 1, n - k)) if k < n else 1.0
def p_ge7(p, rho):
    if rho == 0: return float(binom.sf(6, 8, p))
    return float(betabinom.sf(6, 8, p * (1 - rho) / rho, (1 - p) * (1 - rho) / rho))
res = {}
res["p_max_alpha0.05_rho0.15"] = float(brentq(lambda p: p_ge7(p, 0.15) - 0.05, 1e-4, 0.999))
res["p_max_alpha0.025_rho0.15"] = float(brentq(lambda p: p_ge7(p, 0.15) - 0.025, 1e-4, 0.999))
res["implied_alpha_at_bound_0.40"] = {f"rho{r}": p_ge7(0.40, r) for r in (0.0, 0.05, 0.1, 0.15, 0.2, 0.3)}
res["CP95_k_of_24"] = {str(k): cp(k, 24) for k in range(0, 8)}
res["CP95_k_of_32"] = {str(k): cp(k, 32) for k in range(0, 10)}
# design-effect (Kish) CP: n_eff = n/(1+7 rho), k_eff = k/(1+7 rho), using the beta form with real-valued k
def cp_eff(k, n, rho):
    de = 1 + 7 * rho; ke, ne = k / de, n / de
    return float(beta.ppf(0.95, ke + 1, ne - ke)) if ke < ne else 1.0
res["CP95_design_effect_rho0.15_k_of_24"] = {str(k): cp_eff(k, 24, 0.15) for k in range(0, 8)}
# operating characteristics: rule A = current (CP(k,24) <= 0.40 and max per rep <= 4)
#                            rule B = proposed (CP_eff(k,24, rho_U=0.15) <= p_max(rho=0.15, alpha=0.05) and max per rep <= 4)
pm = res["p_max_alpha0.05_rho0.15"]
rng = np.random.default_rng(12)
oc = {}
for r in (0.0, 0.1, 0.2):
    for p in (0.05, 0.1, 0.2, 0.3, 0.4):
        N = 40000
        q = np.full((N, 3), p) if r == 0 else rng.beta(p * (1 - r) / r, (1 - p) * (1 - r) / r, (N, 3))
        K = rng.binomial(8, q); tot = K.sum(1); bmax = K.max(1) <= 4
        A = np.array([cp(t, 24) <= 0.40 for t in range(25)])[tot] & bmax
        B = np.array([cp_eff(t, 24, 0.15) <= pm for t in range(25)])[tot] & bmax
        oc[f"rho{r}_p{p}"] = {"true_P_supported_H0": p_ge7(p, r), "pass_current": float(A.mean()), "pass_proposed": float(B.mean())}
res["operating_characteristics_3reps"] = oc
res["max_k_of_24_proposed"] = max(k for k in range(25) if cp_eff(k, 24, 0.15) <= pm)
res["max_k_of_32_proposed"] = max(k for k in range(33) if cp_eff(k, 32, 0.15) <= pm)
# ANOVA (moment) estimator of rho from replicate counts, and its spread with 3 replicates
def rho_hat(K):
    p = K.mean() / 8
    if p in (0, 1): return np.nan
    return (K.var(ddof=1) / (8 * p * (1 - p)) - 1) / 7
sp = {}
for r in (0.0, 0.1, 0.2):
    q = np.full((20000, 3), 0.25) if r == 0 else rng.beta(0.25 * (1 - r) / r, 0.75 * (1 - r) / r, (20000, 3))
    K = rng.binomial(8, q); rh = np.array([rho_hat(k) for k in K]); rh = rh[np.isfinite(rh)]
    sp[f"true_rho{r}_p0.25"] = {"q05": float(np.quantile(rh, 0.05)), "median": float(np.median(rh)), "q95": float(np.quantile(rh, 0.95))}
res["rho_hat_from_3_replicates_spread"] = sp
# pre-d replicate (5 LOSO folds; T-P4-5 message and results/null_rep0_preD/decide.json)
res["preD_beats"] = "2/5"; res["preD_CP95"] = cp(2, 5)
json.dump(res, open(os.path.join(OUT, "null_dependence_extra.json"), "w"), indent=1)

# rule C: CP(k,24) <= 0.38 (alpha 0.05 at rho 0.15) and max per rep <= 4
oc2 = {}
rng2 = np.random.default_rng(13)
for r in (0.0, 0.1, 0.15, 0.2):
    for p in (0.1, 0.2, 0.3, 0.35, 0.4):
        N = 40000
        q = np.full((N, 3), p) if r == 0 else rng2.beta(p * (1 - r) / r, (1 - p) * (1 - r) / r, (N, 3))
        K = rng2.binomial(8, q); tot = K.sum(1); bmax = K.max(1) <= 4
        A = np.array([cp(t, 24) <= 0.40 for t in range(25)])[tot] & bmax
        C = np.array([cp(t, 24) <= 0.38 for t in range(25)])[tot] & bmax
        oc2[f"rho{r}_p{p}"] = {"true_P_supported_H0": p_ge7(p, r), "pass_0.40": float(A.mean()), "pass_0.38": float(C.mean())}
res["operating_characteristics_0.40_vs_0.38"] = oc2
res["p_max_alpha0.05"] = {f"rho{r}": float(brentq(lambda p: p_ge7(p, r) - 0.05, 1e-4, 0.999)) for r in (0.0, 0.05, 0.1, 0.12, 0.15, 0.2)}
json.dump(res, open(os.path.join(OUT, "null_dependence_extra.json"), "w"), indent=1)

# (added in-session) whole-decision simulation: CP95 upper bound when 0 of n replicates end "supported"
# res["whole_decision_sim_CP95_0_supported_of_n_replicates"] = {str(n): float(beta.ppf(0.95, 1, n)) for n in (3, 4, 10, 59)}
