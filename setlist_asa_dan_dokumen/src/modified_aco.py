# """
# Implementasi Modified Ant Colony Optimization (Modified ACO)
# untuk optimasi urutan setlist dengan mempertimbangkan kurva energi.

# Modifikasi utama dari ACO standar:
#   Heuristik visibilitas dimodifikasi menjadi energy-aware:
#       eta_mod(i, j, pos) = energy_match(j, pos) / (adj[i][j] + eps)

#   di mana energy_match mengukur seberapa cocok energi lagu j
#   dengan target energi pada posisi sekuensial 'pos' (target: ascending linear).

#   Mekanisme deposit feromon menggunakan strategi elitist:
#   hanya semut terbaik per iterasi yang mendeposit feromon.

# Parameter default:
#   num_ants   = 30    semut per iterasi
#   iterations = 150   jumlah iterasi
#   alpha      = 1.0   bobot intensitas feromon
#   beta       = 2.5   bobot heuristik
#   rho        = 0.5   laju evaporasi feromon
#   Q          = 200   konstanta deposit feromon

# Kompleksitas: O(iterations * num_ants * N^2)
# """

# import random

# from dataset import ADJ, N, SONGS


# def modified_aco(start=0, num_ants=30, iterations=150,
#                  alpha=1.0, beta=2.5, rho=0.5, Q=200):
#     """
#     Membangun urutan setlist menggunakan koloni semut yang dipandu
#     oleh feromon dan heuristik sadar-energi (energy-aware).

#     Parameter
#     ----------
#     start      : int    indeks lagu pembuka
#     num_ants   : int    jumlah semut per iterasi
#     iterations : int    jumlah iterasi total
#     alpha      : float  bobot intensitas feromon [tau^alpha]
#     beta       : float  bobot heuristik [eta^beta]
#     rho        : float  laju evaporasi feromon (0–1)
#     Q          : float  konstanta deposit feromon

#     Return
#     ------
#     best_path        : list[int]    urutan terbaik yang ditemukan
#     best_cost        : float        total cost urutan terbaik
#     convergence_log  : list[float]  best cost per iterasi (untuk analisis konvergensi)
#     """
#     # Inisialisasi matriks feromon seragam
#     pheromone = [[1.0] * N for _ in range(N)]

#     # Target kurva energi: ascending linear dari min ke max
#     e_min = min(s["energy"] for s in SONGS)
#     e_max = max(s["energy"] for s in SONGS)
#     target_energy = [
#         e_min + (e_max - e_min) * (pos / (N - 1)) for pos in range(N)
#     ]

#     best_path        = None
#     best_cost        = float("inf")
#     convergence_log  = []

#     for _ in range(iterations):
#         iter_paths = []
#         iter_costs = []

#         for _ in range(num_ants):
#             path           = [start]
#             visited        = [False] * N
#             visited[start] = True
#             ant_cost       = 0.0

#             for step in range(1, N):
#                 current    = path[-1]
#                 candidates = [j for j in range(N) if not visited[j]]

#                 # Hitung bobot probabilitas untuk setiap kandidat
#                 weights = []
#                 for j in candidates:
#                     energy_match = 1.0 / (1.0 + abs(SONGS[j]["energy"] - target_energy[step]))
#                     eta_mod      = energy_match / (ADJ[current][j] + 1e-9)
#                     tau          = pheromone[current][j]
#                     weights.append((tau ** alpha) * (eta_mod ** beta))

#                 # Seleksi roulette wheel
#                 total_w = sum(weights)
#                 r       = random.random() * total_w
#                 cumul   = 0.0
#                 chosen  = candidates[-1]
#                 for idx, w in enumerate(weights):
#                     cumul += w
#                     if cumul >= r:
#                         chosen = candidates[idx]
#                         break

#                 ant_cost        += ADJ[current][chosen]
#                 visited[chosen]  = True
#                 path.append(chosen)

#             iter_paths.append(path)
#             iter_costs.append(ant_cost)

#             if ant_cost < best_cost:
#                 best_cost = ant_cost
#                 best_path = path[:]

#         # --- Evaporasi feromon ---
#         for i in range(N):
#             for j in range(N):
#                 pheromone[i][j] = max(pheromone[i][j] * (1.0 - rho), 0.01)

