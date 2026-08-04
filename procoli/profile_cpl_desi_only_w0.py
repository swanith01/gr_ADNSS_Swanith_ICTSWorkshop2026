from procoli import lkl_prof

profile = lkl_prof(
  chains_dir='/user/p8_group/gr_ADNSS/Swanith/runs/montepython/2026-08-03_cpl_desi_only/',
  prof_param='w0_fld',
  info_root='2026-08-03_cpl_desi_only',
)

profile.prof_max = 1.0
profile.prof_min = -3.0
profile.processes = 4
profile.prof_incr = 0.1

profile.set_global_jump_fac([1, 0.8, 0.5, 0.2, 0.1, 0.05])
profile.set_global_temp([0.333, 0.25, 0.2, 0.1, 0.005, 0.001])
profile.global_min(N_min_steps=8000)

print("Global minimum: ")
print(profile.global_ML)

profile.init_lkl_prof()
profile.set_jump_fac([0.15, 0.1, 0.05])
profile.set_temp([0.1, 0.005, 0.001])
profile.run_lkl_prof(time_mins=True, N_min_steps=8000)

profile.prof_incr = -0.1
profile.global_min(N_min_steps=8000)
profile.init_lkl_prof()
profile.run_lkl_prof(time_mins=True, N_min_steps=8000)
