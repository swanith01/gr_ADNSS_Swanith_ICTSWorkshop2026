from getdist import loadMCSamples
import getdist.plots as gdplt
import matplotlib.pyplot as plt
import numpy as np
import glob

base = '/home/swanith/Desktop/cosmo_smoketests/cluster_runs'

def get_stat(samples, param):
    stats = samples.getMargeStats()
    p = stats.parWithName(param)
    return p.mean, p.err

def load_profile(files):
    om_all, nl_all, nl_col = [], [], None
    for f in files:
        data = np.genfromtxt(f, skip_header=1)
        if data.ndim == 1:
            data = data.reshape(1, -1)
        # LCDM profile files: col1=Omega_m, col8=-logLike (10 cols total incl BAO/SN breakdown)
        # CPL PROSPECT files: col0=Omega_m, col2=-loglkl (9 cols)
        if data.shape[1] >= 9 and data.shape[1] <= 10 and 'lkl_profile' in f:
            om_all.extend(data[:, 1]); nl_all.extend(data[:, 8])
        else:
            om_all.extend(data[:, 0]); nl_all.extend(data[:, 2])
    om_all = np.array(om_all); nl_all = np.array(nl_all)
    om_u, idx = np.unique(om_all, return_index=True)
    nl_u = nl_all[idx]
    order = np.argsort(om_u)
    return om_u[order], nl_u[order]

def get_bounds(om, nl):
    minLogL = nl.min()
    min_om = om[np.argmin(nl)]
    dchi2 = 2 * (nl - minLogL)
    left = om <= min_om
    right = om >= min_om
    lower = upper = None
    if left.sum() >= 2 and dchi2[left].max() >= 1.0:
        lower = np.interp(1.0, dchi2[left][::-1], om[left][::-1])
    if right.sum() >= 2 and dchi2[right].max() >= 1.0:
        upper = np.interp(1.0, dchi2[right], om[right])
    return min_om, lower, upper, dchi2

# =========================================================
# LOAD CHAINS
# =========================================================
mp_base = f'{base}/montepython_desi_desy5_permutations'
cb_base = f'{base}/cobaya_desi_desy5_permutations'
cpl_base = f'{base}/cobaya_cpl'

mp_desi = loadMCSamples(f'{mp_base}/2026-07-31_lcdm_desi_only/2026-07-31_50000_')
mp_desy5 = loadMCSamples(f'{mp_base}/2026-07-31_lcdm_desy5_only/2026-07-31_50000_')
mp_combined = loadMCSamples(f'{mp_base}/2026-07-31_lcdm_desi_desy5/2026-07-31_50000_')
mp_cmb = loadMCSamples(f'{mp_base}/2026-08-03_lcdm_cmb_only/2026-08-03_50000_')

cb_desi = loadMCSamples(f'{cb_base}/2026-07-31_lcdm_desi_only/lcdm_desi_only')
cb_desy5 = loadMCSamples(f'{cb_base}/2026-07-31_lcdm_desy5_only/lcdm_desy5_only')
cb_combined = loadMCSamples(f'{cb_base}/2026-07-31_lcdm_desi_desy5/lcdm_desi_desy5')

cpl_desi = loadMCSamples(f'{cpl_base}/2026-08-05_cpl_desi_only/cpl_desi_only')
cpl_desy5 = loadMCSamples(f'{cpl_base}/2026-08-05_cpl_desy5_only/cpl_desy5_only')
cpl_cmb = loadMCSamples(f'{base}/runs/cobaya/2026-08-11_cpl_cmb_only_omegam_bootstrapped/cpl_cmb_only_omegam')

for c, l in [(mp_desi,'DESI'),(mp_desy5,'DES Y5'),(mp_combined,'DESI+DES Y5'),(mp_cmb,'CMB'),
             (cb_desi,'DESI'),(cb_desy5,'DES Y5'),(cb_combined,'DESI+DES Y5'),
             (cpl_desi,'DESI (CPL)'),(cpl_desy5,'DES Y5 (CPL)'),(cpl_cmb,'CMB (CPL)')]:
    c.label = l

# =========================================================
# BAYESIAN Omega_m MEANS
# =========================================================
mp_lcdm_bayes = {d: get_stat(c, 'Omega_m') for d, c in
                  [('DESI', mp_desi), ('DES Y5', mp_desy5), ('DESI + DES Y5', mp_combined), ('CMB', mp_cmb)]}
cb_lcdm_bayes = {d: get_stat(c, 'Omega_m') for d, c in
                  [('DESI', cb_desi), ('DES Y5', cb_desy5), ('DESI + DES Y5', cb_combined)]}
