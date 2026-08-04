# gr_ADNSS — Swanith

Reproducing Herold & Karwal (2026), *"Bayesian and frequentist perspectives
agree on dynamical dark energy"* (arXiv:2506.12004), for the ICTS 2026
cosmology summer school.

**Scope of this sub-repo:** ΛCDM standalone-dataset reproduction (DESI DR2
BAO, DES Y5 SNe, Planck-compressed CMB, and their combination), using both
MontePython and Cobaya, cross-validated Bayesian (MCMC) vs. Frequentist
(profile likelihoods via Procoli). w0waCDM (CPL) standalone runs were
attempted as a follow-up exploration; see "Known issues" below.

## Repo structure

```
configs/{montepython,cobaya}/   input files only, never touched by runs
runs/{montepython,cobaya}/      output only, named <date>_<dataset>_<model>
pbs/                             PBS job scripts + logs
procoli/                         Procoli profile-likelihood scripts
analysis/                        GetDist / matplotlib plotting scripts + figures
```

Configs and outputs are kept in separate folders on purpose — early on we
lost a `.param` file to an over-eager `rm -rf` on its output directory.

## Results — ΛCDM, Ω_m

| Dataset | Bayesian (MontePython) | Bayesian (Cobaya) | Frequentist (Procoli) | Paper / literature |
|---|---|---|---|---|
| DESI DR2 BAO only | 0.2979 ± 0.0086 | 0.2979 ± 0.0083 | 0.2973, [0.290, 0.305] (1σ) | 0.298 ± 0.009 |
| CMB only (Planck-compressed) | 0.3215 ± 0.0060 | — | 0.3214 ± 0.0035 | 0.315 ± 0.007 (Planck 2018, literature) |
| DES Y5 SN only | 0.3307 ± 0.0151 | 0.3310 ± 0.0152 | 0.3304, [0.316, 0.345] (1σ) | not run standalone in paper |
| DESI + DES Y5 | 0.3062 ± 0.0076 | 0.3061 ± 0.0074 | 0.3060, [0.300, 0.312] (1σ) | 0.311 ± 0.008 |

Bayesian and frequentist estimates agree closely for every dataset — the
same qualitative conclusion the paper itself draws for the full 7-dataset
comparison, reproduced here on a smaller scale.

Figures in `analysis/figures/`:
- `mp_dataset_breakdown.png` / `cobaya_dataset_breakdown.png` — per-tool
  dataset comparison (BAO/SN/combined), each in its own native
  parametrization.
- `mp_vs_cobaya.png` — cross-tool comparison on the combined dataset.
- `profile_likelihoods.png` — Δχ² profile curves (Procoli), all 4 datasets.
- `whisker_full_comparison.png` — full Bayesian × Frequentist × paper
  comparison.

## Bugs found and fixed (ΛCDM)

1. **BBN prior edge**: original template priors on `omega_b` were far wider
   than the BBN interpolation table CLASS uses for the helium abundance.
   Fixed to `omega_b ∈ [0.01, 0.03]`.
2. **Neutrino/`h` coupling**: `Omega_ncdm = omega_ncdm / h²` — an
   unphysically wide `h` prior (`[0.2, 1.4]`) let the sampler propose an
   `h` too small to support the fixed neutrino mass budget. Fixed to
   `h ∈ [0.4, 1.0]`.
3. **PBS memory**: `mem=4gb` was too tight once multiple Cobaya jobs shared
   a node; bumped to `mem=16gb`.
4. **`$PATH`**: PBS batch jobs don't inherit interactive-shell `$PATH`
   additions; `MontePython.py` must be added to `$PATH` explicitly inside
   the job script for Procoli's internal subprocess calls to find it.
5. **Procoli `IndexError`**: `mp_procoli_functions.py`'s
   `update_neg_log_likelhood_chains` assumes a chain file has ≥2 rows;
   crashes on a 1-row file (numpy 2.x collapses single-row `loadtxt`
   output to 1D). Triggered at low `N_min_steps`; rare at production scale
   but not impossible.
6. **Stale output folders**: Procoli caches `global_min/`, `chi2_per_exp/`,
   and `*_lkl_profile.txt` between runs; editing a `.param` file's priors
   without clearing these first causes `GlobalMLDifferenceError` or silent
   use of stale, inconsistent state. Always clear before rerunning after a
   config change.

## w0waCDM (CPL) — attempted, not completed

Standalone-dataset CPL runs (DESI, DES Y5, CMB, each alone) were attempted
as a follow-up curiosity exercise. Root cause of persistent low MCMC
acceptance and Procoli minimizer failures, finally identified:

**We used independent box priors on `w0_fld` and `wa_fld`
(`w0 ∈ [-3,1]`, `wa ∈ [-3,2]`), but the paper uses a *joint* prior:
`w0 ∈ [-3,1]` AND `w0+wa ∈ [-5,0]`.** Independent boxes allow
`w0+wa > 1/3`, a region where CLASS cannot define a physical
radiation-dominated early universe
(`background_checks: w(a→0) >= 1/3`). The sampler kept wandering into
this dead zone, tanking acceptance and starving Procoli's minimizer of a
valid starting point.

A partial fix (a hard-veto custom MontePython likelihood,
`montepython/likelihoods/w0wa_joint_prior/`, rejecting any point with
`w0+wa > 0`) was built but not fully smoketested before stopping for the
day.

**Two proper fixes for next time, not yet implemented:**
- **Cobaya**: sample `w0_fld` and `w0wa` (≡ `w0+wa`) directly, each with
  its own simple box prior; derive `wa_fld` via `drop: true` +
  `value: 'lambda w0_fld, w0wa: w0wa - w0_fld'`. Structurally excludes the
  unphysical region — no rejection needed.
- **Frequentist**: Procoli only interfaces with MontePython, so the Cobaya
  reparametrization above can't feed it directly. **PROSPECT**
  (Holm et al. 2024, arXiv:2312.02972, `pip install prospect-public`,
  requires Python ≥3.10) is a newer profile-likelihood tool compatible
  with *both* Cobaya and MontePython — worth investigating as a
  Procoli alternative for the CPL case specifically. Not yet installed
  or tested here.

Also unresolved: `w0_fld`/`wa_fld` do not use MontePython's usual
per-parameter `scale` column consistently with the `.bestfit` file's
header-comment ordering when appended after `derived` parameter
declarations in a `.param` file — the header comment and the actual data
columns can desync (data itself was verified correct via the
`H0 = 100·h` self-consistency check; only the header labeling was wrong).
Worth reordering `w0_fld`/`wa_fld` declarations to sit with the other
`'cosmo'` parameters, before any `'derived'` declarations, in any future
`.param` file that adds them after the fact.

## Reproducing this work

See `GITHUB_SETUP.md` for how to set up your own GitHub-backed working
copy of this workflow. Priors, PBS resource conventions, and stopping
criteria used across the group are summarized in the shared tracking
spreadsheet (`gr_ADNSS_tracking_matrix.xlsx`, distributed separately).
