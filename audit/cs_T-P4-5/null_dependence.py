"""T-P4-5 helper (cs-org2): fold dependence, criterion-4 operating characteristics, and the
population-level structure of the null rate factor. Light compute only. Writes null_dependence.json."""
import json, os, sys
import numpy as np
from scipy.stats import binom, beta, betabinom, norm
from scipy.optimize import minimize_scalar, brentq
OUT = os.path.dirname(os.path.abspath(__file__))
res = {}
# 1. binomial checks of cc's numbers
res["binom_P_ge7_of_8"] = {str(p): float(binom.sf(6, 8, p)) for p in (0.2, 0.3, 0.4, 0.473, 0.529)}
cp = lambda k, n: float(beta.ppf(0.95, k + 1, n - k)) if k < n else 1.0
res["CP95_upper"] = {f"{k}/{n}": cp(k, n) for n in (5, 8, 16, 24, 32) for k in range(0, 7) if k <= n}
res["max_beats_with_CP_le_0.40"] = {str(n): max([k for k in range(n + 1) if cp(k, n) <= 0.40], default=None) for n in (16, 24, 32)}
# 2. beta-binomial (exchangeable folds, intra-replicate correlation rho)
def p_ge7(p, rho):
    if rho == 0: return float(binom.sf(6, 8, p))
    a = p * (1 - rho) / rho; b = (1 - p) * (1 - rho) / rho
    return float(betabinom.sf(6, 8, a, b))
rhos = (0.0, 0.05, 0.1, 0.2, 0.3, 0.5)
res["betabinom_P_ge7"] = {f"rho{r}": {str(p): p_ge7(p, r) for p in (0.1, 0.2, 0.3, 0.4)} for r in rhos}
pmax = {}
for alpha in (0.05, 0.025):
    for r in rhos:
        f = lambda p: p_ge7(p, r) - alpha
        pmax[f"alpha{alpha}_rho{r}"] = float(brentq(f, 1e-4, 0.999)) if f(1e-4) < 0 < f(0.999) else None
res["p_max_for_P_ge7_le_alpha"] = pmax
# design effect for CP pooled over replicates of 8 folds
res["design_effect_1+7rho"] = {f"rho{r}": 1 + 7 * r for r in rhos}
# 3. operating characteristic of criterion 4 (a)+(b), 3 replicates x 8 folds, beta-binomial worlds
rng = np.random.default_rng(11)
oc = {}
for r in (0.0, 0.1, 0.2, 0.3):
    for p in (0.1, 0.2, 0.3, 0.4):
        N = 40000
        if r == 0: q = np.full((N, 3), p)
        else: q = rng.beta(p * (1 - r) / r, (1 - p) * (1 - r) / r, (N, 3))
        K = rng.binomial(8, q)
        tot = K.sum(1)
        a_ok = np.array([cp(int(t), 24) <= 0.40 for t in range(25)])[tot]
        b_ok = K.max(1) <= 4
        oc[f"rho{r}_p{p}"] = {"P_null_study_passes_a_and_b": float((a_ok & b_ok).mean()),
                              "true_P_supported_under_H0": p_ge7(p, r)}
