import numpy as np
import matplotlib.pyplot as plt
import glob
import os

base = '/home/swanith/Desktop/cosmo_smoketests/cluster_runs/procoli'

def load_profile(pattern):
    """Load and merge +Omega_m and -Omega_m profile files matching pattern."""
    files = sorted(glob.glob(os.path.join(base, pattern))) #find all the files with a particular patterns
    om_all, nl_all = [], [] #Initialise Omega_m and its -loge_likelihood
    for f in files: #loop over all matched files 
        data = np.genfromtxt(f, skip_header=1) # if file only has one data row numpy automatically returns a 1D array; similarly a (1 row, 12 columns) becme a (12 rows, 1 column), so fix that.
        if data.ndim == 1:
            data = data.reshape(1, -1)
        om_all.extend(data[:, 1])   # Omega_m column in the procoli output file
        nl_all.extend(data[:, 8])   # -logLike column
    om_all = np.array(om_all) #convert to numpy array
    nl_all = np.array(nl_all)
    # dedupe (best-fit point appears in both + and - files)
    om_unique, idx = np.unique(om_all, return_index=True)
    nl_unique = nl_all[idx] # remove any duplictes and index them appropriately
    order = np.argsort(om_unique) #increasing omega_m
    return om_unique[order], nl_unique[order]

def get_bounds(omega_m, negLogL):
    minLogL = negLogL.min() # best fit
    min_om = omega_m[np.argmin(negLogL)] # Omega_m at best fit
    dchi2 = 2 * (negLogL - minLogL) # Chi^2 of all other points relative to the chi^2 minima

    left_mask = omega_m <= min_om 
    right_mask = omega_m >= min_om # separate data in to above and below the best fit Omega_m, cause some likelihoods are one sided

    bounds = {}
    for sigma, target in [('1sigma', 1.0), ('2sigma', 4.0)]: # 1sigma and 2sigma
        lower = upper = None
        if left_mask.sum() >= 2: # need atleast 2 points on the left to draw a line and interpolate. so any 1sigma or 2sigma crossing has some interpolated point
            om_l = omega_m[left_mask][::-1]
            dc_l = dchi2[left_mask][::-1]
            if dc_l.max() >= target: #only trust this if the scan assigned the dchi^2 to it properly
                lower = np.interp(target, dc_l, om_l)
        if right_mask.sum() >= 2:
            om_r = omega_m[right_mask]
            dc_r = dchi2[right_mask]
            if dc_r.max() >= target:
                upper = np.interp(target, dc_r, om_r)
        bounds[sigma] = (lower, upper)  # if a side never reached the target dchi2, that bound just stays None
    # -- this is exactly how we catch DESI-only's missing lower bound
    return min_om, dchi2, bounds
# ============================================================
# PLOT 1: Profile likelihood (dchi2 vs Omega_m) curves -- Procoli only
# Bayesian chains (MontePython/Cobaya) don't have a dchi2 curve,
# only Procoli's frequentist minimization produces this.
# ============================================================

datasets = {
    'DESI + DES Y5': '*lcdm_desi_desy5*_lkl_profile.txt',
    'DES Y5 only': '*lcdm_desy5_only*_lkl_profile.txt',
    'DESI only': '*lcdm_desi_only*_lkl_profile.txt',
}
# maps a nice label to the file pattern for each dataset

colors = {'DESI + DES Y5': 'royalblue', 'DES Y5 only': 'crimson', 'DESI only': 'seagreen'}

fig1, ax1 = plt.subplots(figsize=(7, 5))

procoli_vals = {}  # save results here to reuse in the whisker plot below

for label, pattern in datasets.items():
    om, nl = load_profile(pattern)
    if len(om) < 2:
        print(f"Skipping {label}: not enough points ({len(om)})")
        continue
    min_om, dchi2, bounds = get_bounds(om, nl)
    procoli_vals[label] = (min_om, bounds)

    # plot the actual dchi2 vs Omega_m curve for this dataset
    ax1.plot(om, dchi2, 'o-', color=colors[label], label=label, markersize=4)

    print(f"\n{label}:")
    print(f"  Best-fit Omega_m = {min_om:.4f}")
    print(f"  1-sigma (dchi2=1): lower={bounds['1sigma'][0]}, upper={bounds['1sigma'][1]}")
    print(f"  2-sigma (dchi2=4): lower={bounds['2sigma'][0]}, upper={bounds['2sigma'][1]}")

