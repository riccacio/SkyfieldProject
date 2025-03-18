from collections import defaultdict

import networkx as nx
from skyfield.toposlib import Topos
from utils import haversine, calculate_capacity
from utils import haversine_with_altitude
from utils import latency_calculation
from utils import euclidean_distance

class SatelliteGraph:
    def __init__(self, LISL_range):
        self.G = nx.Graph()
        self.LISL_range = LISL_range

    def add_nodes(self, satellites):
        for sat in satellites:
            # Calcola la latitudine e la longitudine media dal track
            mid_lat = (sat['track'][0][0] + sat['track'][-1][0]) / 2
            mid_lon = (sat['track'][0][1] + sat['track'][-1][1]) / 2
            # L'orbital_plane è già memorizzato in sat['plane']
            orbital_plane = sat.get('plane')
            plane_index = sat.get('plane_index', None)
            sat_index_in_plane = sat.get('sat_index_in_plane', None)

            sat_data = {
                'name': sat['name'],
                'lat': mid_lat,
                'lon': mid_lon,
                'alt': sat['track'][-1][2],
                'plane': orbital_plane,
                'plane_index': plane_index,
                'sat_index_in_plane': sat_index_in_plane,
            }
            self.G.add_node(sat['name'], **sat_data)

    def _try_add_edge(self, node_a, node_b):
        """Aggiunge un arco fra node_a e node_b se la distanza è entro LISL_range."""
        if self.G.has_edge(node_a, node_b):
            return
        sat_a = self.G.nodes[node_a]
        sat_b = self.G.nodes[node_b]
        distance = euclidean_distance(
            sat_a['lat'], sat_a['lon'], sat_a['alt'],
            sat_b['lat'], sat_b['lon'], sat_b['alt']
        )
        if distance <= self.LISL_range:
            self.G.add_edge(node_a, node_b, weight=distance)

    def _find_sat_by_index(self, sat_list, target_index):
        """
        Dato un elenco di satelliti (tupla (node_name, attrs)) già ordinato,
        restituisce il satellite con sat_index_in_plane uguale a target_index.
        """
        for node_name, attrs in sat_list:
            if attrs.get('sat_index_in_plane') == target_index:
                return (node_name, attrs)
        return None

    def connect_nodes_plus_grid(self):
        """
        Collega i satelliti secondo la topologia “+Grid”:
          - Connetti il satellite al successivo e al precedente nello stesso piano.
          - Connetti il satellite a quello con lo stesso sat_index_in_plane nei piani adiacenti.
        """
        # Raggruppa i nodi per plane_index
        plane_dict = defaultdict(list)
        for node_name, attrs in self.G.nodes(data=True):
            p_idx = attrs.get('plane_index')
            if p_idx is not None:
                plane_dict[p_idx].append((node_name, attrs))

        # Ordina i satelliti in ogni piano per sat_index_in_plane
        for p_idx in plane_dict:
            plane_dict[p_idx].sort(key=lambda x: x[1].get('sat_index_in_plane', 0))

        # Ottieni la lista dei piani ordinati
        all_planes = sorted(plane_dict.keys())

        # Per ogni piano, collega:
        for p_idx in all_planes:
            sat_list = plane_dict[p_idx]
            for i, (node_name, attrs) in enumerate(sat_list):
                # Collegamento all'interno dello stesso piano: collega al successivo e al precedente
                if i > 0:
                    prev_node, _ = sat_list[i - 1]
                    self._try_add_edge(node_name, prev_node)
                if i < len(sat_list) - 1:
                    next_node, _ = sat_list[i + 1]
                    self._try_add_edge(node_name, next_node)

                # Collegamento con piani adiacenti: usa lo stesso sat_index_in_plane
                sat_idx = attrs.get('sat_index_in_plane')
                # Piano superiore (p_idx + 1)
                if (p_idx + 1) in plane_dict:
                    candidate = self._find_sat_by_index(plane_dict[p_idx + 1], sat_idx)
                    if candidate is not None:
                        self._try_add_edge(node_name, candidate[0])
                # Piano inferiore (p_idx - 1)
                if (p_idx - 1) in plane_dict:
                    candidate = self._find_sat_by_index(plane_dict[p_idx - 1], sat_idx)
                    if candidate is not None:
                        self._try_add_edge(node_name, candidate[0])

    def connect_nodes_hybrid(self, min_degree=2, extra_range_factor=1.2):
        # 1. Collega secondo la topologia +Grid
        self.connect_nodes_plus_grid()

        # 2. Collega extra basandoti sulla distanza per garantire una connettività minima
        nodes = list(self.G.nodes())
        for node in nodes:
            if self.G.degree(node) < min_degree:
                # Costruisci una lista di candidati (non già connessi) con distanza
                candidate_neighbors = []
                for other in nodes:
                    if other == node or self.G.has_edge(node, other):
                        continue
                    # Calcola la distanza tra 'node' e 'other'
                    sat_node = self.G.nodes[node]
                    sat_other = self.G.nodes[other]
                    d = euclidean_distance(
                        sat_node['lat'], sat_node['lon'], sat_node['alt'],
                        sat_other['lat'], sat_other['lon'], sat_other['alt']
                    )
                    # Permetti un range leggermente più ampio per i collegamenti extra
                    if d <= self.LISL_range * extra_range_factor:
                        candidate_neighbors.append((other, d))
                # Ordina i candidati per distanza
                candidate_neighbors.sort(key=lambda x: x[1])
                # Aggiungi collegamenti fino a raggiungere min_degree o finché ci sono candidati
                for candidate, d in candidate_neighbors:
                    if self.G.degree(node) >= min_degree:
                        break
                    # Opzionale: puoi anche verificare che il candidato non abbia troppi collegamenti
                    if self.G.degree(candidate) < 4:
                        self.G.add_edge(node, candidate, weight=d)


    def connect_nodes(self):
        nodes = list(self.G.nodes(data=True))
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                sat1 = nodes[i][1]
                sat2 = nodes[j][1]
                distance = euclidean_distance(sat1['lat'], sat1['lon'], sat1['alt'],
                                              sat2['lat'], sat2['lon'], sat2['alt'])
                if distance <= self.LISL_range:
                    self.G.add_edge(nodes[i][0], nodes[j][0], weight=distance)


    def get_graph(self):
        return self.G

    def find_shortest_path_Dijkstra(self, start_node, end_node):
        try:
            # Calcola il cammino minimo basato sul peso degli archi (distanze)
            path = nx.dijkstra_path(self.G, source=start_node, target=end_node, weight='distance')
            print(f"Numero di Hop: {len(path) - 1}")
            return path
        except nx.NetworkXNoPath:
            print("Nessun percorso trovato tra", start_node, "e", end_node)
        except KeyError:
            print("Uno o entrambi i nodi non esistono nel grafo")

    def find_shortest_path_minHop(self, start_node, end_node):
        try:
            # Se non inserisco un peso, mi calcola il bfs
            path = nx.shortest_path(self.G, source=start_node, target=end_node)
            print(f"Numero di Hop: {len(path) - 1}")
            return path
        except nx.NetworkXNoPath:
            print("Nessun percorso trovato tra", start_node, "e", end_node)
        except KeyError:
            print("Uno o entrambi i nodi non esistono nel grafo")

    def calculate_total_latency(self, path, city1, city2, load_factor):
        """
        Restituisce la latenza totale (one-way) in secondi.
        """
        total_latency = 0

        if not path or len(path) < 2:
            print("Il percorso deve contenere almeno due nodi.")
            return None

        distance_city1_sat = euclidean_distance(
            self.G.nodes[path[0]]['lat'], self.G.nodes[path[0]]['lon'], self.G.nodes[path[0]]['alt'],
            city1.latitude.degrees, city1.longitude.degrees, 0
        )
        distance_city2_sat = euclidean_distance(
            self.G.nodes[path[-1]]['lat'], self.G.nodes[path[-1]]['lon'], self.G.nodes[path[-1]]['alt'],
            city2.latitude.degrees, city2.longitude.degrees, 0
        )
        lat_earth_sat = latency_calculation(distance_city1_sat) * (1 / (1 - load_factor))
        lat_sat_earth = latency_calculation(distance_city2_sat) * (1 / (1 - load_factor))
        total_latency += lat_earth_sat + lat_sat_earth

        # Latenza ISL
        for i in range(len(path) - 1):
            found = False
            for edge in self.G.edges(data=True):
                if (edge[0] == path[i] and edge[1] == path[i + 1]) or (edge[1] == path[i] and edge[0] == path[i + 1]):
                    total_latency += latency_calculation(edge[2]['weight']) * (1 / (1 - load_factor))
                    found = True
                    break
            if not found:
                raise ValueError(f"Arco non trovato tra {path[i]} e {path[i + 1]}")

        return total_latency

    def calculate_total_throughput(
            self, path, city1, city2, load_factor,
            P_t_laser, G_laser, lambda_laser, B_laser,
            P_t_ka, G_ka, lambda_ka, B_ka,
            P_t_ku, G_ku, lambda_ku, B_ku
    ):
        """
        Calcola e ritorna (throughput_downlink, throughput_uplink, throughput_ISL).
        """
        if not path or len(path) < 2:
            print("Il percorso deve contenere almeno due nodi.")
            return None

        # calcolo throughput banda Ka (downlink)
        distance_city1_sat = euclidean_distance(
            self.G.nodes[path[0]]['lat'], self.G.nodes[path[0]]['lon'], self.G.nodes[path[0]]['alt'],
            city1.latitude.degrees, city1.longitude.degrees, 0
        )
        distance_city2_sat = euclidean_distance(
            self.G.nodes[path[-1]]['lat'], self.G.nodes[path[-1]]['lon'], self.G.nodes[path[-1]]['alt'],
            city2.latitude.degrees, city2.longitude.degrees, 0
        )

        thr_down_ka_1 = calculate_capacity(P_t_ka, G_ka, lambda_ka, distance_city1_sat, B_ka) * (1 - load_factor)
        thr_down_ka_2 = calculate_capacity(P_t_ka, G_ka, lambda_ka, distance_city2_sat, B_ka) * (1 - load_factor)
        throughput_downlink_ka = min(thr_down_ka_1, thr_down_ka_2)

        # calcolo throughput banda Ku (uplink)
        thr_up_ku_1 = calculate_capacity(P_t_ku, G_ku, lambda_ku, distance_city1_sat, B_ku) * (1 - load_factor)
        thr_up_ku_2 = calculate_capacity(P_t_ku, G_ku, lambda_ku, distance_city2_sat, B_ku) * (1 - load_factor)
        throughput_uplink_ku = min(thr_up_ku_1, thr_up_ku_2)

        # calcolo throughput LISL
        throughput_values_ISL = []
        for i in range(len(path) - 1):
            found = False
            for edge in self.G.edges(data=True):
                if (edge[0] == path[i] and edge[1] == path[i + 1]) or (edge[1] == path[i] and edge[0] == path[i + 1]):
                    thr_isl = (calculate_capacity(P_t_laser, G_laser, lambda_laser, edge[2]['weight'], B_laser) * (1 - load_factor))
                    throughput_values_ISL.append(thr_isl)
                    found = True
                    break
            if not found:
                raise ValueError(f"Arco non trovato tra {path[i]} e {path[i + 1]}")

        throughput_isl_laser = min(throughput_values_ISL) if throughput_values_ISL else 0

        print(f"Throughput Downlink banda Ka: {throughput_downlink_ka:.3f} Gbps")
        print(f"Throughput Uplink banda Ku: {throughput_uplink_ku:.3f} Gbps")
        print(f"Throughput ISL Laser: {throughput_isl_laser:.3f} Gbps")

        return throughput_downlink_ka, throughput_uplink_ku, throughput_isl_laser