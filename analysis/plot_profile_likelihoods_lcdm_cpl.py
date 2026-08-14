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
    'CMB only': '*lcdm_cmb_only*_lkl_profile.txt',
}
colors = {'DESI + DES Y5': 'royalblue', 'DES Y5 only': 'crimson', 'DESI only': 'seagreen', 'CMB only': 'darkorange'}
# maps a nice label to the file pattern for each dataset

colors = {'DESI + DES Y5': 'royalblue', 'DES Y5 only': 'crimson', 'DESI only': 'seagreen', 'CMB only': 'darkorange'}

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

# --- CPL profile likelihoods from Prospect ---
cpl_profile_paths = {
    'DESI (CPL)': '/home/swanith/Desktop/cosmo_smoketests/cluster_runs/prospect/2026-08-10_cpl_desi_only_omegam_Om/profile/Omega_m.txt',
    'DES Y5 (CPL)': '/home/swanith/Desktop/cosmo_smoketests/cluster_runs/prospect/2026-08-10_cpl_desy5_only_omegam_Om/profile/Omega_m.txt',
    'CMB (CPL)': '/home/swanith/Desktop/cosmo_smoketests/cluster_runs/runs/prospect/2026-08-11_cpl_cmb_only_omegam_Om/profile/Omega_m.txt',
}

cpl_profile_colors = {
    'DESI (CPL)': colors['DESI only'],
    'DES Y5 (CPL)': colors['DES Y5 only'],
    'CMB (CPL)': colors['CMB only'],
}

for label, path_cpl in cpl_profile_paths.items():
    data_cpl = np.genfromtxt(path_cpl, skip_header=1)
    om_cpl = data_cpl[:, 0]
    dchi2_cpl = data_cpl[:, 1]

    ax1.plot(
        om_cpl,
        dchi2_cpl,
        '--',
        color=cpl_profile_colors[label],
        linewidth=2,
        label=f'{label}: Prospect'
    )

ax1.axhline(1, color='gray', linestyle='--', linewidth=0.8, label=r'$\Delta\chi^2=1$ (1$\sigma$)')
ax1.axhline(4, color='gray', linestyle=':', linewidth=0.8, label=r'$\Delta\chi^2=4$ (2$\sigma$)')
ax1.set_xlabel(r'$\Omega_m$')
ax1.set_ylabel(r'$\Delta\chi^2$')
ax1.set_ylim(0, 12)
ax1.set_title(r'Profile likelihoods: Procoli ($\Lambda$CDM) vs Prospect (CPL)')
ax1.legend(fontsize=8)
plt.tight_layout()
plt.savefig('/home/swanith/Desktop/cosmo_smoketests/analysis/figures/profile_likelihoods.png', dpi=150)
print("\nSaved profile_likelihoods.png")

from getdist import loadMCSamples

cpl_base = '/home/swanith/Desktop/cosmo_smoketests/cluster_runs/cobaya_cpl'
cpl_desi_chain = loadMCSamples(f'{cpl_base}/2026-08-05_cpl_desi_only/cpl_desi_only')
cpl_desy5_chain = loadMCSamples(f'{cpl_base}/2026-08-05_cpl_desy5_only/cpl_desy5_only')
cpl_cmb_chain = loadMCSamples('/home/swanith/Desktop/cosmo_smoketests/cluster_runs/runs/cobaya/2026-08-11_cpl_cmb_only_omegam_bootstrapped/cpl_cmb_only_omegam')

def get_stat(samples, param):
    stats = samples.getMargeStats()
    p = stats.parWithName(param)
    return p.mean, p.err

cpl_bayesian = {
    'DESI (CPL)': get_stat(cpl_desi_chain, 'Omega_m'),
    'DES Y5 (CPL)': get_stat(cpl_desy5_chain, 'Omega_m'),
    'CMB (CPL)': get_stat(cpl_cmb_chain, 'Omega_m'),
}
print("CPL Bayesian loaded successfully.")

def load_prospect_profile(path):
    data = np.genfromtxt(path, skip_header=1)
    om = data[:, 0]
    dchi2 = data[:, 1]
    order = np.argsort(om)
    return om[order], dchi2[order]

prospect_base = '/home/swanith/Desktop/cosmo_smoketests/cluster_runs/prospect'
cpl_procoli_vals = {}
for label, key in [('DESI (CPL)', 'desi_only'), ('DES Y5 (CPL)', 'desy5_only')]:
    om, nl = load_prospect_profile(f'{prospect_base}/2026-08-10_cpl_{key}_omegam_Om/profile/Omega_m.txt')
    min_om, dchi2, bounds = get_bounds(om, nl)
    cpl_procoli_vals[label] = (min_om, bounds)
    print(f"CPL Frequentist {label}: {min_om:.4f}")

