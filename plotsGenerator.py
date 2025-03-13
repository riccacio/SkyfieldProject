import matplotlib.pyplot as plt


class PlotGenerator:
    def __init__(self):
        # Puoi eventualmente aggiungere parametri per personalizzare lo stile
        pass

    def plot_latency(self, lisl_range_list, rtt_half_list, rtt_list):
        """
        Disegna un grafico della latenza in funzione del LISL_range.

        Parametri:
          - lisl_range_list: lista dei valori di LISL_range (asse x)
          - rtt_half_list: lista dei valori di RTT/2 (one-way latency) in secondi
          - rtt_list: lista dei valori di RTT (round-trip time) in secondi
        """
        plt.figure(figsize=(8, 6))
        plt.plot(lisl_range_list, [x  for x in rtt_half_list], marker='o', linestyle='-', color='blue',
                 label='RTT/2 (ms)')
        plt.plot(lisl_range_list, [x  for x in rtt_list], marker='s', linestyle='--', color='red',
                 label='RTT (ms)')
        plt.xlabel("LISL_range (km)")
        plt.ylabel("Latenza (ms)")
        plt.title("Latenza (RTT/2 e RTT) in funzione del LISL_range")
        plt.legend()
        plt.grid(True)
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

    def plot_latency_every_cities(self, cities, rtt_list):
        # Creazione del grafico a colonne
        plt.figure(figsize=(10, 5))  # Imposta la dimensione della figura
        plt.bar(cities, rtt_list, color='blue', width=0.4)  # Crea il bar chart

        # Etichette e titolo
        plt.xlabel("Città")
        plt.ylabel("RTT (ms)")
        plt.title("RTT verso diverse città")
        plt.xticks(rotation=45)  # Ruota i nomi delle città per leggibilità

        # Mostra il grafico
        plt.show()
