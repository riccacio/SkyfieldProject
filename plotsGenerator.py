import matplotlib.pyplot as plt
import numpy as np

class PlotGenerator:
    def __init__(self):
        pass

    def plot_latency(self, LISL_range, dh, plusGrid):
        num_ranges = len(LISL_range)

        width = 0.2  # larghezza delle colonne
        x = np.arange(num_ranges)

        plt.figure(figsize=(10, 6))

        # Solo colonne per RTT/2
        plt.bar(x - width / 2, dh.avg_half_rtt_d_list, width,
                label='RTT/2 Dijkstra', color='blue')
        plt.bar(x + width / 2, dh.avg_half_rtt_m_list, width,
                label='RTT/2 MinHop', color='orange')

        plt.xlabel("Range LISL (km)")
        plt.ylabel("Latenza (ms)")
        if plusGrid:
            plt.title(
                "(+Grid) Confronto delle latenze RTT/2 medie per Dijkstra e MinHop\nal variare del range del laser")
        else:
            plt.title(
                "(Libera) Confronto delle latenze RTT/2 medie per Dijkstra e MinHop\nal variare del range del laser")

        plt.xticks(x, LISL_range)
        plt.legend()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()

    def plot_total_distance(self, LISL_range, dh, plusGrid):
        plt.figure(figsize=(10, 6))

        # Grafico per Dijkstra
        plt.plot(LISL_range, dh.avg_distance_d_list, marker='o', label="Dijkstra")
        # Grafico per MinHop
        plt.plot(LISL_range, dh.avg_distance_m_list, marker='s', label="MinHop")

        plt.xlabel("Range LISL (km)")
        plt.ylabel("Distanza Totale (km)")
        if plusGrid:
            plt.title("(+Grid) Confronto della Distanza Totale media del Percorso in funzione del Range LISL")
        else:
            plt.title("(Libera) Confronto della Distanza Totale media del Percorso in funzione del Range LISL")
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()

    def plot_n_hop(self, LISL_range, dh, plusGrid):
        plt.figure(figsize=(10, 6))

        # Grafico per Dijkstra
        plt.plot(LISL_range, dh.avg_n_hops_d_list, marker='o', label="Dijkstra")
        # Grafico per MinHop
        plt.plot(LISL_range, dh.avg_n_hops_m_list, marker='s', label="MinHop")

        plt.xlabel("Range LISL (km)")
        plt.ylabel("Numero di salti")
        if plusGrid:
            plt.title("(+Grid) Confronto del Numero di salti medi del Percorso in funzione del Range LISL")
        else:
            plt.title("(Libera) Confronto del Numero di salti medi del Percorso in funzione del Range LISL")
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()
    """
    def plot_throughput(self, lisl_range_list, throughput_downlink_list, throughput_uplink_list, throughput_isl_list):

        plt.figure(figsize=(8, 6))
        plt.plot(lisl_range_list, throughput_downlink_list, marker='o', linestyle='-', color='green',
                 label='Throughput Downlink (Gbps)')
        plt.plot(lisl_range_list, throughput_uplink_list, marker='s', linestyle='--', color='orange',
                 label='Throughput Uplink (Gbps)')
        plt.plot(lisl_range_list, throughput_isl_list, marker='^', linestyle='-.', color='purple',
                 label='Throughput ISL (Gbps)')
        plt.xlabel("LISL_range (km)")
        plt.ylabel("Throughput (Gbps)")
        plt.title("Throughput in funzione del LISL_range")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    """

    def plot_latency_every_cities_vs_terrestrial(self, cities, rtt_list, rtt_terrestrial, plusGrid):

        x = np.arange(len(cities))
        width = 0.35  # Larghezza delle colonne

        plt.figure(figsize=(12, 6))

        # RTT Terrestre (arancione)
        plt.bar(x - width / 2, rtt_terrestrial, width=width, color='grey', label='RTT Terrestre')

        # RTT Satellitare (verde)
        plt.bar(x + width / 2, rtt_list, width=width, color='lightblue', label='RTT Satellitare')


        plt.xlabel("Città", fontsize=14)
        plt.ylabel("RTT (ms)", fontsize=14)
        if plusGrid:
            plt.title("(+Grid) RTT verso diverse città: Confronto Terrestre vs Satellitare", fontsize=14)
        else:
            plt.title("(Libera) RTT verso diverse città: Confronto Terrestre vs Satellitare", fontsize=14)
        plt.xticks(x, cities, rotation=45, fontsize=16)  # Rotazione nomi delle città per leggibilità
        plt.legend(fontsize=14)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()  # Aggiusta automaticamente gli spazi

        plt.show()

    def plot_violin_distance_distribution(self, dh):
        dijkstra_data = {}
        minhop_data = {}

        for d in dh.dict_results_d:
            r = d["Range"]
            if r not in dijkstra_data:
                dijkstra_data[r] = []
            dijkstra_data[r].append(d["Distance"])

        for m in dh.dict_results_m:
            r = m["Range"]
            if r not in minhop_data:
                minhop_data[r] = []
            minhop_data[r].append(m["Distance"])

        # Ordina i range per coerenza visiva
        sorted_ranges = sorted(set(dijkstra_data.keys()) | set(minhop_data.keys()))

        # --- Grafico Dijkstra ---
        dijkstra_values = [dijkstra_data[r] for r in sorted_ranges]
        print(dijkstra_values)
        dijkstra_labels = [str(r) for r in sorted_ranges]

        plt.figure(figsize=(10, 5))
        parts = plt.violinplot(dijkstra_values, showmeans=False, showextrema=True, showmedians=True)
        plt.xticks(range(1, len(dijkstra_labels) + 1), dijkstra_labels)
        plt.title("Distribuzione Distanze Totali - Dijkstra")
        plt.xlabel("Range del Laser (km)")
        plt.ylabel("Distanza Totale (km)")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

        # --- Grafico MinHops ---
        minhop_values = [minhop_data[r] for r in sorted_ranges]
        minhop_labels = [str(r) for r in sorted_ranges]

        plt.figure(figsize=(10, 5))
        parts = plt.violinplot(minhop_values, showmeans=False, showextrema=True, showmedians=True)

        for pc in parts['bodies']:
            pc.set_facecolor('orange')
            pc.set_alpha(0.5)

        plt.xticks(range(1, len(minhop_labels) + 1), minhop_labels)
        plt.title("Distribuzione Distanze Totali - MinHop")
        plt.xlabel("Range del Laser (km)")
        plt.ylabel("Distanza Totale (km)")
        plt.grid(True)
        plt.tight_layout()
        plt.show()