import csv
import os
import matplotlib.pyplot as plt

class DataHandler:
    def __init__(self):
        self.results = []
        self.rtt_list = []
        self.half_rtt_list = []
        self.throughput_downlink_list = []
        self.throughput_uplink_list = []
        self.throughput_isl_list = []

    def add_result(self, city1, city2, LISL_range, n_hop, half_rtt, rtt,
                   throughput_downlink, throughput_uplink, throughput_isl):

        result = {
            "City1": city1,
            "City2": city2,
            "LISL_range": LISL_range,
            "n_hop": n_hop,
            "RTT/2 (s)": half_rtt,
            "RTT (s)": rtt,
            "Throughput Downlink (Gbps)": throughput_downlink,
            "Throughput Uplink (Gbps)": throughput_uplink,
            "Throughput ISL (Gbps)": throughput_isl
        }

        self.rtt_list.append(rtt)
        self.half_rtt_list.append(half_rtt)
        self.throughput_downlink_list.append(throughput_downlink)
        self.throughput_uplink_list.append(throughput_uplink)
        self.throughput_isl_list.append(throughput_isl)
        self.results.append(result)

    def save_results_to_csv(self, filename):
        """
        Salva i risultati in un file CSV.
        Se il file non esiste, viene scritta anche l'intestazione.
        """
        file_exists = os.path.exists(filename)
        with open(filename, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                # Scrive l'header
                writer.writerow([
                    "City1", "City2", "LISL_range", "Numero di hop",
                    "RTT/2 (s)", "RTT (s)",
                    "Throughput Downlink (Gbps)",
                    "Throughput Uplink (Gbps)",
                    "Throughput ISL (Gbps)"
                ])
            for res in self.results:
                writer.writerow([
                    res["City1"],
                    res["City2"],
                    res["LISL_range"],
                    res["n_hop"],
                    res["RTT/2 (s)"],
                    res["RTT (s)"],
                    res["Throughput Downlink (Gbps)"],
                    res["Throughput Uplink (Gbps)"],
                    res["Throughput ISL (Gbps)"]
                ])

    def get_results_lists(self):
        return self.rtt_list, self.half_rtt_list, self.throughput_downlink_list, self.throughput_uplink_list, self.throughput_isl_list


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