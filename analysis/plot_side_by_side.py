from getdist import loadMCSamples
import getdist.plots as gdplt
from PIL import Image

# --- MontePython chain ---
mp_root = '/home/swanith/Desktop/cosmo_smoketests/montepython_runs/mp_smoketest_local/2026-07-30_100_'
mp_samples = loadMCSamples(mp_root)

g1 = gdplt.get_subplot_plotter()
g1.triangle_plot(mp_samples, ['H0', 'omega_b', 'omega_cdm'], filled=True)
g1.export('/home/swanith/Desktop/cosmo_smoketests/analysis/mp_triangle.png')

# --- Cobaya chain ---
cobaya_root = '/home/swanith/Desktop/cosmo_smoketests/cobaya_runs/smoketest_local/smoketest'
cobaya_samples = loadMCSamples(cobaya_root)

g2 = gdplt.get_subplot_plotter()
g2.triangle_plot(cobaya_samples, ['a', 'b'], filled=True)
g2.export('/home/swanith/Desktop/cosmo_smoketests/analysis/cobaya_triangle.png')

# --- Combine side by side using PIL ---
img1 = Image.open('/home/swanith/Desktop/cosmo_smoketests/analysis/mp_triangle.png')
img2 = Image.open('/home/swanith/Desktop/cosmo_smoketests/analysis/cobaya_triangle.png')

# Match heights, place side by side
h = max(img1.height, img2.height)
img1 = img1.resize((int(img1.width * h / img1.height), h))
img2 = img2.resize((int(img2.width * h / img2.height), h))

combined = Image.new('RGB', (img1.width + img2.width, h), 'white')
combined.paste(img1, (0, 0))
combined.paste(img2, (img1.width, 0))
combined.save('/home/swanith/Desktop/cosmo_smoketests/analysis/side_by_side.png')

print("Saved: mp_triangle.png, cobaya_triangle.png, side_by_side.png")
