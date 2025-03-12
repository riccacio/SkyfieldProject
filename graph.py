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

    def calculate_total_latency(self, path, city1, city2, congestion_factor):
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

        lat_earth_sat = latency_calculation(distance_city1_sat) * (1 / (1 - congestion_factor))
        lat_sat_earth = latency_calculation(distance_city2_sat) * (1 / (1 - congestion_factor))

        total_latency += lat_earth_sat + lat_sat_earth

        # Latenza ISL
        for i in range(len(path) - 1):
            found = False
            for edge in self.G.edges(data=True):
                if (edge[0] == path[i] and edge[1] == path[i + 1]) or (edge[1] == path[i] and edge[0] == path[i + 1]):
                    total_latency += latency_calculation(edge[2]['weight']) * (1 / (1 - congestion_factor))
                    found = True
                    break
            if not found:
                raise ValueError(f"Arco non trovato tra {path[i]} e {path[i + 1]}")

        return total_latency

    def calculate_total_throughput(
            self, path, city1, city2, congestion_factor,
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

        thr_down_ka_1 = calculate_capacity(P_t_ka, G_ka, lambda_ka, distance_city1_sat, B_ka) * (1 - congestion_factor)
        thr_down_ka_2 = calculate_capacity(P_t_ka, G_ka, lambda_ka, distance_city2_sat, B_ka) * (1 - congestion_factor)
        throughput_downlink_ka = min(thr_down_ka_1, thr_down_ka_2)

        # calcolo throughput banda Ku (uplink)
        thr_up_ku_1 = calculate_capacity(P_t_ku, G_ku, lambda_ku, distance_city1_sat, B_ku) * (1 - congestion_factor)
        thr_up_ku_2 = calculate_capacity(P_t_ku, G_ku, lambda_ku, distance_city2_sat, B_ku) * (1 - congestion_factor)
        throughput_uplink_ku = min(thr_up_ku_1, thr_up_ku_2)

        # calcolo throughput LISL
        throughput_values_ISL = []
        for i in range(len(path) - 1):
            found = False
            for edge in self.G.edges(data=True):
                if (edge[0] == path[i] and edge[1] == path[i + 1]) or (edge[1] == path[i] and edge[0] == path[i + 1]):
                    thr_isl = (calculate_capacity(P_t_laser, G_laser, lambda_laser, edge[2]['weight'], B_laser) * (1 - congestion_factor))
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





