"""
generate_report.py
------------------
Generator laporan HTML dari hasil eksperimen.
Membaca results.json (output dari main.py) dan menghasilkan
file hasil_eksperimen.html yang dapat dibuka di Firefox.

Penggunaan:
    python generate_report.py

Prasyarat:
    results.json harus sudah ada (jalankan main.py terlebih dahulu).

Author  : Shalom Kurniawan - 24060124120033
Matkul  : Analisis dan Strategi Algoritma 2025/2026
"""

import json
import os
import sys

INPUT_FILE  = "plots/results.json"
OUTPUT_FILE = "output/hasil_eksperimen.html"


# ============================================================
# HELPER: KOMPONEN HTML
# ============================================================

def _setlist_rows(path, songs, key_names):
    rows = ""
    for pos, idx in enumerate(path):
        s    = songs[idx]
        drop = pos > 0 and s["energy"] < songs[path[pos - 1]]["energy"]
        cls  = ' class="drop"' if drop else ""
        flag = " &#9660;" if drop else ""
        rows += (
            f"<tr{cls}>"
            f"<td>{pos + 1}</td>"
            f"<td>{s['energy']}/10</td>"
            f"<td>{s['bpm']}</td>"
            f"<td>{key_names[s['key']]}</td>"
            f"<td>{s['title']}{flag}</td>"
            f"</tr>\n"
        )
    return rows


def _energy_bar(energies):
    bars = ""
    for e in energies:
        h = e * 20
        bars += (
            f'<div style="display:inline-block;width:28px;height:{h}px;'
            f'background:var(--accent);margin:1px;vertical-align:bottom;'
            f'border-radius:3px 3px 0 0;" title="E={e}"></div>'
        )
    return bars


def _convergence_rows(log):
    rows = ""
    checkpoints = sorted(set(list(range(0, len(log), 25)) + [len(log) - 1]))
    for cp in checkpoints:
        rows += f"<tr><td>{cp + 1}</td><td>{log[cp]:.2f}</td></tr>\n"
    return rows


# ============================================================
# GENERATOR UTAMA
# ============================================================

