import networkx as nx
from skyfield.toposlib import Topos
from utils import haversine, calculate_capacity
from utils import haversine_with_altitude
from utils import latency_calculation
from utils import euclidean_distance

class SatelliteGraph:
    """
    LISL_range = 659.5, 1319, 1500, 1700, 2500, e 5016 km
    """
    def __init__(self, LISL_range=659.5):
        self.G = nx.Graph()
        self.LISL_range = LISL_range

    def add_nodes(self, satellites):
        for sat in satellites:
            # Calcola la latitudine e la longitudine media dal track
            mid_lat = (sat['track'][0][0] + sat['track'][-1][0]) / 2
            mid_lon = (sat['track'][0][1] + sat['track'][-1][1]) / 2
           # mid_lon = mid_lon if mid_lon >= 0 else mid_lon + 360  # Gestione longitudine negativa

            orbital_plane = sat.get('plane')

            sat_data = {
                'name': sat['name'],
                'lat': mid_lat,
                'lon': mid_lon,
                'alt': sat['track'][-1][2],
                'plane': orbital_plane,
            }
            self.G.add_node(sat['name'], **sat_data)

    def can_add_edge(self, node1, node2):
        return self.G.degree(node1) < 4 and self.G.degree(node2) < 4

   
    def connect_nodes(self):
        nodes = list(self.G.nodes(data=True))
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                sat1 = nodes[i][1]
                sat2 = nodes[j][1]

                distance = euclidean_distance(sat1['lat'], sat1['lon'], sat1['alt'], sat2['lat'], sat2['lon'], sat2['alt'])

                if distance <= self.LISL_range:
                    self.G.add_edge(nodes[i][0], nodes[j][0], weight=distance)


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

        if not path or len(path) < 2:
            print("Il percorso deve contenere almeno due nodi.")
            return None

        for i in range(len(path) - 1):
            found = False
            for edge in self.G.edges(data=True):
               if (edge[0] == path[i] and edge[1] == path[i+1]) or (edge[1] == path[i] and edge[0] == path[i+1]):
                    total_latency += latency_calculation(edge[2]['weight'])
                    found = True
                    break
            if not found:
                raise ValueError(f"Arco non trovato tra {path[i]} e {path[i + 1]}")
        return total_latency

    def calculate_total_throughput(self, path, P_t, G_t, G_r, lambda_, B, N):
        """
        Calcola il throughput massimo lungo un percorso dato.
        """
        if not path or len(path) < 2:
            print("Il percorso deve contenere almeno due nodi.")
            return None

        throughput_values = []

        for i in range(len(path) - 1):
            found = False
            for edge in self.G.edges(data=True):
                if (edge[0] == path[i] and edge[1] == path[i + 1]) or (edge[1] == path[i] and edge[0] == path[i + 1]):
                    throughput_values.append(calculate_capacity(
                        P_t, G_t, G_r, lambda_, edge[2]['weight'], B, N
                    ))
                    found = True
                    break
            if not found:
                raise ValueError(f"Arco non trovato tra {path[i]} e {path[i + 1]}")

        return min(throughput_values) if throughput_values else None  # Minimo valore lungo il percorso





