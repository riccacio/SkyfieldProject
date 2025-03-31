import csv
import os
import matplotlib.pyplot as plt

import utils


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


        self.dict_results_d = []
        self.dict_results_m = []

        self.dict_distance_d = {}
        self.dict_distance_m = {}


    def add_result(self, range, n_hop_d, n_hop_m, half_rtt_d, half_rtt_m, distance_d,
                   distance_m):

        self.half_rtt_d_list.append(half_rtt_d)
        self.half_rtt_m_list.append(half_rtt_m)
        self.n_hops_d_list.append(n_hop_d)
        self.n_hops_m_list.append(n_hop_m)
        self.distance_d_list.append(distance_d)
        self.distance_m_list.append(distance_m)

        self.dict_distance_d = {
            "Range": range,
            "Distance" : distance_d
        }

        self.dict_distance_m = {
            "Range": range,
            "Distance": distance_m
        }

        self.dict_results_d.append(self.dict_distance_d)
        self.dict_results_m.append(self.dict_distance_m)


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
                       avg_half_rtt_d, avg_half_rtt_m,
                       avg_distance_d, avg_distance_m):

        avg_result = {
            "City1": city1,
            "City2": city2,
            "LISL_range": LISL_range,
            "N. hop Dijkstra": utils.round_sig(avg_n_hop_d, 3),
            "N. hop MinHops": utils.round_sig(avg_n_hop_m, 3),
            "RTT/2 (ms) Dijkstra": utils.round_sig(avg_half_rtt_d, 6),
            "RTT/2 (ms) MinHops": utils.round_sig(avg_half_rtt_m, 6),
            "Distance totale media Dijkstra": utils.round_sig(avg_distance_d, 6),
            "Distance totale media MinHops": utils.round_sig(avg_distance_m, 6)
        }
        self.avg_results.append(avg_result)
        self.avg_half_rtt_d_list.append(avg_half_rtt_d)
        self.avg_half_rtt_m_list.append(avg_half_rtt_m)
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
                gap = utils.round_sig(gap, 5)
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