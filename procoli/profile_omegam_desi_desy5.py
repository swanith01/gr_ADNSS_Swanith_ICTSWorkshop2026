from procoli import lkl_prof
# lkl_prof is Procoli's main class -- create an instance of it to profile a parameter

profile = lkl_prof(
  chains_dir='/user/p8_group/gr_ADNSS/Swanith/runs/montepython/2026-07-31_lcdm_desi_desy5/',
  prof_param='Omega_m',
  info_root='2026-07-31_lcdm_desi_desy5',
)
# points to the chain to start from, and which parameter to scan (Omega_m for LCDM)

profile.prof_max = 0.35
profile.prof_min = 0.25
profile.processes = 2
profile.prof_incr = 0.01
# range of Omega_m to scan over (smoketest window), 2 parallel workers, grid step size 0.01

# --- Schedule for the GLOBAL best-fit search ---
# Finds the single overall minimum chi^2 point across ALL parameters
# (Omega_m is free here too, not fixed). This becomes the reference
# point that every profile point below gets compared against.
profile.set_global_jump_fac([1, 0.8, 0.5, 0.2, 0.1, 0.05])
profile.set_global_temp([0.333, 0.25, 0.2, 0.1, 0.005, 0.001])
# step size factor and temperature ladder, hot to cold

profile.global_min(N_min_steps=50)
# 6 temp stages x 50 steps each = 300 steps total; small for smoketest

print("Global minimum: ")
print(profile.global_ML)

profile.init_lkl_prof()
# sets up the profile likelihood scan using the global best-fit as starting point

# --- Schedule for the PER-POINT profile search ---
# At each fixed Omega_m grid point (0.25, 0.26, ..., 0.35), only the
# OTHER parameters are re-minimized via simulated annealing, starting
# near the global best-fit found above. This gives one best chi^2 per
# fixed Omega_m -- the resulting chi^2-vs-Omega_m curve IS the profile
# likelihood (Delta chi^2 = 1 from the minimum gives the 1-sigma interval).
profile.set_jump_fac([0.15, 0.1, 0.05])
profile.set_temp([0.1, 0.005, 0.001])

profile.run_lkl_prof(
  time_mins=True,
  N_min_steps=50
)