om_cmb_cpl, nl_cmb_cpl = load_prospect_profile('/home/swanith/Desktop/cosmo_smoketests/cluster_runs/runs/prospect/2026-08-11_cpl_cmb_only_omegam_Om/profile/Omega_m.txt')
min_om_cmb_cpl, dchi2_cmb_cpl, bounds_cmb_cpl = get_bounds(om_cmb_cpl, nl_cmb_cpl)
cpl_procoli_vals['CMB (CPL)'] = (min_om_cmb_cpl, bounds_cmb_cpl)
cmb_cpl_om_range = (om_cmb_cpl.min(), om_cmb_cpl.max())
print(f"CPL Frequentist CMB (CPL): best-fit={min_om_cmb_cpl:.4f}, 1sigma={bounds_cmb_cpl['1sigma']}")

cpl_paper_vals = {'DESI (CPL)': (0.382, 0.046)}

# ============================================================
# ============================================================
# PLOT 2: Whisker comparison
# ============================================================

# --- Bayesian: MontePython (LCDM) ---
mp_bayesian = {
    'DESI only': (0.2979, 0.0086),
    'DES Y5 only': (0.3307, 0.0151),
    'DESI + DES Y5': (0.3062, 0.0076),
    'CMB only': (0.3215, 0.0060),
}

# --- Bayesian: Cobaya (LCDM) ---
cobaya_bayesian = {
    'DESI only': (0.2979, 0.0083),
    'DES Y5 only': (0.3310, 0.0152),
    'DESI + DES Y5': (0.3061, 0.0074),
    'CMB only': (0.3215, 0.0060),
}

# --- Paper: Herold & Karwal 2026, Bayesian ---
paper_vals = {
    'DESI only': (0.298, 0.009),
    'DESI + DES Y5': (0.311, 0.008),
    'CMB only': (0.315, 0.007),
}

# --- Paper: Herold & Karwal 2026, Frequentist ---
paper_freq_vals = {
    'DESI only': (0.297, 0.009),
    'DESI + DES Y5': (0.310, 0.008),
}

# --- CPL: Cobaya Bayesian ---
# Already loaded above as cpl_bayesian

# --- CPL: Prospect Frequentist ---
# Already loaded above as cpl_procoli_vals

# --- CPL: Herold & Karwal 2026 ---
cpl_paper_vals = {
    'DESI (CPL)': (0.382, 0.046),
}


# ------------------------------------------------------------
# Dataset ordering
# ------------------------------------------------------------

order = [
    'DESI only',
    'DESI (CPL)',
    'CMB only',
    'CMB (CPL)',
    'DES Y5 only',
    'DES Y5 (CPL)',
    'DESI + DES Y5'
]

y_pos = {d: i for i, d in enumerate(order)}


# ------------------------------------------------------------
# Vertical offsets
# ------------------------------------------------------------

offsets = {
    # LCDM
    'mp': 0.30,
    'cobaya': 0.15,
    'procoli': 0.00,
    'paper': -0.15,
    'paper_freq': -0.30,

    # CPL
    'cpl_bayes': 0.18,
    'cpl_freq': 0.06,
    'cpl_paper': -0.06,
}


# ------------------------------------------------------------
# Figure
# ------------------------------------------------------------

fig2, ax2 = plt.subplots(figsize=(11, 5))

seen_labels = set()


# ============================================================
# Plot each dataset
# ============================================================

