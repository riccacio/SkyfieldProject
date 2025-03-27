import csv
import os
import matplotlib.pyplot as plt

class DataHandler:
    def __init__(self):
        self.results = []  # risultati per ogni simulazione (valori singoli)
        self.avg_results = []  # risultati medi aggregati per ogni valore di LISL_range

        self.rtt_d_list = []
        self.rtt_m_list = []
        self.half_rtt_d_list = []
        self.half_rtt_m_list = []
        self.n_hops_d_list = []
        self.n_hops_m_list = []
        self.distance_d_list = []
        self.distance_m_list = []

        self.avg_rtt_d_list = []
        self.avg_half_rtt_d_list = []
        self.avg_rtt_m_list = []
        self.avg_half_rtt_m_list = []
        self.avg_n_hops_d_list = []
        self.avg_n_hops_m_list = []
        self.avg_distance_d_list = []
        self.avg_distance_m_list = []


    def add_result(self, n_hop_d, n_hop_m, half_rtt_d, rtt_d, half_rtt_m, rtt_m, distance_d,
                   distance_m):

        self.rtt_d_list.append(rtt_d)
        self.rtt_m_list.append(rtt_m)
        self.half_rtt_d_list.append(half_rtt_d)
        self.half_rtt_m_list.append(half_rtt_m)
        self.n_hops_d_list.append(n_hop_d)
        self.n_hops_m_list.append(n_hop_m)
        self.distance_d_list.append(distance_d)
        self.distance_m_list.append(distance_m)


    def reset_avg_values(self):
        self.rtt_d_list = []
        self.rtt_m_list = []
        self.half_rtt_d_list = []
        self.half_rtt_m_list = []
        self.n_hops_d_list = []
        self.n_hops_m_list = []
        self.distance_d_list = []
        self.distance_m_list = []

    def reset_rtt_values(self):
        self.rtt_d_list = []

    def add_avg_result(self, city1, city2, LISL_range, avg_n_hop_d, avg_n_hop_m,
                       avg_rtt_d, avg_rtt_m, avg_half_rtt_d, avg_half_rtt_m,
                       avg_distance_d, avg_distance_m):

        avg_result = {
            "City1": city1,
            "City2": city2,
            "LISL_range": LISL_range,
            "N. hop Dijkstra": avg_n_hop_d,
            "N. hop MinHops": avg_n_hop_m,
            "RTT medio (ms) Dijkstra": avg_rtt_d,
            "RTT medio (ms) MinHops": avg_rtt_m,
            "RTT/2 (ms) Dijkstra": avg_half_rtt_d,
            "RTT/2 (ms) MinHops": avg_half_rtt_m,
            "Distance totale media Dijkstra": avg_distance_d,
            "Distance totale media MinHops": avg_distance_m
        }
        self.avg_results.append(avg_result)
        self.avg_half_rtt_d_list.append(avg_half_rtt_d)
        self.avg_half_rtt_m_list.append(avg_half_rtt_m)
        self.avg_rtt_d_list.append(avg_rtt_d)
        self.avg_rtt_m_list.append(avg_rtt_m)
        self.avg_n_hops_d_list.append(avg_n_hop_d)
        self.avg_n_hops_m_list.append(avg_n_hop_m)
        self.avg_distance_d_list.append(avg_distance_d)
        self.avg_distance_m_list.append(avg_distance_m)



    def add_rtt_value(self, value):
        self.rtt_d_list.append(value)

    def get_rtt_values(self):
        return self.rtt_d_list

    def get_results_lists(self):
        return (self.rtt_d_list, self.half_rtt_d_list,
                self.rtt_m_list, self.half_rtt_m_list,
                self.n_hops_d_list, self.n_hops_m_list,
                self.distance_d_list, self.distance_m_list)

    def save_results_to_csv(self, filename):
        file_exists = os.path.exists(filename)
        with open(filename, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow([
                    "City1", "City2", "LISL_range",
                    "Numero di salti (Dijkstra)", "Numero di salti (Min-hop)",
                    "RTT medio (ms) (Dijkstra)", "RTT medio (ms) (Min-hop)",
                    "RTT/2 (ms) (Dijkstra)", "RTT/2 (ms) (Min-hop)",
                    "Distanza totale media (Dijkstra)", "Distanza totale media (Min-hop)"
                ])
            # Scrive una riga per ogni risultato medio salvato
            for res in self.avg_results:
                writer.writerow([
                    res["City1"],
                    res["City2"],
                    res["LISL_range"],
                    res["N. hop Dijkstra"],
                    res["N. hop MinHops"],
                    res["RTT medio (ms) Dijkstra"],
                    res["RTT medio (ms) MinHops"],
                    res["RTT/2 (ms) Dijkstra"],
                    res["RTT/2 (ms) MinHops"],
                    res["Distance totale media Dijkstra"],
                    res["Distance totale media MinHops"]
                ])

    def save_rtt_values_table_to_csv(self, city_names, satellite_rtt_list, terrestrial_rtt, filename="rtt_values.csv"):
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            # Scrittura dell'header
            writer.writerow(["City", "RTT Terrestre (ms)", "RTT Satellitare (ms)", "Gap (ms)"])
            # Per ogni città, salva la riga con i dati
            for i, city in enumerate(city_names):
                sat_rtt = satellite_rtt_list[i]
                gap = sat_rtt - terrestrial_rtt[i]
                writer.writerow([city, terrestrial_rtt[i], sat_rtt, gap])


    def save_graph_to_csv(graph):
        with open("nodes.csv", mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Satellite", "Latitudine", "Longitudine"])
            for node, data in graph.nodes(data=True):
                writer.writerow([node, data["lat"], data["lon"]])

        with open("edges.csv", mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Satellite1", "Satellite2", "Distanza_km"])
            for u, v, data in graph.edges(data=True):
                writer.writerow([u, v, data["weight"]])

    def save_map_as_png(filename="map.png"):
        plt.savefig(filename, dpi=600, bbox_inches='tight')
        print(f"Mappa salvata come {filename}")