cb_cpl_bayes = {d: get_stat(c, 'Omega_m') for d, c in
                  [('DESI', cpl_desi), ('DES Y5', cpl_desy5), ('CMB', cpl_cmb)]}

print("=== Bayesian Omega_m ===")
for tag, d in [('MP LCDM', mp_lcdm_bayes), ('Cobaya LCDM', cb_lcdm_bayes), ('Cobaya CPL', cb_cpl_bayes)]:
    for k, (m, e) in d.items():
        print(f"  {tag} {k}: {m:.4f} +/- {e:.4f}")

# =========================================================
# FREQUENTIST Omega_m: LCDM (Procoli) + CPL (PROSPECT)
# =========================================================
lcdm_patterns = {'DESI': 'lcdm_desi_only', 'DES Y5': 'lcdm_desy5_only',
                  'CMB': 'lcdm_cmb_only', 'DESI + DES Y5': 'lcdm_desi_desy5'}
lcdm_freq = {}
for label, key in lcdm_patterns.items():
    files = sorted(glob.glob(f'{base}/procoli/*{key}*_lkl_profile.txt'))
    om, nl = load_profile(files)
    lcdm_freq[label] = get_bounds(om, nl) + (om, nl)

cpl_patterns = {'DESI': 'desi_only', 'DES Y5': 'desy5_only'}
cpl_freq = {}
for label, key in cpl_patterns.items():
    f = f'{base}/prospect/2026-08-10_cpl_{key}_omegam_Om/profile/Omega_m.txt'
    om, nl = load_profile([f])
    cpl_freq[label] = get_bounds(om, nl) + (om, nl)

print("\n=== Frequentist Omega_m ===")
for tag, d in [('LCDM Procoli', lcdm_freq), ('CPL PROSPECT', cpl_freq)]:
    for k, v in d.items():
        print(f"  {tag} {k}: best-fit={v[0]:.4f}, lower={v[1]}, upper={v[2]}")

paper_lcdm = {'DESI': (0.298, 0.009), 'DESI + DES Y5': (0.311, 0.008), 'CMB': (0.315, 0.007)}

# =========================================================
# PLOT 1: Combined whisker, LCDM + CPL, all methods
# =========================================================
order = ['DESI', 'CMB', 'DES Y5', 'DESI + DES Y5']
y_pos = {d: i for i, d in enumerate(order)}
fig1, ax1 = plt.subplots(figsize=(9, 6))
seen = set()

for d in order:
    y = y_pos[d]
    # LCDM: MP Bayesian, Cobaya Bayesian, Procoli Frequentist, Paper
    if d in mp_lcdm_bayes:
        m, e = mp_lcdm_bayes[d]
        lbl = 'LCDM: MontePython (Bayesian)' if 'mp_l' not in seen else None
        ax1.errorbar(m, y + 0.35, xerr=e, fmt='o', color='crimson', capsize=3, label=lbl, markersize=5)
        seen.add('mp_l')
    if d in cb_lcdm_bayes:
        m, e = cb_lcdm_bayes[d]
        lbl = 'LCDM: Cobaya (Bayesian)' if 'cb_l' not in seen else None
        ax1.errorbar(m, y + 0.22, xerr=e, fmt='s', color='royalblue', capsize=3, label=lbl, markersize=5)
        seen.add('cb_l')
    if d in lcdm_freq:
        min_om, lower, upper = lcdm_freq[d][0], lcdm_freq[d][1], lcdm_freq[d][2]
        if lower is not None and upper is not None:
            err = [[min_om - lower], [upper - min_om]]
            lbl = 'LCDM: Frequentist' if 'f_l' not in seen else None
            ax1.errorbar(min_om, y + 0.09, xerr=err, fmt='D', color='darkorange', capsize=3, label=lbl, markersize=5)
            seen.add('f_l')
    if d in paper_lcdm:
        m, e = paper_lcdm[d]
        lbl = 'LCDM: Paper/Planck' if 'p_l' not in seen else None
        ax1.errorbar(m, y - 0.04, xerr=e, fmt='^', color='black', capsize=3, label=lbl, markersize=5)
        seen.add('p_l')

    # CPL: Cobaya Bayesian, PROSPECT Frequentist (open markers)
    if d in cb_cpl_bayes:
        m, e = cb_cpl_bayes[d]
        lbl = 'CPL: Cobaya (Bayesian)' if 'cb_c' not in seen else None
        ax1.errorbar(m, y - 0.20, xerr=e, fmt='s', mfc='white', color='royalblue', capsize=3, label=lbl, markersize=5)
        seen.add('cb_c')
    if d in cpl_freq:
        min_om, lower, upper = cpl_freq[d][0], cpl_freq[d][1], cpl_freq[d][2]
        if lower is not None and upper is not None:
            err = [[min_om - lower], [upper - min_om]]
            lbl = 'CPL: Frequentist' if 'f_c' not in seen else None
            ax1.errorbar(min_om, y - 0.33, xerr=err, fmt='D', mfc='white', color='darkorange', capsize=3, label=lbl, markersize=5)
            seen.add('f_c')
    if d == 'CMB':
        ax1.text(0.55, y - 0.27,
                 'CPL: R-1~3.2-3.6 (not converged);\n'
                 'freq. Delta_chi2 flat, Omega_m unconstrained',
                 fontsize=7, color='gray', va='center')

