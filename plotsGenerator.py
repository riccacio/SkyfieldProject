import matplotlib.pyplot as plt
import numpy as np

from data_handler import DataHandler


class PlotGenerator:
    def __init__(self):
        pass

    def plot_latency(self, LISL_range, dh, plusGrid):
        # Verifica che la lunghezza dei dati sia compatibile
        num_ranges = len(LISL_range)

        width = 0.2  # larghezza delle colonne
        x = np.arange(num_ranges)

        plt.figure(figsize=(10, 6))

        # Colonne per Dijkstra
        plt.bar(x - width * 1.5, dh.avg_half_rtt_d_list, width,
                label='RTT/2 Dijkstra', color='blue')
        plt.bar(x - width / 2, dh.avg_rtt_d_list, width,
                label='RTT Dijkstra', color='lightblue')

        # Colonne per MinHops
        plt.bar(x + width / 2, dh.avg_half_rtt_m_list, width,
                label='RTT/2 MinHops', color='red')
        plt.bar(x + width * 1.5, dh.avg_rtt_m_list, width,
                label='RTT MinHops', color='salmon')

        plt.xlabel("Range LISL (km)")
        plt.ylabel("Latenza (ms)")
        if plusGrid:
            plt.title("(+Grid) Confronto delle latenze RTT e RTT/2 medie per Dijkstra e MinHops\nal variare del range del laser")
        else:
            plt.title("(NO +Grid) Confronto delle latenze RTT e RTT/2 medie per Dijkstra e MinHops\nal variare del range del laser")

        plt.xticks(x, LISL_range)  # se LISL_range è già una lista di valori (o stringhe), basta usarla direttamente
        plt.legend()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()

    def plot_total_distance(self, LISL_range, dh, plusGrid):
        plt.figure(figsize=(10, 6))

        # Grafico per Dijkstra
        plt.plot(LISL_range, dh.avg_distance_d_list, marker='o', label="Dijkstra")
        # Grafico per MinHops
        plt.plot(LISL_range, dh.avg_distance_m_list, marker='s', label="MinHops")

        plt.xlabel("Range LISL (km)")
        plt.ylabel("Distanza Totale (km)")
        if plusGrid:
            plt.title("(+Grid) Confronto della Distanza Totale media del Percorso in funzione del Range LISL")
        else:
            plt.title("(NO +Grid) Confronto della Distanza Totale media del Percorso in funzione del Range LISL")
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()

    def plot_n_hop(self, LISL_range, dh, plusGrid):
        plt.figure(figsize=(10, 6))

        # Grafico per Dijkstra
        plt.plot(LISL_range, dh.avg_n_hops_d_list, marker='o', label="Dijkstra")
        # Grafico per MinHops
        plt.plot(LISL_range, dh.avg_n_hops_m_list, marker='s', label="MinHops")

        plt.xlabel("Range LISL (km)")
        plt.ylabel("Numero di salti")
        if plusGrid:
            plt.title("(+Grid) Confronto del Numero di salti medi del Percorso in funzione del Range LISL")
        else:
            plt.title("(NO +Grid) Confronto del Numero di salti medi del Percorso in funzione del Range LISL")
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()

    def plot_throughput(self, lisl_range_list, throughput_downlink_list, throughput_uplink_list, throughput_isl_list):
        """
        Disegna un grafico del throughput in funzione del LISL_range.

        Parametri:
          - lisl_range_list: lista dei valori di LISL_range (asse x)
          - throughput_downlink_list: lista dei throughput downlink (Gbps)
          - throughput_uplink_list: lista dei throughput uplink (Gbps)
          - throughput_isl_list: lista dei throughput ISL (Gbps)
        """
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

    def plot_latency_every_cities_vs_terrestrial(self, cities, rtt_list, rtt_terrestrial, plusGrid):
        # Crea vettore delle posizioni per ogni città
        x = np.arange(len(cities))
        width = 0.35  # Larghezza delle colonne

        plt.figure(figsize=(12, 6))

        # RTT Terrestre (arancione)
        plt.bar(x - width / 2, rtt_terrestrial, width=width, color='orange', label='RTT Terrestre')

        # RTT Satellitare (verde)
        plt.bar(x + width / 2, rtt_list, width=width, color='green', label='RTT Satellitare')

        # Personalizzazione etichette e titolo
        plt.xlabel("Città")
        plt.ylabel("RTT (ms)")
        if plusGrid:
            plt.title("(+Grid) RTT verso diverse città: Confronto Terrestre vs Satellitare")
        else:
            plt.title("(NO +Grid) RTT verso diverse città: Confronto Terrestre vs Satellitare")
        plt.xticks(x, cities, rotation=45)  # Nomi delle città inclinati per leggibilità
        plt.legend()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()  # Aggiusta automaticamente gli spazi

        # Mostra il grafico
        plt.show()