for d in order:

    y = y_pos[d]

    # --------------------------------------------------------
    # LCDM Bayesian: MontePython
    # ONLY plot if this is an LCDM dataset
    # --------------------------------------------------------

    if d in mp_bayesian:

        m, e = mp_bayesian[d]

        lbl = (
            'MontePython (Bayesian)'
            if 'mp' not in seen_labels else None
        )

        seen_labels.add('mp')

        ax2.errorbar(
            m,
            y + offsets['mp'],
            xerr=e,
            fmt='o',
            color='crimson',
            capsize=4,
            label=lbl
        )


    # --------------------------------------------------------
    # LCDM Bayesian: Cobaya
    # ONLY plot if this is an LCDM dataset
    # --------------------------------------------------------

    if d in cobaya_bayesian:

        m, e = cobaya_bayesian[d]

        lbl = (
            'Cobaya (Bayesian)'
            if 'cobaya' not in seen_labels else None
        )

        seen_labels.add('cobaya')

        ax2.errorbar(
            m,
            y + offsets['cobaya'],
            xerr=e,
            fmt='s',
            color='royalblue',
            capsize=4,
            label=lbl
        )


    # --------------------------------------------------------
    # LCDM Frequentist: Procoli
    #
    # IMPORTANT:
    # This condition deliberately excludes ALL CPL rows.
    # Therefore the old orange filled diamonds cannot appear
    # on DESI (CPL) or DES Y5 (CPL).
    # --------------------------------------------------------

    if (
        d in procoli_vals
        and d in [
            'DESI only',
            'CMB only',
            'DES Y5 only',
            'DESI + DES Y5'
        ]
    ):

        min_om, bounds = procoli_vals[d]

        lower, upper = bounds['1sigma']

        if lower is not None and upper is not None:

            err = [
                [min_om - lower],
                [upper - min_om]
            ]

            lbl = (
                'Procoli (Frequentist)'
                if 'procoli' not in seen_labels else None
            )

            seen_labels.add('procoli')

            ax2.errorbar(
                min_om,
                y + offsets['procoli'],
                xerr=err,
                fmt='D',
                color='darkorange',
                capsize=4,
                label=lbl
            )


    # --------------------------------------------------------
    # LCDM paper Bayesian
    # --------------------------------------------------------

    if d in paper_vals:

        m, e = paper_vals[d]

        if d == 'CMB only':
            lbl = (
                'Planck 2018 (cited in H&K 2026)'
                if 'planck' not in seen_labels else None
            )
            seen_labels.add('planck')

        else:
            lbl = (
                'Herold & Karwal 2026 (Bayesian)'
                if 'paper' not in seen_labels else None
            )
            seen_labels.add('paper')

        ax2.errorbar(
            m,
            y + offsets['paper'],
            xerr=e,
            fmt='^',
            mfc='white' if d != 'CMB only' else 'black',
            color='black',
            capsize=4,
            label=lbl
        )


    # --------------------------------------------------------
    # LCDM paper Frequentist
    # --------------------------------------------------------

    if d in paper_freq_vals:

        m, e = paper_freq_vals[d]

        lbl = (
            'Herold & Karwal 2026 (Frequentist)'
            if 'paper_freq' not in seen_labels else None
        )

        seen_labels.add('paper_freq')

        ax2.errorbar(
            m,
            y + offsets['paper_freq'],
            xerr=e,
            fmt='v',
            color='gray',
            capsize=4,
            label=lbl
        )


    # ========================================================
    # CPL Bayesian: Cobaya
    # ========================================================

    if d in cpl_bayesian:

        m, e = cpl_bayesian[d]

        lbl = (
            'CPL: Cobaya (Bayesian)'
            if 'cpl_bayes' not in seen_labels else None
        )

        seen_labels.add('cpl_bayes')

        ax2.errorbar(
            m,
            y + offsets['cpl_bayes'],
            xerr=e,
            fmt='s',
            mfc='white',
            mec='royalblue',
            color='royalblue',
            capsize=4,
            label=lbl
        )


    # ========================================================
    # CPL Frequentist: Prospect
    #
    # 1 sigma = EMPTY orange diamond + SOLID whisker
    # 2 sigma = DASHED whisker
    #
    # Crucially, this is completely independent of
    # procoli_vals.
    # ========================================================

    if d in cpl_procoli_vals:

        min_om, bounds = cpl_procoli_vals[d]

        y_cpl = y + offsets['cpl_freq']


        # ----------------------------------------------------
        # 1 sigma
        # ----------------------------------------------------

        lower1, upper1 = bounds['1sigma']

        if lower1 is not None and upper1 is not None:

            err1 = [
                [min_om - lower1],
                [upper1 - min_om]
            ]

            lbl = (
                'Prospect (Frequentist, CPL)'
                if 'cpl_freq' not in seen_labels else None
            )

            seen_labels.add('cpl_freq')

            ax2.errorbar(
                min_om,
                y_cpl,
                xerr=err1,
                fmt='D',
                mfc='white',
                mec='darkorange',
                ecolor='darkorange',
                color='darkorange',
                capsize=4,
                linestyle='-',
                label=lbl,
                zorder=4
            )


        # ----------------------------------------------------
        # 2 sigma -- explicitly dashed
        #
        # Recompute the crossings directly from the actual
        # CPL Prospect profile rather than using the stored
        # bounds.  This avoids the incorrect CPL 2-sigma
        # whisker.
        # ----------------------------------------------------

        # Load the actual CPL profile for this dataset
        if d == 'DESI (CPL)':
            profile_path = (
                f'{prospect_base}/2026-08-10_cpl_desi_only_omegam_Om/'
                f'profile/Omega_m.txt'
            )
        else:
            profile_path = (
                f'{prospect_base}/2026-08-10_cpl_desy5_only_omegam_Om/'
                f'profile/Omega_m.txt'
            )

        profile_data = np.genfromtxt(
            profile_path,
            skip_header=1
        )

        om_prof = profile_data[:, 0]
        dchi2_prof = profile_data[:, 1]

        # Sort by Omega_m
        sort_idx = np.argsort(om_prof)
        om_prof = om_prof[sort_idx]
        dchi2_prof = dchi2_prof[sort_idx]

        # Find the minimum
        i_min = np.argmin(dchi2_prof)
        om_best = om_prof[i_min]

        # Find crossings of Delta chi2 = 4
        target = 4.0

        lower2 = None
        upper2 = None

        # Left-hand crossing
        for i in range(i_min - 1, -1, -1):
            if dchi2_prof[i] >= target and dchi2_prof[i + 1] < target:
                lower2 = np.interp(
                    target,
                    [dchi2_prof[i], dchi2_prof[i + 1]],
                    [om_prof[i], om_prof[i + 1]]
                )
                break

        # Right-hand crossing
        for i in range(i_min, len(om_prof) - 1):
            if dchi2_prof[i] < target and dchi2_prof[i + 1] >= target:
                upper2 = np.interp(
                    target,
                    [dchi2_prof[i], dchi2_prof[i + 1]],
                    [om_prof[i], om_prof[i + 1]]
                )
                break

        if lower2 is not None and upper2 is not None:

            cap_height = 0.035

            # Dashed horizontal 2-sigma interval
            ax2.plot(
                [lower2, upper2],
                [y_cpl, y_cpl],
                linestyle='--',
                color='darkorange',
                linewidth=1.5,
                zorder=2
            )

            # Left dashed cap
            ax2.plot(
                [lower2, lower2],
                [y_cpl - cap_height, y_cpl + cap_height],
                linestyle='--',
                color='darkorange',
                linewidth=1.5,
                zorder=2
            )

            # Right dashed cap
            ax2.plot(
                [upper2, upper2],
                [y_cpl - cap_height, y_cpl + cap_height],
                linestyle='--',
                color='darkorange',
                linewidth=1.5,
                zorder=2
            )

    # ========================================================
    # CPL paper
    # ========================================================

    if d in cpl_paper_vals:

        m, e = cpl_paper_vals[d]

        lbl = (
            'CPL: Herold & Karwal 2026'
            if 'cpl_paper' not in seen_labels else None
        )

        seen_labels.add('cpl_paper')

        ax2.errorbar(
            m,
            y + offsets['cpl_paper'],
            xerr=e,
            fmt='^',
            mfc='white',
            mec='black',
            color='black',
            capsize=4,
            label=lbl
        )


