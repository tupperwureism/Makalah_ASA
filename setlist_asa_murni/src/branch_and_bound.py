# """
# branch_and_bound.py
# -------------------
# Implementasi Algoritma Branch and Bound (B&B)
# untuk mencari urutan setlist optimal secara eksak.

# Strategi:
#   - Branching  : eksplorasi semua permutasi urutan secara DFS rekursif
#   - Bounding   : pangkas cabang jika accumulated cost >= solusi terbaik
#   - Upper Bound: diinisialisasi dari solusi Dijkstra NN agar pruning
#                  bekerja agresif sejak awal

# Kompleksitas: O(N!) worst case — dipercepat signifikan oleh pruning.

# Author  : Shalom Kurniawan - 24060124120033
# Matkul  : Analisis dan Strategi Algoritma 2025/2026
# """

# from dataset import ADJ, N
# from dijkstra import dijkstra_nearest_neighbor


# def branch_and_bound(start=0):
#     """
#     Mencari urutan setlist dengan total cost minimum secara eksak.

#     Algoritma dimulai dengan upper bound dari solusi greedy Dijkstra,
#     lalu menggunakan DFS + pruning untuk menemukan solusi yang lebih baik.
#     Kandidat pada setiap level diurutkan dari cost terkecil (cheap-first)
#     agar pruning bekerja lebih agresif.

#     Parameter
#     ----------
#     start : int
#         Indeks lagu pembuka (default: 0)

#     Return
#     ------
#     best_path    : list[int]  — urutan optimal
#     best_cost    : float      — total cost optimal (global minimum)
#     explored     : int        — jumlah node yang dieksplorasi
#     pruned       : int        — jumlah node yang dipangkas
#     """
#     # --- Inisialisasi upper bound dari solusi greedy ---
#     init_path, init_cost = dijkstra_nearest_neighbor(start)

#     best  = {"cost": init_cost, "path": init_path[:]}
#     stats = {"explored": 0, "pruned": 0}

#     def _backtrack(path, visited, cost_so_far):
#         stats["explored"] += 1

#         # Base case: semua lagu sudah dijadwalkan
#         if len(path) == N:
#             if cost_so_far < best["cost"]:
#                 best["cost"] = cost_so_far
#                 best["path"] = path[:]
#             return

#         current    = path[-1]
#         candidates = sorted(
#             [(ADJ[current][j], j) for j in range(N) if not visited[j]]
#         )

#         for edge_cost, next_node in candidates:
#             new_cost = cost_so_far + edge_cost

#             # --- BOUNDING: pangkas cabang yang sudah tidak mungkin optimal ---
#             if new_cost >= best["cost"]:
#                 stats["pruned"] += 1
#                 continue

#             visited[next_node] = True
#             path.append(next_node)
#             _backtrack(path, visited, new_cost)
#             path.pop()
#             visited[next_node] = False

#     visited_init         = [False] * N
#     visited_init[start]  = True
#     _backtrack([start], visited_init, 0.0)

#     return best["path"], best["cost"], stats["explored"], stats["pruned"]
from dataset import ADJ, N
from dijkstra import dijkstra_nearest_neighbor
def branch_and_bound(start=0):
    # --- Inisialisasi upper bound dari solusi greedy ---
    init_path, init_cost = dijkstra_nearest_neighbor(start)
    best  = {"cost": init_cost, "path": init_path[:]}
    stats = {"explored": 0, "pruned": 0}
    def _backtrack(path, visited, cost_so_far):
        stats["explored"] += 1
        # Base case: semua lagu sudah dijadwalkan
        if len(path) == N:
            if cost_so_far < best["cost"]:
                best["cost"] = cost_so_far
                best["path"] = path[:]
            return
        current    = path[-1]
        candidates = sorted(
            [(ADJ[current][j], j) for j in range(N) if not visited[j]]
        )
        for edge_cost, next_node in candidates:
            new_cost = cost_so_far + edge_cost
            # --- BOUNDING: pangkas cabang yang sudah tidak mungkin optimal ---
            if new_cost >= best["cost"]:
                stats["pruned"] += 1
                continue
            visited[next_node] = True
            path.append(next_node)
            _backtrack(path, visited, new_cost)
            path.pop()
            visited[next_node] = False
    visited_init         = [False] * N
    visited_init[start]  = True
    _backtrack([start], visited_init, 0.0)
    return best["path"], best["cost"], stats["explored"], stats["pruned"]
