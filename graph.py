import networkx as nx
from skyfield.toposlib import Topos
from utils import haversine
from utils import haversine_with_altitude
from utils import latency_calculation
from utils import euclidean_distance


class SatelliteGraph:
    def __init__(self, LISL_range=3000):
        self.G = nx.Graph()
        self.LISL_range = LISL_range

    def add_nodes(self, satellites):
        """
        Aggiunge i satelliti al grafo.
        Oltre a 'lat', 'lon' e 'alt', si presume che ogni satellite abbia anche:
          - 'orbit': identificativo numerico dell'orbita
          - 'angle': posizione angolare lungo l'orbita (in gradi)
        """
        for sat in satellites:
            # Calcola la latitudine e la longitudine media dal track
            mid_lat = (sat['track'][0][0] + sat['track'][-1][0]) / 2
            mid_lon = (sat['track'][0][1] + sat['track'][-1][1]) / 2
            mid_lon = mid_lon if mid_lon >= 0 else mid_lon + 360  # Gestione longitudine negativa

            sat_data = {
                'name': sat['name'],
                'lat': mid_lat,
                'lon': mid_lon,
                'alt': sat['track'][-1][2],
                'orbit': sat['orbit'],  # ad esempio: numero o identificativo dell'orbita
                'angle': sat['angle']  # posizione angolare lungo l'orbita (in gradi)
            }
            self.G.add_node(sat['name'], **sat_data)

    def can_add_edge(self, node1, node2):
        """Verifica che entrambi i nodi abbiano meno di 4 collegamenti."""
        return self.G.degree(node1) < 4 and self.G.degree(node2) < 4

    def connect_nodes(self):
        """
        Collega i satelliti applicando i seguenti vincoli:
         - Solo se la distanza (euclidea) è entro LISL_range.
         - Collegamenti tra satelliti della stessa orbita: solo ai nodi immediatamente davanti e dietro.
         - Collegamenti tra orbite adiacenti: collega il satellite con quello in orbita immediatamente superiore
           e quello in orbita immediatamente inferiore aventi la posizione angolare (angle) più vicina.
         - Ogni satellite può avere al massimo 4 collegamenti.
        """
        # Raggruppa i satelliti per orbita
        orbits = {}
        for node, data in self.G.nodes(data=True):
            orbit = data.get('orbit')
            if orbit not in orbits:
                orbits[orbit] = []
            orbits[orbit].append((node, data))

        # 1. Collegamenti lungo la stessa orbita (vicini)
        for orb, sats in orbits.items():
            # Ordina i satelliti in base al valore di 'angle'
            sats.sort(key=lambda x: x[1]['angle'])
            n = len(sats)
            for i in range(n):
                # Il satellite si collega al successivo; uso il wrap-around per orbite circolari
                j = (i + 1) % n
                node1, data1 = sats[i]
                node2, data2 = sats[j]
                distance = euclidean_distance(
                    data1['lat'], data1['lon'], data1['alt'],
                    data2['lat'], data2['lon'], data2['alt']
                )
                if distance <= self.LISL_range and self.can_add_edge(node1, node2):
                    self.G.add_edge(node1, node2, weight=distance)

        # 2. Collegamenti tra orbite adiacenti
        # Ordina le orbite in base al loro identificativo (si presume che l'ordine numerico rifletta la posizione spaziale)
        sorted_orbits = sorted(orbits.keys())
        for idx, orb in enumerate(sorted_orbits):
            current_satellites = orbits[orb]
            for node, data in current_satellites:
                # Verifica orbite adiacenti: quella inferiore (idx-1) e quella superiore (idx+1)
                for adj_idx in [idx - 1, idx + 1]:
                    if 0 <= adj_idx < len(sorted_orbits):
                        adjacent_orbit = sorted_orbits[adj_idx]
                        # Per la orbita adiacente, trova il satellite con 'angle' più vicino
                        candidate = None
                        min_angle_diff = float('inf')
                        for node_adj, data_adj in orbits[adjacent_orbit]:
                            # Calcola la differenza angolare considerando il wrap-around (0-360)
                            diff = abs(data['angle'] - data_adj['angle'])
                            diff = min(diff, 360 - diff)
                            if diff < min_angle_diff:
                                candidate = (node_adj, data_adj)
                                min_angle_diff = diff
                        if candidate is not None:
                            node_adj, data_adj = candidate
                            distance = euclidean_distance(
                                data['lat'], data['lon'], data['alt'],
                                data_adj['lat'], data_adj['lon'], data_adj['alt']
                            )
                            if distance <= self.LISL_range and self.can_add_edge(node, node_adj):
                                self.G.add_edge(node, node_adj, weight=distance)

    def get_graph(self):
        return self.G


    def find_shortest_path(self, start_node, end_node):
        try:
            # Calcola il cammino minimo basato sul peso degli archi (distanze)
            path = nx.dijkstra_path(self.G, source=start_node, target=end_node, weight='distance')
            print(f"Numero di Hop: {len(path) - 1}")
            return path
        except nx.NetworkXNoPath:
            print("Nessun percorso trovato tra", start_node, "e", end_node)
        except KeyError:
            print("Uno o entrambi i nodi non esistono nel grafo")

    def calculate_total_latency(self, path):
        total_latency = 0

        for i in range(len(path) - 1):
            found = False
            for edge in self.G.edges(data=True):
               if (edge[0] == path[i] and edge[1] == path[i+1]) or (edge[1] == path[i] and edge[0] == path[i+1]):
                    print(f"Arco tra {path[i]} e {path[i + 1]}: {edge[2]}")
                    total_latency += latency_calculation(edge[2]['weight'])
                    found = True
                    break
            if not found:
                raise ValueError(f"Arco non trovato tra {path[i]} e {path[i + 1]}")
        return total_latency