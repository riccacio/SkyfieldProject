import os
from datetime import timedelta

from matplotlib import pyplot as plt
from skyfield.api import load

import utils
from data_handler import DataHandler
from satellite_tracker import SatelliteTracker
from graph import SatelliteGraph
from visualization import SatelliteVisualization
from plotsGenerator import PlotGenerator

class Test:
    def __init__(self):
        self.dh = DataHandler()
        self.pg = PlotGenerator()

    def test_city_pair_with_lisl_range(self, city1_name, city1, city2_name, city2, E_to_W, LISL_range, plusGrid, load_factor):
        """
        Testa la comunicazione tra due città variando il LISL_range.
        """
        desktop_folder = os.path.join(os.path.expanduser("~"), "Desktop", "MyPlots")
        os.makedirs(desktop_folder, exist_ok=True)

        ts = load.timescale()

        n_simulations = 5 # minuti di simulazione ogni range
        j=1
        for range_value in LISL_range:
            current_start_time = ts.utc(2025, 2, 10, 12, 00, 00)  # Inizia da 10/02/2025 12:00:00
            self.dh.reset_avg_values()
            print(f"\nTest tra {city1_name} e {city2_name} con LISL_range: {range_value} km")
            for i in range(0, n_simulations):
                print(f"Ora simulazione: {current_start_time.utc_datetime()}")
                tracker = SatelliteTracker(city1, city2, current_start_time, E_to_W)
                satellites = tracker.filter_satellites()

                print(f"Satelliti validi dentro il range: {len(satellites)}")

                start_node = tracker.find_satellite_more_close(city1.latitude.degrees, city1.longitude.degrees, satellites)
                end_node = tracker.find_satellite_more_close(city2.latitude.degrees, city2.longitude.degrees, satellites)

                print(f"Satellite più vicino a {city1_name}: {start_node[0]}"
                      f"\nSatellite più vicino a {city2_name}: {end_node[0]}")

                sat_graph = SatelliteGraph(range_value)
                sat_graph.add_nodes(satellites)

                if plusGrid:
                    print("Connessione con topologia +Grid")
                    sat_graph.connect_nodes_hybrid()
                else:
                    print("Connessione con topologia libera")
                    sat_graph.connect_nodes()

                print(f"Numero di nodi: {sat_graph.get_graph().number_of_nodes()}"
                      f"\nNumero di archi: {sat_graph.get_graph().number_of_edges()}")

                DataHandler.save_graph_to_csv(sat_graph.get_graph())

                # Calcola il percorso più breve con dijkstra
                shortest_path_dijkstra, distance_d = sat_graph.find_shortest_path_Dijkstra(start_node[0], end_node[0])
                if shortest_path_dijkstra:
                    print("Il percorso più breve è:", shortest_path_dijkstra)
                    print("Con distanza totale: ", distance_d)

                # Calcola il percorso più breve con min hop count
                shortest_path_minHops, distance_m = sat_graph.find_shortest_path_minHop(start_node[0], end_node[0])
                if shortest_path_minHops:
                    print("Il percorso più breve è:", shortest_path_minHops)
                    print("Con distanza totale: ", distance_m)


                print("Fattore di carico: ", load_factor)

                if shortest_path_dijkstra is not None or shortest_path_minHops is not None:
                    n_hops_d = len(shortest_path_dijkstra) - 1

                    # Calcolo di RTT e RTT/2 con dijkstra
                    latency_d = sat_graph.calculate_total_latency(shortest_path_dijkstra, city1, city2, load_factor)
                    half_rtt_d = latency_d * 1000 + (n_hops_d+1)

                    print(f"Latenza con Dijkstra RTT/2: {half_rtt_d:.3f} ms")

                    # Calcolo di RTT e RTT/2 con min hop count
                    n_hops_m = len(shortest_path_minHops) - 1
                    latency_m = sat_graph.calculate_total_latency(shortest_path_minHops, city1, city2, load_factor)
                    half_rtt_m = latency_m * 1000 + (n_hops_m+1)

                    print(f"Latenza con Min Hops RTT/2: {half_rtt_m:.3f} ms")

                else:
                    print("Percorso non trovato")
                    n_hops_d = 0
                    n_hops_m = 0
                    half_rtt_d = 0
                    half_rtt_m = 0


                #self.dh.add_result(range_value, n_hops_d, n_hops_m, half_rtt_d, rtt_d, half_rtt_m, rtt_m, distance_d, distance_m)
                self.dh.add_result(range_value, n_hops_d, n_hops_m, half_rtt_d, half_rtt_m, distance_d, distance_m)

                #self.dh.save_results_to_csv("results.csv")


                # visualizzazione della mappa, mostra tutti i collegamenti solo per range_value di 659.5 km
                #viz = SatelliteVisualization(city1_name, city2_name, city1, city2, sat_graph.get_graph(),
                                            #satellites, start_node, end_node, E_to_W, False, plusGrid)
                #viz.draw_map()
                #viz.add_cities()
                #viz.plot_edges(shortest_path_dijkstra, shortest_path_minHops, range_value)
                #viz.plot_nodes(shortest_path_dijkstra)

                #viz.show(save_as_png=False)


                # Genera il nome file unico per questa iterazione
                #filename = os.path.join(desktop_folder, f"myplot{j}.png")

                # Se il metodo show() non supporta direttamente il salvataggio, puoi
                # richiamare plt.savefig() subito dopo aver disegnato la figura.
                # Ad esempio, se viz.show() chiama plt.show() alla fine, puoi fare:
                #plt.savefig(filename, dpi=600)
                #print(f"Plot salvato in: {filename}")

                # Se preferisci visualizzare anche il plot, puoi chiamare plt.show()
                # oppure chiudere la figura per evitare conflitti nelle iterazioni successive:
                #plt.close()

                current_start_time += timedelta(minutes=5)
                j += 1

            rtt_d_list, half_rtt_d_list, rtt_m_list , half_rtt_m_list, n_hops_d_list, n_hops_m_list, distance_d_list, distance_m_list = self.dh.get_results_lists()


            avg_half_rtt_d = sum(half_rtt_d_list) / n_simulations
            avg_half_rtt_m = sum(half_rtt_m_list) / n_simulations
            avg_distance_d = sum(distance_d_list) / n_simulations
            avg_distance_m = sum(distance_m_list) / n_simulations
            avg_n_hop_d = sum(n_hops_d_list) / n_simulations
            avg_n_hop_m = sum(n_hops_m_list) / n_simulations

            self.dh.add_avg_result(city1_name, city2_name, range_value,
                                   avg_n_hop_d, avg_n_hop_m,
                                   avg_half_rtt_d, avg_half_rtt_m,
                                   avg_distance_d, avg_distance_m)


            print (f"RTT/2 medio Dijkstra: {avg_half_rtt_d:.3f} ms")
            print (f"RTT/2 medio MinHops: {avg_half_rtt_m:.3f} ms")
            print (f"Numero di salti medio Dijkstra: {avg_n_hop_d:.2f}")
            print (f"Numero di salti medio MinHops: {avg_n_hop_m:.2f}")
            print(f"Distanza totale media Dijkstra: {avg_distance_d:.3f} km")
            print(f"Distanza totale media MinHops: {avg_distance_m:.3f} km")



        self.dh.save_results_to_csv("results.csv")
        self.pg.plot_latency(LISL_range, self.dh, plusGrid)
        self.pg.plot_total_distance(LISL_range, self.dh, plusGrid)
        self.pg.plot_n_hop(LISL_range, self.dh, plusGrid)
        self.pg.plot_violin_distance_distribution(self.dh)
        #self.pg.plot_throughput(LISL_range, throughput_downlink_list, throughput_uplink_list, throughput_isl_list)


    def test_multiple_cities_with_fixed_lisl(self, city1_name, city1, cities, fixed_LISL, rtt_terrestrial, plusGrid, load_factor):
        """
        Calcolo dell'RTT per più città con un LISL_range fisso.
        """
        desktop_folder = os.path.join(os.path.expanduser("~"), "Desktop", "MyPlots2")
        os.makedirs(desktop_folder, exist_ok=True)

        ts = load.timescale()


        avg_rtt_list = []

        n_simulations = 5  # minuti di simulazione ogni minuto

        for city2_name, city2, E_to_W in cities:
            current_start_time = ts.utc(2025, 2, 10, 12, 00, 00)  # Inizia da 15/02/2025 12:00:00
            self.dh.reset_rtt_values()
            print(f"\nTest con LISL {fixed_LISL} km tra {city1_name} e {city2_name}")

            for i in range(0, n_simulations):
                tracker = SatelliteTracker(city1, city2, current_start_time, E_to_W)
                satellites = tracker.filter_satellites()

                print(f"Satelliti validi dentro il range: {len(satellites)}")

                sat_graph = SatelliteGraph(fixed_LISL)
                sat_graph.add_nodes(satellites)


                if plusGrid:
                    print("Connessione con topologia +Grid")
                    sat_graph.connect_nodes_hybrid()
                else:
                    print("Connessione con topologia libera")
                    sat_graph.connect_nodes()


                print(f"Numero di nodi: {sat_graph.get_graph().number_of_nodes()}"
                      f"\nNumero di archi: {sat_graph.get_graph().number_of_edges()}")


                start_node = tracker.find_satellite_more_close(city1.latitude.degrees, city1.longitude.degrees, satellites)
                end_node = tracker.find_satellite_more_close(city2.latitude.degrees, city2.longitude.degrees, satellites)


                print(f"Satellite più vicino a {city1_name}: {start_node[0]}"
                      f"\nSatellite più vicino a {city2_name}: {end_node[0]}")

                # Calcola il percorso più breve con dijkstra
                shortest_path_dijkstra, _ = sat_graph.find_shortest_path_Dijkstra(start_node[0], end_node[0])
                if shortest_path_dijkstra:
                    print("Il percorso più breve è:", shortest_path_dijkstra)

                print("Fattore di carico: ", load_factor)
                if shortest_path_dijkstra is not None:
                    latency = sat_graph.calculate_total_latency(shortest_path_dijkstra, city1, city2, load_factor)
                    rtt = 2 * latency * 1000 + (len(shortest_path_dijkstra) * 2)

                    print(f"RTT: {rtt:.3f} ms")
                else:
                    print("Percorso non trovato")
                    rtt = 0

                self.dh.add_rtt_value(rtt)
                current_start_time += timedelta(minutes=5)

            avg_rtt = sum(self.dh.get_rtt_values()) / n_simulations
            print(f"RTT medio tra {city1_name} e {city2_name}: {avg_rtt:.3f} ms")
            avg_rtt_list.append(utils.round_sig(avg_rtt, 5))

        """
        avg_rtt_list = [160.520,
                        299.811,
                        245.360,
                        51.347,
                        253.272,
                        254.141,
                        245.390,
                        173.262]
        """

        #avg_rtt_list = [103.190, 189.474, 156.058, 23.673, 131.471, 149.612, 146.168, 92.775]
        # Generazione grafico
        self.dh.save_rtt_values_table_to_csv([c[0] for c in cities], avg_rtt_list, rtt_terrestrial)
        self.pg.plot_latency_every_cities_vs_terrestrial([c[0] for c in cities], avg_rtt_list, rtt_terrestrial, plusGrid)
