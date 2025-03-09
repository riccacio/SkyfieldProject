import networkx as nx
from skyfield.toposlib import Topos
from utils import haversine, calculate_capacity
from utils import haversine_with_altitude
from utils import latency_calculation
from utils import euclidean_distance

"""
class SatelliteGraph:
    def __init__(self, LISL_range=660, P=72, F=39, Q=None):
        """"""
        Se i parametri della costellazione Walker Delta (P, Q, F) sono forniti,
        la modalità di connettività ISL seguirà le regole viste nell’articolo.

        - LISL_range: Range massimo per il collegamento.
        - P: Numero totale di piani orbitali.
        - Q: Numero di satelliti per piano.
        - F: Phasing factor (fase) per il collegamento tra piani adiacenti.
        """"""
        self.G = nx.Graph()
        self.LISL_range = LISL_range
        self.P = P
        self.Q = Q
        self.F = F


    def add_nodes(self, satellites):
        """"""
        Aggiunge i satelliti al grafo.
        Ogni satellite deve essere un dizionario che contiene almeno:
            - 'name': identificativo univoco
            - 'lat', 'lon', 'alt': coordinate (latitudine, longitudine, altitudine)

        Se sono disponibili, devono essere presenti anche:
            - 'orbit': indice del piano orbitale (intero, 0 ≤ orbit < P)
            - 'index': posizione all’interno del piano (intero, 0 ≤ index < Q)
            - 'angle': (opzionale) posizione angolare, per eventuali ordinamenti
       """ """


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
                'angle': sat['angle'],  # posizione angolare lungo l'orbita (in gradi)
                'index': sat['index']
            }
            self.G.add_node(sat['name'], **sat_data)

        if self.Q is None:
            # Stima Q come il numero di satelliti diviso il numero di piani
            self.Q = len(satellites) // self.P


    def connect_nodes(self):
        """"""
        Collega i satelliti.

        Se i parametri per la costellazione Walker Delta (P, Q, F) sono stati forniti
        e i nodi hanno gli attributi 'orbit' e 'index', viene usata la modalità ISL
        basata sui collegamenti fissi (massimo 4 per satellite, secondo il modello Walker Delta).
        Altrimenti, viene usato il metodo precedente che collega tutti i satelliti la cui
        distanza euclidea è <= LISL_range.
        """"""

        if self.P is not None and self.Q is not None and self.F is not None:
            self.connect_nodes_ISL()
        else:
            nodes = list(self.G.nodes(data=True))
            for i in range(len(nodes)):
                for j in range(i + 1, len(nodes)):
                    sat1 = nodes[i][1]
                    sat2 = nodes[j][1]
                    distance = euclidean_distance(sat1['lat'], sat1['lon'], sat1['alt'], sat2['lat'], sat2['lon'], sat2['alt'])
                    if distance <= self.LISL_range:
                        self.G.add_edge(nodes[i][0], nodes[j][0], weight=distance)




    def connect_nodes_ISL(self):
        """"""
        Collega i satelliti secondo le regole ISL per costellazioni Walker Delta.
        Si assume che ogni nodo abbia gli attributi:
            - 'orbit': indice del piano orbitale (0 ≤ orbit < P)
            - 'index': posizione all’interno del piano (0 ≤ index < Q)

        I collegamenti sono:
            • Intra-plane:
                - Predecessore: (o, (i-1) mod Q)
                - Successore:   (o, (i+1) mod Q)
            • Inter-plane:
                - Vicino a sinistra: se o != 0, allora (o-1, i); altrimenti (P-1, (i-F) mod Q)
                - Vicino a destra:   se o != P-1, allora (o+1, i); altrimenti (0, (i+F) mod Q)
        """"""
        if self.P is None or self.Q is None or self.F is None:
            raise ValueError("I parametri P, Q e F devono essere definiti per la connettività ISL.")

        # Costruisce un dizionario per accedere ai nodi tramite (orbit, index)
        node_dict = {}
        for node, data in self.G.nodes(data=True):
            print(f"Nodo: {node}, Dati: {data}")
            if 'orbit' in data and 'index' in data:
                node_dict[(data['orbit'], data['index'])] = node
                print(f"Aggiungo nodo {node} con chiave ({data['orbit']}, {data['angle']})")

        # Per ogni satellite, aggiunge gli archi con i satelliti vicini secondo le regole
        for (o, i), node in node_dict.items():
            # Intra-plane: collega con predecessore e successore
            pred_key = (o, (i - 1) % self.Q)
            succ_key = (o, (i + 1) % self.Q)
            if pred_key in node_dict:
                print(f"Aggiungo arco tra {node} e {node_dict[pred_key]}")
                self._add_edge_if_in_range(node, node_dict[pred_key])
            if succ_key in node_dict:
                print(f"Aggiungo arco tra {node} e {node_dict[succ_key]}")
                self._add_edge_if_in_range(node, node_dict[succ_key])

            # Inter-plane: collega con il vicino a sinistra
            if o != 0:
                left_key = (o - 1, i)
            else:
                left_key = (self.P - 1, (i - self.F) % self.Q)

            if left_key in node_dict:
                print(f"Aggiungo arco tra {node} e {node_dict[left_key]}")
                self._add_edge_if_in_range(node, node_dict[left_key])

            # Inter-plane: collega con il vicino a destra
            if o != self.P - 1:
                right_key = (o + 1, i)
            else:
                right_key = (0, (i + self.F) % self.Q)

            if right_key in node_dict:
                print(f"Aggiungo arco tra {node} e {node_dict[right_key]}")
                self._add_edge_if_in_range(node, node_dict[right_key])


    def _add_edge_if_in_range(self, node1, node2):
        """"""
        Aggiunge un arco tra node1 e node2 se la distanza euclidea (calcolata con la funzione
        euclidean_distance) è minore o uguale a LISL_range.
        Si assume che i nodi abbiano gli attributi 'lat', 'lon' e 'alt'.
        """"""
        data1 = self.G.nodes[node1]
        data2 = self.G.nodes[node2]
        distance = euclidean_distance(
            data1['lat'], data1['lon'], data1['alt'],
            data2['lat'], data2['lon'], data2['alt']
        )
        if distance <= self.LISL_range:
            self.G.add_edge(node1, node2, weight=distance)


    def get_graph(self):
        return self.G


    def find_shortest_path(self, start_node, end_node):
        try:
            # Utilizza Dijkstra per calcolare il percorso minimo (basato sul peso degli archi)
            path = nx.dijkstra_path(self.G, source=start_node, target=end_node, weight='weight')
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
                if (edge[0] == path[i] and edge[1] == path[i + 1]) or (edge[1] == path[i] and edge[0] == path[i + 1]):
                    # La funzione latency_calculation si aspetta di ricevere il segmento del path e i dati dell'arco
                    total_latency += latency_calculation([path[i], path[i + 1]], edge)
                    found = True
                    break
            if not found:
                raise ValueError(f"Arco non trovato tra {path[i]} e {path[i + 1]}")
        return total_latency
"""



class SatelliteGraph:
    def __init__(self, LISL_range=660):
        self.G = nx.Graph()
        self.LISL_range = LISL_range


    def add_nodes(self, satellites):        
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
            }
            self.G.add_node(sat['name'], **sat_data)

    def can_add_edge(self, node1, node2):
        return self.G.degree(node1) < 4 and self.G.degree(node2) < 4

    def connect_nodes(self):
        """Connette i satelliti se la distanza tra loro è inferiore a LISL_range."""
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
            raise ValueError("Il percorso deve contenere almeno due nodi.")

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





