"""
main.py
Entry point eksperimen: menjalankan ketiga algoritma, mencetak
hasil ke terminal, menyimpan data eksperimen ke results.json,
dan menghasilkan grafik visualisasi PNG.
Output:
    - Terminal: ringkasan perbandingan & urutan setlist
    - results.json: data eksperimen lengkap
    - kurva_energi_plot.png
    - perbandingan_waktu_plot.png
    - konvergensi_aco_plot.png
"""

import json
import random
import time
import os

import matplotlib.pyplot as plt

from dataset         import SONGS, KEY_NAMES, N, W1, W2, LAMBDA, ADJ
from dijkstra        import dijkstra_nearest_neighbor
from branch_and_bound import branch_and_bound
from modified_aco    import modified_aco


def _energy_stats(path):
    energies = [SONGS[i]["energy"] for i in path]
    drops    = sum(1 for k in range(1, len(energies)) if energies[k] < energies[k-1])
    return energies, drops


def generate_charts(dijkstra_res, bb_res, aco_res):
    """Menghasilkan 3 grafik PNG dari data hasil eksperimen."""
    print("\n  Generating charts...")

    # 1. Kurva Energi Perbandingan
    plt.figure(figsize=(9, 4.5))
    x = list(range(1, 16))
    plt.plot(x, dijkstra_res['energies'], marker='o', color='#ef4444',
             label=f'Dijkstra NN ({dijkstra_res["drops"]} drops)', linewidth=2)
    plt.plot(x, bb_res['energies'], marker='s', color='#22c55e',
             label=f'Branch and Bound ({bb_res["drops"]} drops)', linewidth=2)
    plt.plot(x, aco_res['energies'], marker='^', color='#0284c7',
             label=f'Modified ACO ({aco_res["drops"]} drops)', linewidth=2)
    plt.title('Perbandingan Kurva Transisi Energi Setlist', fontsize=12, fontweight='bold', pad=15)
    plt.xlabel('Urutan Repertoar (Lagu Ke-1 s.d. 15)', fontsize=10)
    plt.ylabel('Tingkat Energi Lagu (Skala 1-10)', fontsize=10)
    plt.xticks(x)
    plt.yticks(range(1, 11))
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(loc='lower right')
    plt.tight_layout()
    os.makedirs('plots', exist_ok=True)
    plt.savefig('plots/kurva_energi_plot.png', dpi=300)
    plt.close()
    print("    -> plots/kurva_energi_plot.png")

    # 2. Perbandingan Waktu Eksekusi (Log Scale)
    plt.figure(figsize=(6, 4))
    algos = ['Dijkstra NN', 'Modified ACO', 'Branch & Bound']
    times = [dijkstra_res['time_ms'], aco_res['time_ms'], bb_res['time_ms']]
    colors_list = ['#ef4444', '#0284c7', '#22c55e']
    plt.bar(algos, times, color=colors_list, width=0.45)
    plt.yscale('log')
    plt.title('Perbandingan Waktu Eksekusi Algoritma (Log Scale)', fontsize=11, fontweight='bold', pad=12)
    plt.ylabel('Waktu Eksekusi (ms)', fontsize=9)
    for i, t in enumerate(times):
        plt.text(i, t * 1.2, f"{t:.4f} ms" if t < 1 else f"{t:,.2f} ms",
                 ha='center', fontsize=9, fontweight='bold')
    plt.grid(True, which="both", linestyle='--', alpha=0.3)
    plt.tight_layout()
    plt.savefig('plots/perbandingan_waktu_plot.png', dpi=300)
    plt.close()
    print("    -> plots/perbandingan_waktu_plot.png")

    # 3. Konvergensi ACO
    plt.figure(figsize=(8, 3.5))
    log = aco_res['convergence_log']
    plt.plot(range(1, len(log)+1), log, color='#0284c7', linewidth=2)
    plt.title('Kurva Konvergensi Nilai Fungsi Objektif Modified ACO', fontsize=11, fontweight='bold', pad=12)
    plt.xlabel('Iterasi (1 s.d. 150)', fontsize=9)
    plt.ylabel('Cost Terbaik (Best Cost)', fontsize=9)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig('plots/konvergensi_aco_plot.png', dpi=300)
    plt.close()
    print("    -> plots/konvergensi_aco_plot.png")


