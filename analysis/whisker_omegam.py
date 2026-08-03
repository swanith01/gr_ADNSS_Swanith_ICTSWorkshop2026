from getdist import loadMCSamples
import matplotlib.pyplot as plt
import numpy as np

base = '/home/swanith/Desktop/cosmo_smoketests/cluster_runs'

# --- Load your chains ---
mp_desi = loadMCSamples(f'{base}/montepython/2026-07-31_lcdm_desi_only/2026-07-31_50000_')
mp_desy5 = loadMCSamples(f'{base}/montepython/2026-07-31_lcdm_desy5_only/2026-07-31_50000_')
mp_combined = loadMCSamples(f'{base}/montepython/2026-07-31_lcdm_desi_desy5/2026-07-31_50000_')

cobaya_desi = loadMCSamples(f'{base}/cobaya/2026-07-31_lcdm_desi_only/lcdm_desi_only')
cobaya_desy5 = loadMCSamples(f'{base}/cobaya/2026-07-31_lcdm_desy5_only/lcdm_desy5_only')
cobaya_combined = loadMCSamples(f'{base}/cobaya/2026-07-31_lcdm_desi_desy5/lcdm_desi_desy5')

def mean_std(samples, param):
    stats = samples.getMargeStats()
    p = stats.parWithName(param)
    return p.mean, p.err

# --- Extract Omega_m mean +/- 1sigma ---
mp_vals = {
    'DESI': mean_std(mp_desi, 'Omega_m'),
    'DES Y5': mean_std(mp_desy5, 'Omega_m'),
    'DESI+DES Y5': mean_std(mp_combined, 'Omega_m'),
}
cobaya_vals = {
    'DESI': mean_std(cobaya_desi, 'Omega_m'),
    'DES Y5': mean_std(cobaya_desy5, 'Omega_m'),
    'DESI+DES Y5': mean_std(cobaya_combined, 'Omega_m'),
}

# --- Paper's values (Table II, Bayesian, LCDM Omega_m) ---
# Note: paper does not run DES Y5 alone
paper_vals = {
    'DESI': (0.298, 0.009),
    'DESI+DES Y5': (0.311, 0.008),
}

datasets = ['DESI', 'DES Y5', 'DESI+DES Y5']
y_positions = {d: i for i, d in enumerate(datasets)}

fig, ax = plt.subplots(figsize=(7, 4))

offset = 0.15
for d in datasets:
    y = y_positions[d]
    # MontePython
    m, e = mp_vals[d]
    ax.errorbar(m, y + offset, xerr=e, fmt='o', color='crimson', capsize=4,
                label='MontePython' if y == 0 else None)
    # Cobaya
    m, e = cobaya_vals[d]
    ax.errorbar(m, y, xerr=e, fmt='s', color='royalblue', capsize=4,
                label='Cobaya' if y == 0 else None)
    # Paper, if available
    if d in paper_vals:
        m, e = paper_vals[d]
        ax.errorbar(m, y - offset, xerr=e, fmt='^', color='black', capsize=4,
                    label='Herold & Karwal 2026 (Bayesian)' if y == 0 else None)
    else:
        ax.text(ax.get_xlim()[1] if ax.get_xlim()[1] else 0.4, y - offset,
                '  (not run in paper)', fontsize=8, color='gray', va='center')

ax.set_yticks(list(y_positions.values()))
ax.set_yticklabels(datasets)
ax.set_xlabel(r'$\Omega_m$ ($\Lambda$CDM)')
ax.set_title('Our runs vs Herold & Karwal (2506.12004): $\\Omega_m$ ($\\Lambda$CDM)')
ax.legend(loc='best', fontsize=8)
ax.invert_yaxis()
plt.tight_layout()
plt.savefig('/home/swanith/Desktop/cosmo_smoketests/analysis/figures/whisker_omegam_vs_paper.png', dpi=150)
print("Saved whisker plot")

# Print numeric summary too
print("\n--- Summary ---")
for d in datasets:
    print(f"{d}:")
    print(f"  MontePython: {mp_vals[d][0]:.4f} +/- {mp_vals[d][1]:.4f}")
    print(f"  Cobaya:      {cobaya_vals[d][0]:.4f} +/- {cobaya_vals[d][1]:.4f}")
    if d in paper_vals:
        print(f"  Paper:       {paper_vals[d][0]:.4f} +/- {paper_vals[d][1]:.4f}")
