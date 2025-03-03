import networkx as nx
from utils import haversine

class SatelliteGraph:
    def __init__(self, LISL_range=660):
        """Inizializza un grafo con i satelliti e la distanza limite di collegamento."""
        self.G = nx.Graph()
        self.LISL_range = LISL_range

    def add_nodes(self, satellites):
        """Aggiunge i satelliti come nodi nel grafo."""
        for sat in satellites:
            mid_lat = (sat['track'][0][0] + sat['track'][-1][0]) / 2
            mid_lon = (sat['track'][0][1] + sat['track'][-1][1]) / 2
            mid_lon = mid_lon if mid_lon >= 0 else mid_lon + 360  # Gestione longitudine

            sat_data = {
                'name': sat['name'],
                'lat': mid_lat,
                'lon': mid_lon
            }
            self.G.add_node(sat['name'], **sat_data)

    def connect_nodes(self):
        """Connette i satelliti se la distanza tra loro è inferiore a LISL_range."""
        nodes = list(self.G.nodes(data=True))
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                sat1 = nodes[i][1]
                sat2 = nodes[j][1]

                distance = haversine(sat1['lat'], sat1['lon'], sat2['lat'], sat2['lon'])

                if distance <= self.LISL_range:
                    self.G.add_edge(nodes[i][0], nodes[j][0], weight=distance)

    def get_graph(self):
        return self.G