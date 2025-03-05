import networkx as nx
from skyfield.toposlib import Topos

from utils import haversine_with_altitude as haversine

class SatelliteGraph:
    def __init__(self, LISL_range=660):
        self.G = nx.Graph()
        self.LISL_range = LISL_range

    def add_nodes(self, satellites):
        for sat in satellites:
            # prendo la latitudine e la longitudine media
            mid_lat = (sat['track'][0][0] + sat['track'][-1][0]) / 2
            mid_lon = (sat['track'][0][1] + sat['track'][-1][1]) / 2
            mid_lon = mid_lon if mid_lon >= 0 else mid_lon + 360  # Gestione longitudine

            sat_data = {
                'name': sat['name'],
                'lat': mid_lat,
                'lon': mid_lon,
                'alt' : sat['track'][-1][2]
            }
            self.G.add_node(sat['name'], **sat_data)

    def connect_nodes(self):
        nodes = list(self.G.nodes(data=True))
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                sat1 = nodes[i][1]
                sat2 = nodes[j][1]

                distance = haversine(sat1['lat'], sat1['lon'], sat1['alt'], sat2['lat'], sat2['lon'], sat2['alt'])

                if distance <= self.LISL_range:
                    self.G.add_edge(nodes[i][0], nodes[j][0], weight=distance)

    def get_graph(self):
        return self.G


    def find_shortest_path(self, start_node, end_node):
        try:
            # Calcola il cammino minimo basato sul peso degli archi (distanze)
            path = nx.dijkstra_path(self.G, source=start_node, target=end_node, weight='distance')
            return path
        except nx.NetworkXNoPath:
            print("Nessun percorso trovato tra", start_node, "e", end_node)
        except KeyError:
            print("Uno o entrambi i nodi non esistono nel grafo")