#         # --- Deposit feromon (elitist: hanya semut terbaik per iterasi) ---
#         best_idx  = iter_costs.index(min(iter_costs))
#         elite     = iter_paths[best_idx]
#         deposit   = Q / iter_costs[best_idx]
#         for k in range(len(elite) - 1):
#             i, j = elite[k], elite[k + 1]
#             pheromone[i][j] += deposit
#             pheromone[j][i] += deposit

#         convergence_log.append(best_cost)

#     return best_path, best_cost, convergence_log

"""
Implementasi Modified Ant Colony Optimization (Modified ACO)
untuk optimasi urutan setlist dengan mempertimbangkan kurva energi.

Modifikasi utama dari ACO standar:
  Heuristik visibilitas dimodifikasi menjadi energy-aware:
      eta_mod(i, j, pos) = energy_match(j, pos) / (adj[i][j] + eps)

  di mana energy_match mengukur seberapa cocok energi lagu j
  dengan target energi pada posisi sekuensial 'pos' (target: ascending linear).

  Mekanisme deposit feromon menggunakan strategi elitist:
  hanya semut terbaik per iterasi yang mendeposit feromon.

Parameter default:
  num_ants   = 30    semut per iterasi
  iterations = 150   jumlah iterasi
  alpha      = 1.0   bobot intensitas feromon
  beta       = 2.5   bobot heuristik
  rho        = 0.5   laju evaporasi feromon
  Q          = 200   konstanta deposit feromon

Kompleksitas: O(iterations * num_ants * N^2)
"""
import random
from dataset import ADJ, N, SONGS

def modified_aco(start=0, num_ants=30, iterations=150,
                 alpha=1.0, beta=2.5, rho=0.5, Q=200):
    # Inisialisasi matriks feromon seragam
    pheromone = [[1.0] * N for _ in range(N)]
    # Target kurva energi: ascending linear dari min ke max
    e_min = min(s["energy"] for s in SONGS)
    e_max = max(s["energy"] for s in SONGS)
    target_energy = [
        e_min + (e_max - e_min) * (pos / (N - 1)) for pos in range(N)
    ]

    best_path        = None
    best_cost        = float("inf")
    convergence_log  = []

    for _ in range(iterations):
        iter_paths = []
        iter_costs = []

        for _ in range(num_ants):
            path           = [start]
            visited        = [False] * N
            visited[start] = True
            ant_cost       = 0.0

            for step in range(1, N):
                current    = path[-1]
                candidates = [j for j in range(N) if not visited[j]]

                # Hitung bobot probabilitas untuk setiap kandidat
                weights = []
                for j in candidates:
                    energy_match = 1.0 / (1.0 + abs(SONGS[j]["energy"] - target_energy[step]))
                    eta_mod      = energy_match / (ADJ[current][j] + 1e-9)
                    tau          = pheromone[current][j]
                    weights.append((tau ** alpha) * (eta_mod ** beta))

                # Seleksi roulette wheel
                total_w = sum(weights)
                r       = random.random() * total_w
                cumul   = 0.0
                chosen  = candidates[-1]
                for idx, w in enumerate(weights):
                    cumul += w
                    if cumul >= r:
                        chosen = candidates[idx]
                        break

                ant_cost        += ADJ[current][chosen]
                visited[chosen]  = True
                path.append(chosen)

            iter_paths.append(path)
            iter_costs.append(ant_cost)

            if ant_cost < best_cost:
                best_cost = ant_cost
                best_path = path[:]

        # --- Evaporasi feromon ---
        for i in range(N):
            for j in range(N):
                pheromone[i][j] = max(pheromone[i][j] * (1.0 - rho), 0.01)

        # --- Deposit feromon (elitist: hanya semut terbaik per iterasi) ---
        best_idx  = iter_costs.index(min(iter_costs))
        elite     = iter_paths[best_idx]
        deposit   = Q / iter_costs[best_idx]
        for k in range(len(elite) - 1):
            i, j = elite[k], elite[k + 1]
            pheromone[i][j] += deposit
            pheromone[j][i] += deposit

        convergence_log.append(best_cost)

    return best_path, best_cost, convergence_log
