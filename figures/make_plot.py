"""Plot detector macro-F1 from Vykopal et al. (2024), Table 6 (p. 8). Reads only the CSV next to this file."""
import csv, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
rows = [r for r in csv.DictReader(l for l in open(os.path.join(HERE, "vykopal2024_table6_detectors.csv"), encoding="utf-8") if not l.startswith("#"))]
matplotlib.rcParams.update({"pdf.fonttype": 42, "font.family": "DejaVu Sans"})
COL = {"ELECTRA-large (MULTITuDE)": "#1f5f8b", "Other detectors": "#9aa5b1"}

def draw(path, width_in, height_in, fs, label_fs, short=False):
    fig, ax = plt.subplots(figsize=(width_in, height_in))
    def name(r):
        d = r["detector"].replace("-Max-1.3B", "-1.3B").replace("RoBERTa-large OpenAI", "RoBERTa-L OpenAI") if short else r["detector"]
        return (f"ELECTRA [{d}]" if short else f"ELECTRA-large [{d}]") if r["group"].startswith("ELECTRA") else d
    names = [name(r) for r in rows][::-1]
    vals = [float(r["macro_f1"]) for r in rows][::-1]
    cols = [COL[r["group"]] for r in rows][::-1]
    bars = ax.barh(names, vals, color=cols, height=0.7)
    for b, v in zip(bars, vals):
        ax.text(v + 0.01, b.get_y() + b.get_height() / 2, f"{v:.2f}", va="center", fontsize=label_fs)
    ax.set_xlim(0, 1.0)
    ax.set_xlabel("Macro-F1" if short else "Macro-F1 (Vykopal et al., 2024, Table 6)", fontsize=fs)
    ax.tick_params(labelsize=fs)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in COL.values()]
    if not short:  # poster: colours are explained in the poster caption instead of a legend
        ax.legend(handles, ["ELECTRA-large fine-tuned on MULTITuDE [training generator]", "Other detectors"],
                  fontsize=label_fs, loc="lower center", bbox_to_anchor=(0.35, 1.0), ncol=2, frameon=False)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    print("wrote", path)

# Paper: 0.95 textwidth ~ 6.2 in, fonts 9 pt at 100 % scale.
draw(os.path.join(HERE, "fig_detectors_paper.pdf"), 6.2, 3.6, 9, 8)
