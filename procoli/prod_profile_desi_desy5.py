from procoli import lkl_prof

profile = lkl_prof(
  chains_dir='/user/p8_group/gr_ADNSS/Swanith/runs/montepython/2026-07-31_lcdm_desi_desy5/',
  prof_param='Omega_m',
  info_root='2026-07-31_lcdm_desi_desy5',
)

profile.prof_max = 0.40
profile.prof_min = 0.20
profile.processes = 4
profile.prof_incr = 0.01

profile.set_global_jump_fac([1, 0.8, 0.5, 0.2, 0.1, 0.05])
profile.set_global_temp([0.333, 0.25, 0.2, 0.1, 0.005, 0.001])
profile.global_min(N_min_steps=1000)

print("Global minimum: ")
print(profile.global_ML)

profile.init_lkl_prof()
profile.set_jump_fac([0.15, 0.1, 0.05])
profile.set_temp([0.1, 0.005, 0.001])
profile.run_lkl_prof(time_mins=True, N_min_steps=1000)

# Negative direction
profile.prof_incr = -0.01
profile.global_min(N_min_steps=1000)
profile.init_lkl_prof()
profile.run_lkl_prof(time_mins=True, N_min_steps=1000)
