# gr_ADNSS — Swanith's notes
## Reproducing Herold & Karwal (2506.12004) — DESI DR2 dynamical dark energy

## Setup

- Local (laptop): MontePython + Cobaya installed in separate conda envs
  (`montepython_env`, `cobaya_env`), tested with toy likelihoods
  (`test_gaussian`, `gaussian_mixture`) to learn the tools before touching
  real data.
- Cluster (`pawna`): tutors provided `pantheon.param` (MontePython, ΛCDM,
  DESI DR2 BAO + DES Y5 SNe) and `cobaya_smoketest.yaml` (Cobaya, full
  CMB+DESI+DES Y5, w0wa block left as an exercise).

## Directory structure (`~/gr_ADNSS/Swanith/`)

Lesson learned: keep configs and outputs in separate folders. Early on we
`rm -f`'d an output folder that also contained the `.param` file sitting
inside it — lost the file. Never again.

## ΛCDM smoketests — dataset breakdown

Goal: understand what each dataset (DESI DR2 BAO, DES Y5 SNe) constrains
individually, before combining, matching the paper's Table II structure.

Configs (all fixing neutrino settings: m_ncdm=0.02 eV x deg_ncdm=3,
matching paper's degenerate-mass approximation):
- `lcdm_desi_desy5.{param,yaml}` — combined
- `lcdm_desi_only.{param,yaml}` — DESI DR2 BAO only
- `lcdm_desy5_only.{param,yaml}` — DES Y5 SNe only

## Bugs found and fixed

### 1. omega_b prior too close to BBN table edges
CLASS derives YHe (helium fraction) from a BBN interpolation table that
only covers a finite omega_b range. Original template priors
(`omega_b: [0.001, 0.2]` in Cobaya yaml, `[0.005, 10.]` scaled in
MontePython param) were far too wide — real BBN table edges are roughly
`omega_b ~ [0.01, 0.03]`.

Symptom: `CosmoComputationError` /
`condition (omega_b < omegab[0]) is true` or
`condition (omega_b > omegab[num_omegab-1]) is true`

Fix: tightened to `omega_b in [0.01, 0.03]` in all configs.

Why DESI-only / combined didn't hit it immediately: BAO data strongly
constrains omega_b, keeping the chain away from the edges early on.
DES-Y5-only (SN alone) has essentially no constraining power on omega_b,
so the chain wandered into the danger zone almost immediately. This
turned into a genuine physics lesson: SN alone can't constrain the sound
horizon / baryon density at all (only measures *relative* distances).

### 2. Omega_m floor too low given fixed neutrino mass
Physical minimum: Omega_ncdm*h^2 ~ Sum(m_nu)/93.14 eV. With
Sum(m_nu)=0.06 eV fixed, Omega_ncdm*h^2 ~ 6.4e-4. If Omega_m's sampled
value drops below what's needed to "fit" this neutrino density (plus
baryons/CDM), CLASS can't build a consistent cosmology.

Symptom: `condition (Omega_m_remaining < pba->Omega0_ncdm_tot) is true`

Fix: raised Omega_m floor to 0.1 (well above the bare neutrino/baryon
floor) in all MontePython configs.

### 3. h range too wide, indirectly breaking the neutrino budget
Even after fixing Omega_m's floor, DES-Y5-only still crashed with the
same "not enough room for neutrinos" error — but now with a much smaller
remaining budget than expected. Root cause: `Omega_ncdm = omega_ncdm/h^2`.
Original `h` prior was `[0.2, 1.4]` (i.e. H0 in [20, 140] km/s/Mpc) —
wildly unphysical. Small h inflates Omega_ncdm even though the physical
neutrino mass never changed.

Fix: tightened h to [0.4, 1.0] (H0 in [40, 100]) across all configs.

### Takeaway
A "reasonable-looking" wide prior in a template isn't automatically safe
— it needs to be checked against what the theory code can actually
compute, not just against what looks statistically permissive. Different
datasets expose different edges of the same underlying prior volume
depending on how well they constrain each parameter.

## Job management (PBS)
- Cluster has 4 nodes (pawna), 192 cores each.
- Requesting ppn=32 per job means 6 jobs exactly fill one node — checked
  with `pbsnodes -aSj` to confirm we weren't starving other groups (3
  nodes remained free/lightly used).
- Interactive smoketests via `qsub -I` for fast iteration; batch `qsub`
  for real scaled-up runs (survives SSH/wifi disconnects).

## Status log
- [DATE/TIME] mp_lcdm, mp_desi: succeeded first try (50000 steps each)
- [DATE/TIME] cobaya_lcdm, cobaya_desi, cobaya_desy5, mp_desy5: crashed
  (bugs #1-3 above), fixed, resubmitted