def generate(data):
    songs     = data["songs"]
    key_names = data["key_names"]
    meta      = data["meta"]

    d   = data["dijkstra"]
    bb  = data["branch_and_bound"]
    aco = data["modified_aco"]

    eff_bb = (bb["pruned"] / (bb["explored"] + bb["pruned"]) * 100
              if bb["explored"] + bb["pruned"] > 0 else 0)

    # Konvergensi: iterasi di mana ACO pertama mencapai nilai terbaik
    log       = aco["convergence_log"]
    best_val  = aco["cost"]
    conv_iter = next((i + 1 for i, v in enumerate(log) if v <= best_val), len(log))

    pct_from_optimal = (aco["cost"] / bb["cost"] - 1) * 100

    html = f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Laporan Eksperimen ASA &mdash; Optimasi Setlist Orkestra Klasik</title>
  <style>
    :root {{
      --bg:     #0f1117;
      --card:   #1a1d2e;
      --border: #2a2d3e;
      --hover:  #1e2030;
      --accent: #4fc3f7;
      --gold:   #ffd54f;
      --red:    #ef5350;
      --green:  #66bb6a;
      --text:   #e0e0e0;
      --muted:  #9e9e9e;
    }}
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: 'Segoe UI', system-ui, sans-serif;
      font-size: 14px;
      line-height: 1.65;
      padding: 36px 40px;
      max-width: 1400px;
      margin: 0 auto;
    }}

    /* --- Heading --- */
    h1 {{ font-size: 1.55rem; color: var(--accent); margin-bottom: 4px; font-weight: 700; }}
    .meta {{ color: var(--muted); font-size: 0.82rem; margin-bottom: 36px; }}
    h2 {{
      font-size: 1rem; color: var(--gold); font-weight: 600;
      margin: 36px 0 14px;
      border-left: 3px solid var(--gold);
      padding-left: 10px;
      text-transform: uppercase; letter-spacing: 0.5px;
    }}
    h3 {{ font-size: 0.88rem; color: var(--accent); margin: 18px 0 8px; font-weight: 600; }}

    /* --- Summary cards --- */
    .grid-3 {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 14px;
      margin-bottom: 28px;
    }}
    .card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 18px 20px;
    }}
    .card.best  {{ border-color: var(--green); }}
    .card.worst {{ border-color: var(--red);   }}
    .card .lbl  {{ font-size: 0.7rem; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; }}
    .card .val  {{ font-size: 2rem; font-weight: 700; margin: 6px 0 4px; }}
    .card .sub  {{ font-size: 0.75rem; color: var(--muted); }}

    /* --- Tags --- */
    .tag {{
      display: inline-block; padding: 2px 7px;
      border-radius: 4px; font-size: 0.68rem; margin-left: 6px;
      vertical-align: middle; font-weight: 600;
    }}
    .tag-greedy {{ background: #4a148c; color: #ce93d8; }}
    .tag-eksak  {{ background: #1b5e20; color: #a5d6a7; }}
    .tag-meta   {{ background: #0d47a1; color: #90caf9; }}

    /* --- Tables --- */
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.83rem;
      margin-bottom: 20px;
    }}
    th {{
      background: #252840;
      color: var(--accent);
      padding: 8px 12px;
      text-align: left;
      font-weight: 600;
    }}
    td {{ padding: 6px 12px; border-bottom: 1px solid var(--border); }}
    tr.drop td {{ color: var(--red); }}
    tbody tr:hover td {{ background: var(--hover); }}

    /* --- 3-column layout --- */
    .cols-3 {{
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 20px;
    }}

    /* --- Energy bar chart --- */
    .bar-chart {{
      display: flex;
      align-items: flex-end;
      gap: 2px;
      padding: 10px 0 4px;
      height: 220px;
    }}

    /* --- Narrow tables --- */
    .tbl-narrow {{ max-width: 340px; }}

    /* --- Footer --- */
    footer {{
      margin-top: 52px;
      color: var(--muted);
      font-size: 0.78rem;
      border-top: 1px solid var(--border);
      padding-top: 14px;
    }}
  </style>
</head>
<body>

<h1>Laporan Eksperimen: Optimasi Setlist Orkestra Klasik</h1>
<p class="meta">
  Shalom Kurniawan &mdash; 24060124120033 &nbsp;|&nbsp;
  Analisis dan Strategi Algoritma 2025/2026 &nbsp;|&nbsp; Informatika UNDIP<br>
  Dataset: {meta['n_songs']} repertoar orkestra klasik populer<br>
  Parameter fungsi objektif: W<sub>1</sub>&nbsp;=&nbsp;{meta['w1']} (modulasi) &nbsp;&bull;&nbsp;
  W<sub>2</sub>&nbsp;=&nbsp;{meta['w2']} (tempo) &nbsp;&bull;&nbsp;
  &lambda;&nbsp;=&nbsp;{meta['lambda']} (penalti energi)
</p>

<!-- ================================================================ -->
<h2>I. Ringkasan Perbandingan Algoritma</h2>

<div class="grid-3">
  <div class="card worst">
    <div class="lbl">Dijkstra NN <span class="tag tag-greedy">Greedy</span></div>
    <div class="val" style="color:var(--red)">{d['cost']:.0f}</div>
    <div class="sub">Total Cost</div>
    <div class="sub">{d['time_ms']:.4f} ms &nbsp;&bull;&nbsp;
                     {d['drops']}x energy drop &nbsp;&bull;&nbsp; penalti {d['drops'] * meta['lambda']}</div>
  </div>
  <div class="card best">
    <div class="lbl">Branch and Bound <span class="tag tag-eksak">Eksak / Optimal</span></div>
    <div class="val" style="color:var(--green)">{bb['cost']:.0f}</div>
    <div class="sub">Total Cost &mdash; Solusi Optimal Global</div>
    <div class="sub">{bb['time_ms']:.2f} ms &nbsp;&bull;&nbsp;
                     {bb['drops']}x energy drop &nbsp;&bull;&nbsp; pruning {eff_bb:.1f}%</div>
  </div>
  <div class="card">
    <div class="lbl">Modified ACO <span class="tag tag-meta">Metaheuristik</span></div>
    <div class="val" style="color:var(--accent)">{aco['cost']:.0f}</div>
    <div class="sub">Total Cost (+{pct_from_optimal:.1f}% dari optimal)</div>
    <div class="sub">{aco['time_ms']:.2f} ms &nbsp;&bull;&nbsp;
                     {aco['drops']}x energy drop &nbsp;&bull;&nbsp; konvergen iter. {conv_iter}</div>
  </div>
</div>

<table>
  <thead>
    <tr>
      <th>Algoritma</th><th>Total Cost</th><th>Waktu (ms)</th>
      <th>Energy Drops</th><th>Penalti Energi</th><th>Cost Murni*</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Dijkstra (Nearest Neighbor)</td>
      <td>{d['cost']:.2f}</td><td>{d['time_ms']:.4f}</td>
      <td>{d['drops']}x</td><td>{d['drops'] * meta['lambda']}</td>
      <td>{d['cost'] - d['drops'] * meta['lambda']:.2f}</td>
    </tr>
    <tr style="font-weight:600">
      <td>Branch and Bound</td>
      <td style="color:var(--green)">{bb['cost']:.2f}</td><td>{bb['time_ms']:.2f}</td>
      <td>{bb['drops']}x</td><td>{bb['drops'] * meta['lambda']}</td>
      <td>{bb['cost'] - bb['drops'] * meta['lambda']:.2f}</td>
    </tr>
    <tr>
      <td>Modified ACO</td>
      <td>{aco['cost']:.2f}</td><td>{aco['time_ms']:.2f}</td>
      <td>{aco['drops']}x</td><td>{aco['drops'] * meta['lambda']}</td>
      <td>{aco['cost'] - aco['drops'] * meta['lambda']:.2f}</td>
    </tr>
  </tbody>
</table>
<p style="color:var(--muted);font-size:0.78rem">*Cost Murni = Total Cost dikurangi seluruh penalti energi.</p>

<!-- ================================================================ -->
<h2>II. Kurva Energi yang Dihasilkan</h2>
<div class="cols-3">
  <div>
    <h3>Dijkstra &mdash; {d['drops']} penurunan &nbsp;|&nbsp; Cost {d['cost']:.0f}</h3>
    <div class="bar-chart">{_energy_bar(d['energies'])}</div>
    <small style="color:var(--muted)">{d['energies']}</small>
  </div>
  <div>
    <h3>Branch &amp; Bound &mdash; {bb['drops']} penurunan &nbsp;|&nbsp; Cost {bb['cost']:.0f}</h3>
    <div class="bar-chart">{_energy_bar(bb['energies'])}</div>
    <small style="color:var(--muted)">{bb['energies']}</small>
  </div>
  <div>
    <h3>Modified ACO &mdash; {aco['drops']} penurunan &nbsp;|&nbsp; Cost {aco['cost']:.0f}</h3>
    <div class="bar-chart">{_energy_bar(aco['energies'])}</div>
    <small style="color:var(--muted)">{aco['energies']}</small>
  </div>
</div>

<!-- ================================================================ -->
<h2>III. Urutan Setlist Detail</h2>
<div class="cols-3">
  <div>
    <h3>Dijkstra &mdash; Cost = {d['cost']:.2f}</h3>
    <table>
      <thead><tr><th>#</th><th>E</th><th>BPM</th><th>Key</th><th>Repertoar</th></tr></thead>
      <tbody>{_setlist_rows(d['path'], songs, key_names)}</tbody>
    </table>
  </div>
  <div>
    <h3>Branch &amp; Bound &mdash; Cost = {bb['cost']:.2f}</h3>
    <table>
      <thead><tr><th>#</th><th>E</th><th>BPM</th><th>Key</th><th>Repertoar</th></tr></thead>
      <tbody>{_setlist_rows(bb['path'], songs, key_names)}</tbody>
    </table>
  </div>
  <div>
    <h3>Modified ACO &mdash; Cost = {aco['cost']:.2f}</h3>
    <table>
      <thead><tr><th>#</th><th>E</th><th>BPM</th><th>Key</th><th>Repertoar</th></tr></thead>
      <tbody>{_setlist_rows(aco['path'], songs, key_names)}</tbody>
    </table>
  </div>
</div>

<!-- ================================================================ -->
<h2>IV. Konvergensi Modified ACO</h2>
<table class="tbl-narrow">
  <thead><tr><th>Iterasi</th><th>Best Cost</th></tr></thead>
  <tbody>{_convergence_rows(log)}</tbody>
</table>

<!-- ================================================================ -->
<h2>V. Statistik Branch and Bound</h2>
<table class="tbl-narrow">
  <thead><tr><th>Metrik</th><th>Nilai</th></tr></thead>
  <tbody>
    <tr><td>Node dieksplorasi</td><td>{bb['explored']:,}</td></tr>
    <tr><td>Node dipangkas (pruned)</td><td>{bb['pruned']:,}</td></tr>
    <tr><td>Total node diproses</td><td>{bb['explored'] + bb['pruned']:,}</td></tr>
    <tr><td>Efisiensi pruning</td><td>{eff_bb:.1f}%</td></tr>
  </tbody>
</table>

<footer>
  Dibuat oleh generate_report.py &nbsp;|&nbsp;
  ASA 2025/2026 &nbsp;|&nbsp;
  Shalom Kurniawan &mdash; 24060124120033 &mdash; Informatika UNDIP
</footer>

</body>
</html>
"""
    return html


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    if not os.path.exists(INPUT_FILE):
        print(f"[ERROR] {INPUT_FILE} tidak ditemukan.")
        print("        Jalankan  python main.py  terlebih dahulu.")
        sys.exit(1)

    with open(INPUT_FILE, encoding="utf-8") as f:
        data = json.load(f)

    html = generate(data)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    abs_path = os.path.abspath(OUTPUT_FILE)
    print(f"[OK] Laporan disimpan: {OUTPUT_FILE}")
    print(f"     Buka di Firefox : file:///{abs_path.replace(chr(92), '/')}")
