"""
dataset.py
----------
Lapisan data untuk proyek Optimasi Setlist Orkestra.
Berisi: dataset lagu, parameter fungsi objektif,
        fungsi cost transisi, dan matriks ketetanggaan.

Author  : Shalom Kurniawan - 24060124120033
Matkul  : Analisis dan Strategi Algoritma 2025/2026
"""

# ============================================================
# PEMETAAN CIRCLE OF FIFTHS (searah jarum jam)
# C=0, G=1, D=2, A=3, E=4, B=5, F#=6, Db=7, Ab=8, Eb=9, Bb=10, F=11
# Kunci minor dipetakan ke posisi relatif mayornya
# ============================================================
KEY_NAMES = ["C", "G", "D", "A", "E", "B", "F#", 
            "Db", "Ab", "Eb", "Bb", "F"]
# ============================================================
# DATASET: 15 Repertoar Orkestra Klasik
# Repertoar populer terstandarisasi untuk konser simfoni
# ============================================================
SONGS = [
    {"id":  0, "title": "Erik Satie – Gymnopédie No. 1",            
    "key":  2, "bpm":  54, "energy":  1},
    {"id":  1, "title": "J.S. Bach – Air on the G String",          
    "key":  2, "bpm":  60, "energy":  2},
    {"id":  2, "title": "Samuel Barber – Adagio for Strings",       
    "key":  7, "bpm":  60, "energy":  3},
    {"id":  3, "title": "Johann Pachelbel – Canon in D",            
    "key":  2, "bpm":  80, "energy":  3},
    {"id":  4, "title": "Edvard Grieg – Morning Mood (Peer Gynt)",   
    "key":  4, "bpm":  66, "energy":  4},
    {"id":  5, "title": "L. van Beethoven – Symphony No. 9, 3rd Mvt",
    "key": 10, "bpm":  60, "energy":  4},
    {"id":  6, "title": "J. Strauss II – The Blue Danube Waltz",    
    "key":  2, "bpm": 120, "energy":  5},
    {"id":  7, "title": "P.I. Tchaikovsky – Swan Lake Theme",       
    "key":  2, "bpm":  80, "energy":  6},
    {"id":  8, "title": "W.A. Mozart – Symphony No. 40, 1st Mvt",   
    "key": 10, "bpm": 110, "energy":  7},
    {"id":  9, "title": "Antonio Vivaldi – Spring (The Four Seasons)",
    "key":  4, "bpm": 108, "energy":  7},
    {"id": 10, "title": "L. van Beethoven – Symphony No. 5, 1st Mvt",
    "key":  9, "bpm": 108, "energy":  8},
    {"id": 11, "title": "Richard Wagner – Ride of the Valkyries",   
    "key":  5, "bpm": 120, "energy":  9},
    {"id": 12, "title": "Edvard Grieg – In the Hall of the Mountain King",
    "key": 2, "bpm": 138, "energy":  9},
    {"id": 13, "title": "Gioachino Rossini – William Tell Overture",
    "key":  4, "bpm": 150, "energy": 10},
    {"id": 14, "title": "P.I. Tchaikovsky – 1812 Overture",         
    "key":  9, "bpm": 140, "energy": 10},
]
N = len(SONGS)

# ============================================================
# PARAMETER FUNGSI OBJEKTIF
# ============================================================

W1     = 5    # bobot jarak modulasi (Circle of Fifths)
W2     = 0.5  # bobot selisih tempo (BPM)
# Lambda (P) disesuaikan agar penalti transisi energi dominan (50)
LAMBDA = 50   # penalti penurunan energi

# ============================================================
# FUNGSI OBJEKTIF (COST FUNCTION)
# Total_Cost(u,v) = W1 * C_mod^2 + W2 * C_bpm + C_penalti
# ============================================================

def transition_cost(i, j):
    """
    Menghitung bobot penalti transisi dari lagu i ke lagu j.

    Komponen:
      C_mod     : jarak geodesik pada Circle of Fifths, dipangkatkan dua (kuadrat)
      C_bpm     : selisih tempo absolut
      C_penalti : LAMBDA jika energi lagu j lebih rendah dari lagu i
    """
    diff  = abs(SONGS[i]["key"] - SONGS[j]["key"])
    c_mod = (min(diff, 12 - diff)) ** 2
    c_bpm = abs(SONGS[i]["bpm"] - SONGS[j]["bpm"])
    c_pen = LAMBDA if SONGS[j]["energy"] < SONGS[i]["energy"] else 0
    return W1 * c_mod + W2 * c_bpm + c_pen



def path_total_cost(path):
    """Menghitung total cost dari seluruh urutan lagu dalam path."""
    return sum(ADJ[path[k]][path[k + 1]] for k in range(len(path) - 1))


# ============================================================
# MATRIKS KETETANGGAAN (dibangun sekali saat modul dimuat)
# ============================================================

ADJ = [[0.0] * N for _ in range(N)]
for _i in range(N):
    for _j in range(N):
        if _i != _j:
            ADJ[_i][_j] = transition_cost(_i, _j)
