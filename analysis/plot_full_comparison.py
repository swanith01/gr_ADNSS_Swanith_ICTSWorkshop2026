from getdist import loadMCSamples
import getdist.plots as gdplt
import matplotlib.pyplot as plt

base = '/home/swanith/Desktop/cosmo_smoketests/cluster_runs'

#MontePython dataset breakdown
mp_desi = loadMCSamples(f'{base}/montepython/2026-07-31_lcdm_desi_only/2026-07-31_50000_')
mp_desy5 = loadMCSamples(f'{base}/montepython/2026-07-31_lcdm_desy5_only/2026-07-31_50000_')
mp_combined = loadMCSamples(f'{base}/montepython/2026-07-31_lcdm_desi_desy5/2026-07-31_50000_')

mp_desi.label = 'MP: DESI only'
mp_desy5.label = 'MP: DES Y5 only'
mp_combined.label = 'MP: DESI + DES Y5'

g1 = gdplt.get_subplot_plotter()
g1.triangle_plot([mp_desi, mp_desy5, mp_combined], ['omega_b', 'Omega_m', 'h'],
                  filled=True, legend_labels=['DESI only', 'DES Y5 only', 'Combined'])
g1.fig.suptitle('MontePython: ΛCDM, dataset breakdown (DESI vs DES Y5 vs Combined)', y=1.02, fontsize=11)
g1.export('/home/swanith/Desktop/cosmo_smoketests/analysis/figures/mp_dataset_breakdown.png')
print("Saved dataset breakdown plot")

# MontePython vs Cobaya, same dataset (combined)
cobaya_combined = loadMCSamples(f'{base}/cobaya/2026-07-31_lcdm_desi_desy5/lcdm_desi_desy5')
cobaya_combined.label = 'Cobaya'
mp_combined.label = 'MontePython'

g2 = gdplt.get_subplot_plotter()
g2.triangle_plot([mp_combined, cobaya_combined], ['Omega_m', 'H0'],
                  filled=True, legend_labels=['MontePython', 'Cobaya'])
g2.fig.suptitle('MontePython vs Cobaya: ΛCDM, DESI + DES Y5 combined', y=1.02, fontsize=11)
g2.export('/home/swanith/Desktop/cosmo_smoketests/analysis/figures/mp_vs_cobaya.png')
print("Saved MP vs Cobaya comparison plot")

cobaya_desi = loadMCSamples(f'{base}/cobaya/2026-07-31_lcdm_desi_only/lcdm_desi_only')
cobaya_desy5 = loadMCSamples(f'{base}/cobaya/2026-07-31_lcdm_desy5_only/lcdm_desy5_only')

cobaya_desi.label = 'Cobaya: DESI only'
cobaya_desy5.label = 'Cobaya: DES Y5 only'
cobaya_combined.label = 'Cobaya: DESI + DES Y5'

g3 = gdplt.get_subplot_plotter()
g3.triangle_plot([cobaya_desi, cobaya_desy5, cobaya_combined], ['omega_b', 'omega_cdm', 'H0'],
                  filled=True, legend_labels=['DESI only', 'DES Y5 only', 'Combined'])
g3.fig.suptitle('Cobaya: ΛCDM, dataset breakdown (DESI vs DES Y5 vs Combined)', y=1.02, fontsize=11)
g3.export('/home/swanith/Desktop/cosmo_smoketests/analysis/figures/cobaya_dataset_breakdown.png')
print("Saved Cobaya dataset breakdown plot")
