import re

old = """  omega_cdm:
    prior:
      min: 0.003
      max: 0.9
    ref:
      dist: norm
      loc: 0.12
      scale: 0.001
    proposal: 0.0013
    latex: \\Omega_\\mathrm{c} h^2"""

new = """  Omega_m:
    prior:
      min: 0.1
      max: 0.6
    ref:
      dist: norm
      loc: 0.31
      scale: 0.01
    proposal: 0.01
    latex: \\Omega_\\mathrm{m}
    drop: true
  omega_cdm:
    value: 'lambda Omega_m, H0, omega_b: Omega_m*(H0/100.)**2 - omega_b - 6.4422e-4'
    latex: \\Omega_\\mathrm{c} h^2"""

def patch(src, dst, output_dir, output_prefix):
    with open(src) as f:
        content = f.read()
    if old not in content:
        print(f"PATTERN NOT FOUND in {src}")
        return
    content = content.replace(old, new)
    # remove the OLD standalone "Omega_m:\n    latex: ..." derived-only block, since we now define Omega_m above as sampled
    old_derived = "  Omega_m:\n    latex: \\Omega_\\mathrm{m}\n"
    if old_derived in content:
        content = content.replace(old_derived, "", 1)
    else:
        print(f"  (note: old derived Omega_m block not found/removed in {src}, check manually)")
    content = re.sub(r"output: .*", f"output: /user/p8_group/gr_ADNSS/Swanith/runs/cobaya/{output_dir}/{output_prefix}", content)
    with open(dst, "w") as f:
        f.write(content)
    print(f"Wrote {dst}")

patch("cpl_desi_only.yaml", "cpl_desi_only_omegam.yaml", "2026-08-10_cpl_desi_only_omegam", "cpl_desi_only_omegam")
patch("cpl_desy5_only.yaml", "cpl_desy5_only_omegam.yaml", "2026-08-10_cpl_desy5_only_omegam", "cpl_desy5_only_omegam")
patch("cpl_cmb_only.yaml", "cpl_cmb_only_omegam.yaml", "2026-08-10_cpl_cmb_only_omegam", "cpl_cmb_only_omegam")