ax1.axhline(1, color='gray', linestyle='--', linewidth=0.8, label=r'$\Delta\chi^2=1$ (1$\sigma$)')
ax1.axhline(4, color='gray', linestyle=':', linewidth=0.8, label=r'$\Delta\chi^2=4$ (2$\sigma$)')
ax1.set_xlabel(r'$\Omega_m$')
ax1.set_ylabel(r'$\Delta\chi^2$')
ax1.set_ylim(0, 12)
ax1.set_title('Profile likelihoods (frequentist, Procoli), $\\Lambda$CDM')
ax1.legend(fontsize=8)
plt.tight_layout()
plt.savefig('/home/swanith/Desktop/cosmo_smoketests/analysis/figures/profile_likelihoods.png', dpi=150)
print("\nSaved profile_likelihoods.png")

# ============================================================
# PLOT 2: Whisker comparison -- MontePython (Bayesian) vs
# Cobaya (Bayesian) vs Procoli (Frequentist) vs Paper
# ============================================================

# --- Bayesian: MontePython (from your MCMC chains, mean +/- std) ---
mp_bayesian = {
    'DESI only': (0.2979, 0.0086),
    'DES Y5 only': (0.3307, 0.0151),
    'DESI + DES Y5': (0.3062, 0.0076),
}

# --- Bayesian: Cobaya (from your MCMC chains, mean +/- std) ---
cobaya_bayesian = {
    'DESI only': (0.2979, 0.0083),
    'DES Y5 only': (0.3310, 0.0152),
    'DESI + DES Y5': (0.3061, 0.0074),
}

# --- Paper (Herold & Karwal 2026, Table II, Bayesian) ---
paper_vals = {
    'DESI only': (0.298, 0.009),
    'DESI + DES Y5': (0.311, 0.008),
}

order = ['DESI only', 'DES Y5 only', 'DESI + DES Y5']
y_pos = {d: i for i, d in enumerate(order)}
offsets = {'mp': 0.24, 'cobaya': 0.08, 'procoli': -0.08, 'paper': -0.24}

fig2, ax2 = plt.subplots(figsize=(8, 5))

for d in order:
    y = y_pos[d]

    m, e = mp_bayesian[d]
    ax2.errorbar(m, y + offsets['mp'], xerr=e, fmt='o', color='crimson', capsize=4,
                 label='MontePython (Bayesian)' if y == 0 else None)

    m, e = cobaya_bayesian[d]
    ax2.errorbar(m, y + offsets['cobaya'], xerr=e, fmt='s', color='royalblue', capsize=4,
                 label='Cobaya (Bayesian)' if y == 0 else None)

    min_om, bounds = procoli_vals[d]
    lower, upper = bounds['1sigma']
    if lower is not None and upper is not None:
        err = [[min_om - lower], [upper - min_om]]
        ax2.errorbar(min_om, y + offsets['procoli'], xerr=err, fmt='D', color='darkorange',
                      capsize=4, label='Procoli (Frequentist)' if y == 0 else None)
    elif upper is not None:
        ax2.errorbar(min_om, y + offsets['procoli'], xerr=[[0], [upper - min_om]], fmt='D',
                      color='darkorange', capsize=4,
                      label='Procoli (Frequentist, one-sided)' if y == 0 else None)

    if d in paper_vals:
        m, e = paper_vals[d]
        ax2.errorbar(m, y + offsets['paper'], xerr=e, fmt='^', color='black', capsize=4,
                      label='Herold & Karwal 2026 (Bayesian)' if y == 0 else None)
    else:
        ax2.text(0.355, y + offsets['paper'], '(not run in paper)', fontsize=8,
                 color='gray', va='center')

ax2.set_yticks(list(y_pos.values()))
ax2.set_yticklabels(order)
ax2.set_xlabel(r'$\Omega_m$ ($\Lambda$CDM)')
ax2.set_title('Bayesian (MontePython & Cobaya) vs Frequentist (Procoli) vs Paper')
ax2.legend(loc='best', fontsize=8)
ax2.invert_yaxis()
plt.tight_layout()
plt.savefig('/home/swanith/Desktop/cosmo_smoketests/analysis/figures/whisker_full_comparison.png', dpi=150)
print("Saved whisker_full_comparison.png")
