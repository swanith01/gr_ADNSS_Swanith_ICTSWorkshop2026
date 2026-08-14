import numpy as np
import sys

def build_covmat(chain_prefix, param_names, out_path, burn_frac=0.15):
    all_rows = []
    with open(f"{chain_prefix}.1.txt") as f:
        header = f.readline().lstrip("#").split()
    col_idx = {name: i for i, name in enumerate(header)}

    for i in range(1, 5):
        fname = f"{chain_prefix}.{i}.txt"
        try:
            data = np.loadtxt(fname)
        except OSError:
            continue
        if data.ndim == 1:
            data = data[None, :]
        n_burn = int(len(data) * burn_frac)
        all_rows.append(data[n_burn:])

    data = np.vstack(all_rows)
    weights = data[:, col_idx["weight"]]
    values = np.column_stack([data[:, col_idx[p]] for p in param_names])

    mean = np.average(values, axis=0, weights=weights)
    diff = values - mean
    cov = (diff.T * weights) @ diff / weights.sum()

    with open(out_path, "w") as f:
        f.write("# " + " ".join(param_names) + "\n")
        for row in cov:
            f.write(" ".join(f"{v:.8e}" for v in row) + "\n")

    print(f"Wrote {out_path}")
    print("N_eff samples used:", weights.sum(), "| N_rows used:", len(values))
    print("Mean:", dict(zip(param_names, mean)))
    print("Correlation matrix:")
    std = np.sqrt(np.diag(cov))
    corr = cov / np.outer(std, std)
    with np.printoptions(precision=2, suppress=True):
        print(corr)

if __name__ == "__main__":
    chain_prefix, out_path = sys.argv[1], sys.argv[2]
    param_names = sys.argv[3:]
    build_covmat(chain_prefix, param_names, out_path)
