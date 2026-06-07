# """
# dijkstra.py
# -----------
# Implementasi Algoritma Dijkstra (Nearest Neighbor Greedy)
# untuk optimasi urutan setlist berdasarkan cost transisi minimum.

# Strategi: pada setiap langkah, pilih lagu berikutnya dengan
# cost transisi terkecil dari posisi saat ini (greedy lokal).

# Kompleksitas: O(N^2 log N)
# """

# import heapq

# from dataset import ADJ, N


# def dijkstra_nearest_neighbor(start=0):
#     """
#     Membangun urutan setlist secara greedy menggunakan priority queue.

#     Pada setiap iterasi, semua lagu yang belum dikunjungi dimasukkan
#     ke dalam min-heap berdasarkan cost transisi dari posisi saat ini.
#     Lagu dengan cost terkecil dipilih sebagai lagu berikutnya.

#     Parameter
#     ----------
#     start : int
#         Indeks lagu pembuka (default: 0)

#     Return
#     ------
#     path       : list[int]  — urutan indeks lagu
#     total_cost : float      — total cost urutan
#     """
#     visited            = [False] * N
#     path               = [start]
#     visited[start]     = True
#     total_cost         = 0.0

#     for _ in range(N - 1):
#         current = path[-1]

#         pq = []
#         for j in range(N):
#             if not visited[j]:
#                 heapq.heappush(pq, (ADJ[current][j], j))

#         min_cost, next_song = heapq.heappop(pq)
#         visited[next_song]  = True
#         path.append(next_song)
#         total_cost += min_cost

#     return path, total_cost
import heapq

from dataset import ADJ, N


def dijkstra_nearest_neighbor(start=0):
    visited            = [False] * N
    path               = [start]
    visited[start]     = True
    total_cost         = 0.0

    for _ in range(N - 1):
        current = path[-1]

        pq = []
        for j in range(N):
            if not visited[j]:
                heapq.heappush(pq, (ADJ[current][j], j))

        min_cost, next_song = heapq.heappop(pq)
        visited[next_song]  = True
        path.append(next_song)
        total_cost += min_cost

    return path, total_cost