def main():
    random.seed(42)

    SEP = "=" * 68

    print(SEP)
    print("  OPTIMASI SETLIST ORKESTRA KLASIK — ASA 2025/2026")
    print(f"  Dataset: {N} repertoar  |  W1={W1}  W2={W2}  Lambda={LAMBDA}")
    print(SEP)

    # ----------------------------------------------------------
    # Dataset
    # ----------------------------------------------------------
    print(f"\n{'ID':<4} {'Judul':<44} {'Key':<5} {'BPM':<6} {'Energi'}")
    print("-" * 65)
    for s in SONGS:
        print(f"{s['id']:<4} {s['title']:<44} {KEY_NAMES[s['key']]:<5} {s['bpm']:<6} {s['energy']}/10")

    # ----------------------------------------------------------
    # Jalankan algoritma
    # ----------------------------------------------------------
    print(f"\n{SEP}")
    print("  EKSEKUSI ALGORITMA")
    print(SEP)

    print("\n  [1/3] Dijkstra Nearest Neighbor... ", end="", flush=True)
    t0 = time.perf_counter()
    path_d, cost_d = dijkstra_nearest_neighbor(start=0)
    t_d = (time.perf_counter() - t0) * 1000
    print(f"selesai ({t_d:.4f} ms)")

    print("  [2/3] Branch and Bound...          ", end="", flush=True)
    t0 = time.perf_counter()
    path_bb, cost_bb, explored_bb, pruned_bb = branch_and_bound(start=0)
    t_bb = (time.perf_counter() - t0) * 1000
    print(f"selesai ({t_bb:.2f} ms)")

    print("  [3/3] Modified ACO (30 ants x 150)...", end="", flush=True)
    t0 = time.perf_counter()
    path_aco, cost_aco, aco_log = modified_aco(start=0)
    t_aco = (time.perf_counter() - t0) * 1000
    print(f"selesai ({t_aco:.2f} ms)")

    # ----------------------------------------------------------
    # Ringkasan perbandingan
    # ----------------------------------------------------------
    en_d,   drop_d   = _energy_stats(path_d)
    en_bb,  drop_bb  = _energy_stats(path_bb)
    en_aco, drop_aco = _energy_stats(path_aco)

    print(f"\n{SEP}")
    print("  PERBANDINGAN HASIL")
    print(SEP)
    print(f"\n  {'Algoritma':<28} {'Cost':>8} {'Waktu (ms)':>12} {'Drops':>7} {'Tipe':>14}")
    print(f"  {'-'*63}")
    print(f"  {'Dijkstra NN':<28} {cost_d:>8.2f} {t_d:>12.4f} {drop_d:>7} {'Greedy':>14}")
    print(f"  {'Branch and Bound':<28} {cost_bb:>8.2f} {t_bb:>12.2f} {drop_bb:>7} {'Eksak':>14}")
    print(f"  {'Modified ACO':<28} {cost_aco:>8.2f} {t_aco:>12.2f} {drop_aco:>7} {'Metaheuristik':>14}")
    print(f"\n  B&B: {explored_bb:,} node dieksplorasi | {pruned_bb:,} dipangkas")
    if explored_bb + pruned_bb > 0:
        eff = pruned_bb / (explored_bb + pruned_bb) * 100
        print(f"  Efisiensi pruning: {eff:.1f}%")

    # ----------------------------------------------------------
    # Detail setlist per algoritma
    # ----------------------------------------------------------
    for label, path, cost in [
        ("DIJKSTRA", path_d, cost_d),
        ("BRANCH AND BOUND", path_bb, cost_bb),
        ("MODIFIED ACO", path_aco, cost_aco),
    ]:
        print(f"\n  [{label}]  Cost = {cost:.2f}")
        print(f"  {'#':<4} {'E':>4} {'BPM':>5} {'Key':>4}   Judul")
        print(f"  {'-' * 58}")
        for pos, idx in enumerate(path):
            s    = SONGS[idx]
            flag = " [v]" if pos > 0 and s["energy"] < SONGS[path[pos-1]]["energy"] else "    "
            print(f"  {pos+1:<4} {s['energy']:>3}/10 {s['bpm']:>5} {KEY_NAMES[s['key']]:>4} {flag} {s['title']}")

    # ----------------------------------------------------------
    # Simpan hasil ke results.json
    # ----------------------------------------------------------
    dijkstra_res = {
        "path": path_d, "cost": cost_d, "time_ms": t_d,
        "energies": en_d, "drops": drop_d,
    }
    bb_res = {
        "path": path_bb, "cost": cost_bb, "time_ms": t_bb,
        "energies": en_bb, "drops": drop_bb,
        "explored": explored_bb, "pruned": pruned_bb,
    }
    aco_res = {
        "path": path_aco, "cost": cost_aco, "time_ms": t_aco,
        "energies": en_aco, "drops": drop_aco,
        "convergence_log": aco_log,
    }
    results = {
        "meta": {
            "n_songs": N,
            "w1": W1, "w2": W2, "lambda": LAMBDA,
        },
        "songs": SONGS,
        "key_names": KEY_NAMES,
        "dijkstra": dijkstra_res,
        "branch_and_bound": bb_res,
        "modified_aco": aco_res,
    }
    with open("plots/results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n  Hasil disimpan ke plots/results.json")
    
    # ----------------------------------------------------------
    # Generate grafik PNG
    # ----------------------------------------------------------
    generate_charts(dijkstra_res, bb_res, aco_res)
    print(f"\n{SEP}")
    print("  SELESAI. Output:")
    print("    - plots/results.json  (data mentah)")
    print("    - plots/kurva_energi_plot.png")
    print("    - plots/perbandingan_waktu_plot.png")
    print("    - plots/konvergensi_aco_plot.png")
    print(SEP)
if __name__ == "__main__":
    main()