ax1.set_yticks(list(y_pos.values()))
ax1.set_yticklabels(order)
ax1.set_xlabel(r'$\Omega_m$')
ax1.set_title(r'$\Omega_m$: $\Lambda$CDM (filled) vs $w_0w_a$CDM/CPL (open) -- all methods')
ax1.legend(fontsize=7, ncol=2, loc='upper right')
ax1.invert_yaxis()
plt.tight_layout()
plt.savefig('figures/whisker_lcdm_and_cpl.png', dpi=150)
print("\nSaved whisker_lcdm_and_cpl.png")

# =========================================================
# PLOT 2: Profile likelihoods, LCDM (left) + CPL (right)
# =========================================================
fig2, (axL, axC) = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
colorsL = {'DESI': 'seagreen', 'DES Y5': 'crimson', 'CMB': 'darkorange', 'DESI + DES Y5': 'royalblue'}
for label, v in lcdm_freq.items():
    om, nl = v[3], v[4]
    dchi2 = 2 * (nl - nl.min())
    axL.plot(om, dchi2, 'o-', color=colorsL[label], label=label, markersize=4)
axL.axhline(1, color='gray', linestyle='--', linewidth=0.8)
axL.set_xlabel(r'$\Omega_m$'); axL.set_ylabel(r'$\Delta\chi^2$')
axL.set_xlim(0.2, 0.45); axL.set_ylim(0, 12)
axL.set_title(r'$\Lambda$CDM'); axL.legend(fontsize=8)

colorsC = {'DESI': 'seagreen', 'DES Y5': 'crimson', 'CMB': 'darkorange'}
for label, v in cpl_freq.items():
    om, nl = v[3], v[4]
    dchi2 = 2 * (nl - nl.min())
    axC.plot(om, dchi2, 'o-', color=colorsC[label], label=label, markersize=4)
axC.axhline(1, color='gray', linestyle='--', linewidth=0.8)
axC.set_xlabel(r'$\Omega_m$')
axC.set_xlim(0.15, 0.6); axC.set_ylim(0, 12)
axC.set_title(r'$w_0w_a$CDM (CPL) -- CMB shown, unconstrained (see text)'); axC.legend(fontsize=8)

fig2.suptitle('Profile likelihoods (frequentist): $\\Lambda$CDM vs CPL', y=1.02)
plt.tight_layout()
plt.savefig('figures/profile_likelihoods_lcdm_and_cpl.png', dpi=150)
print("Saved profile_likelihoods_lcdm_and_cpl.png")

# =========================================================
# PLOT 3: LCDM corner plot, all 4 datasets
# =========================================================
g1 = gdplt.get_subplot_plotter()
g1.triangle_plot([mp_cmb, mp_desi, mp_desy5, mp_combined], ['Omega_m', 'h', 'omega_b'],
                  filled=True, legend_labels=['CMB', 'DESI', 'DES Y5', 'DESI + DES Y5'])
g1.fig.suptitle('$\\Lambda$CDM posteriors, all datasets (MontePython)', fontsize=13, y=1.01)
g1.export('figures/corner_lcdm_all.png')
print("Saved corner_lcdm_all.png")

# =========================================================
# PLOT 4: CPL corner plot, DESI + DES Y5
# =========================================================
g2 = gdplt.get_subplot_plotter()
g2.triangle_plot([cpl_desi, cpl_desy5, cpl_cmb], ['Omega_m', 'H0', 'w0_fld', 'wa_fld'],
                  filled=True, legend_labels=['DESI', 'DES Y5', 'CMB (R-1~3.2-3.6, not converged)'])
g2.fig.suptitle('$w_0w_a$CDM (CPL) posteriors -- DESI, DES Y5, CMB', fontsize=12, y=1.01)
g2.export('figures/corner_cpl_all.png')
print("Saved corner_cpl_all.png")

print("\nAll done.")