# ============================================================
# ============================================================
# CMB (CPL): Prospect never crosses Delta_chi2=1 anywhere on the
# scanned grid (max Delta_chi2 ~3e-3 over Omega_m in [0.20, 0.45]),
# so there is no meaningful 1/2-sigma interval -- show the scanned
# range as an unconstrained band instead, and flag the Bayesian
# chain as not formally converged (R-1 ~ 3.2-3.6).
# ============================================================

if 'CMB (CPL)' in y_pos:
    y_cmb_cpl = y_pos['CMB (CPL)'] + offsets['cpl_freq']
    lo, hi = cmb_cpl_om_range

    lbl = 'Prospect (Frequentist, CPL): unconstrained'
    ax2.plot([lo, hi], [y_cmb_cpl, y_cmb_cpl], linestyle='--',
             color='darkorange', linewidth=2, alpha=0.6, label=lbl, zorder=2)
    for x in (lo, hi):
        ax2.plot([x, x], [y_cmb_cpl - 0.035, y_cmb_cpl + 0.035],
                 linestyle='--', color='darkorange', linewidth=1.5, alpha=0.6, zorder=2)

    ax2.text(hi + 0.01, y_pos['CMB (CPL)'],
             'CPL: R-1~3.2-3.6 (not converged);\nfreq. flat, unconstrained',
             fontsize=7, color='gray', va='center')

# Formatting
# ============================================================

ax2.set_yticks(list(y_pos.values()))
ax2.set_yticklabels(order)

ax2.set_xlabel(r'$\Omega_m$ ($\Lambda$CDM)')

ax2.set_title(
    r'$\Lambda$CDM: Procoli vs Bayesian  |  CPL: Prospect vs Bayesian'
)

ax2.invert_yaxis()

ax2.legend(
    loc='upper left',
    bbox_to_anchor=(1.02, 1.0),
    fontsize=8,
    borderaxespad=0
)

plt.tight_layout(rect=[0, 0, 0.78, 1])

plt.savefig(
    '/home/swanith/Desktop/cosmo_smoketests/analysis/figures/whisker_full_comparison.png',
    dpi=150,
    bbox_inches='tight'
)

print("Saved whisker_full_comparison.png")