res["criterion4_operating_characteristic_3reps"] = oc
# 4. stylised learner with shared training sorbents: ICC of null beats within a replicate.
# The ridge prediction is linear in b, so bh_i = W[i] @ b is precomputed per fold and worlds are vectorised.
def world_sim(q_dim, lam, e0, mu_sd=0.0, n_world=20000, seed=0):
    g = np.random.default_rng(seed)
    Z = g.normal(size=(8, q_dim))                   # fixed isotherm descriptors of 8 sorbents
    W = np.zeros((8, 8))
    for i in range(8):
        v = (i + 1) % 8                               # validation sorbent, excluded from the fit
        tr = [j for j in range(8) if j not in (i, v)]
        X = np.c_[np.ones(len(tr)), Z[tr]]
        A = np.linalg.solve(X.T @ X + lam * np.diag([0] + [1] * q_dim), X.T)
        W[i, tr] = np.r_[1, Z[i]] @ A
    mu = g.normal(0, mu_sd, (n_world, 1)) if mu_sd else np.zeros((n_world, 1))
    b = mu + g.normal(0, 1, (n_world, 8))
    bh = b @ W.T
    R = 1 - np.sqrt(e0 ** 2 + (b - bh) ** 2) / np.sqrt(e0 ** 2 + b ** 2)
    K = (R >= 0.10).sum(1)
    p = K.mean() / 8
    var_bin = 8 * p * (1 - p)
    rho = (K.var() / var_bin - 1) / 7 if var_bin > 0 else None
    return {"p_fold": float(p), "icc_rho": float(rho), "P_ge7_observed": float((K >= 7).mean()),
            "P_ge7_if_independent": float(binom.sf(6, 8, p)), "P_ge5_in_a_replicate": float((K >= 5).mean()),
            "mean_r": float(R.mean()), "median_r": float(np.median(R))}
st = {}
for qd in (1, 3):
    for lam in (0.1, 3.0):
        for e0 in (0.5, 1.0):
            st[f"q{qd}_lam{lam}_e0{e0}"] = world_sim(qd, lam, e0, n_world=40000, seed=qd * 100 + int(lam * 10) + int(e0 * 10))
for mu_sd in (0.5, 1.0):
    st[f"q1_lam0.1_e00.5_popLean{mu_sd}"] = world_sim(1, 0.1, 0.5, mu_sd=mu_sd, n_world=40000, seed=7 + int(mu_sd * 10))
res["stylised_learner_shared_training"] = st
res["stylised_learner_note"] = ("8 sorbents with fixed random descriptors Z (dim q); per world b ~ N(mu, 1) per sorbent, "
    "mu = 0 unless popLean; fold i fits ridge(lam, free intercept) of b on Z over 6 training sorbents (one validation "
    "sorbent excluded), predicts b_i; fold error sqrt(e0^2 + misfit^2), e0 = error from other sources in units of SD(b); "
    "beat if r >= 0.10 (within-fold test assumed passed, as in the pre-d replicate). Not the real learner.")
# 5. population-level shape in the current null factor: median over a of exp(a(x-1/2) - sa^2 (x-1/2)^2/2)
sa = 0.6
res["median_factor_current_null"] = {str(x): float(np.exp(-sa ** 2 * (x - 0.5) ** 2 / 2)) for x in (0, 0.5, 1, 1.5, 2, 2.5, 3)}
res["world_C_factor_for_comparison"] = {str(x): float(np.exp(-0.7 * x)) for x in (0, 0.5, 1, 1.5, 2)}
# 6. metric asymmetry: E-optimal common log-rate shift c* when the truth's log factor u ~ N(0, s^2) is symmetric
t = np.linspace(0, 1, 401)
def seg_E(u, c, L):
    tt = t * L
    return np.sqrt(np.mean((np.exp(-np.exp(c) * tt) - np.exp(-np.exp(u) * tt)) ** 2))
uq = norm.ppf((np.arange(200) + 0.5) / 200)
def cstar(s, L):
    f = lambda c: np.median([seg_E(s * z, c, L) for z in uq])
    return float(minimize_scalar(f, bounds=(-1, 1), method="bounded", options={"xatol": 1e-5}).x)
res["metric_asymmetry_cstar"] = {f"L{L}": {f"s{s}": cstar(s, L) for s in (0.1, 0.3, 0.6, 0.9)} for L in (3, 10)}
res["metric_asymmetry_note"] = ("first-order approach, segment length L time constants, E = RMS of fraction error; c* "
    "minimises the median over the population of E. c* != 0 means that a symmetric log factor still has an E-optimal "
    "shift; a constant shift is absorbed by the metric-fitted k'', a shift that varies with x is learnable shape.")
json.dump(res, open(os.path.join(OUT, "null_dependence.json"), "w"), indent=1)
print("ok")
