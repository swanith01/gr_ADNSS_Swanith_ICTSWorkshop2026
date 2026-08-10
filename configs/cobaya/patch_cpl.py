import re

theory_old = """theory:
  classy:
    stop_at_error: True
    extra_args:
      N_ncdm: 1 # one non cdm species
      deg_ncdm: 3 # 3 dof for one neutrino species
      m_ncdm: 0.02 # Mass of each neutrino species
      N_ur: 0.00441 # Number of Ultra-Relativistic species"""

theory_new = """theory:
  classy:
    stop_at_error: True
    extra_args:
      N_ncdm: 1 # one non cdm species
      deg_ncdm: 3 # 3 dof for one neutrino species
      m_ncdm: 0.02 # Mass of each neutrino species
      N_ur: 0.00441 # Number of Ultra-Relativistic species
      Omega_Lambda: 0
      use_ppf: True
      a_ini_over_a_today_default: 1.e-16"""

de_old = "  # start Dynamical DE params \n  # find which params classy accepts? \n  # We will put priors on w0 and w0+wa but we want to sample w0 and wa \n  # Use drop: True and value: to implement this below\n\n  # w0_fld:\n  #   latex: w_0\n  # w0wa:\n  #   latex: w_0+w_a\n  # wa_fld:\n  #   latex: w_a\n  # end Dynamical DE params "

de_new = """  w0_fld:
    prior:
      min: -3
      max: 1
    ref:
      dist: norm
      loc: -1.0
      scale: 0.1
    proposal: 0.1
    latex: w_0
    drop: true
  w0wa:
    prior:
      min: -5
      max: 0
    ref:
      dist: norm
      loc: 0.0
      scale: 0.3
    proposal: 0.3
    latex: w_0+w_a
    drop: true
  wa_fld:
    value: 'lambda w0_fld, w0wa: w0wa - w0_fld'
    latex: w_a"""

def patch(src_path, dst_path, output_dir, output_prefix):
    with open(src_path) as f:
        content = f.read()
    if theory_old not in content:
        print(f"THEORY BLOCK NOT FOUND in {src_path}")
        return
    if de_old not in content:
        print(f"DE BLOCK NOT FOUND in {src_path}")
        return
    content = content.replace(theory_old, theory_new)
    content = content.replace(de_old, de_new)
    content = re.sub(r"output: .*", f"output: /user/p8_group/gr_ADNSS/Swanith/runs/cobaya/{output_dir}/{output_prefix}", content)
    with open(dst_path, "w") as f:
        f.write(content)
    print(f"Wrote {dst_path}")

patch("lcdm_desi_only.yaml", "cpl_desi_only.yaml", "2026-08-05_cpl_desi_only", "cpl_desi_only")
patch("lcdm_desy5_only.yaml", "cpl_desy5_only.yaml", "2026-08-05_cpl_desy5_only", "cpl_desy5_only")
