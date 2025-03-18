import os

from matplotlib import pyplot as plt

from data_handler import DataHandler
from satellite_tracker import SatelliteTracker
from graph import SatelliteGraph
from visualization import SatelliteVisualization
from plotsGenerator import PlotGenerator

class Test:
    def __init__(self):
        self.dh = DataHandler()
        self.pg = PlotGenerator()

    def test_city_pair_with_lisl_range(self, city1_name, city1, city2_name, city2, E_to_W, LISL_range):
        """
        Testa la comunicazione tra due città variando il LISL_range.
        """
        desktop_folder = os.path.join(os.path.expanduser("~"), "Desktop", "MyPlots")
        os.makedirs(desktop_folder, exist_ok=True)

        for range_value in LISL_range:
            print(f"\nTest tra {city1_name} e {city2_name} con LISL_range: {range_value} km")
            for i in range(0, 5):
                tracker = SatelliteTracker(city1, city2, E_to_W)
                satellites = tracker.filter_satellites()

                print(f"Satelliti validi dentro il range: {len(satellites)}")

                start_node = tracker.find_satellite_more_close(city1.latitude.degrees, city1.longitude.degrees, satellites)
                end_node = tracker.find_satellite_more_close(city2.latitude.degrees, city2.longitude.degrees, satellites)

                print(f"Satellite più vicino a {city1_name}: {start_node[0]}"
                      f"\nSatellite più vicino a {city2_name}: {end_node[0]}")

                sat_graph = SatelliteGraph(range_value)
                sat_graph.add_nodes(satellites)
                #sat_graph.connect_nodes_plus_grid()
                #sat_graph.connect_nodes()
                sat_graph.connect_nodes_hybrid()

                print(f"Numero di nodi: {sat_graph.get_graph().number_of_nodes()}"
                      f"\nNumero di archi: {sat_graph.get_graph().number_of_edges()}")

                DataHandler.save_graph_to_csv(sat_graph.get_graph())

                # Calcola il percorso più breve con dijkstra
                shortest_path_dijkstra = sat_graph.find_shortest_path_Dijkstra(start_node[0], end_node[0])
                if shortest_path_dijkstra:
                    print("Il percorso più breve è:", shortest_path_dijkstra)

                # Calcola il percorso più breve con min hop count
                shortest_path_minHops = sat_graph.find_shortest_path_minHop(start_node[0], end_node[0])
                if shortest_path_minHops:
                    print("Il percorso più breve è:", shortest_path_minHops)
                    print(f"Con {len(shortest_path_minHops)-1} salti")

                # Calcola la latenza RTT
                load_factor = 0
                latency = sat_graph.calculate_total_latency(shortest_path_dijkstra, city1, city2, load_factor)
                rtt = 2 * latency * 1000 + (len(shortest_path_dijkstra) * 2)
                half_rtt = latency * 1000 + len(shortest_path_dijkstra)

                print(f"Latenza RTT/2: {half_rtt:.3f} ms, RTT: {rtt:.3f} ms")

                load_factor = 0
                latency = sat_graph.calculate_total_latency(shortest_path_minHops, city1, city2, load_factor)
                rtt = 2 * latency * 1000 + (len(shortest_path_minHops) * 2)
                half_rtt = latency * 1000 + len(shortest_path_minHops)

                print(f"Latenza RTT/2: {half_rtt:.3f} ms, RTT: {rtt:.3f} ms")

                """
                    # Parametri dei segnali
                    params = {
                        "P_t_laser": 1, "G_laser": 80, "lambda_laser": 1.55e-6, "B_laser": 80e9,
                        "P_t_ku": 50, "G_ku_dBi": 45, "lambda_ku": 0.0214, "B_ku": 13e9,
                        "P_t_ka": 30, "G_ka_dBi": 50, "lambda_ka": 0.011, "B_ka": 20e9
                    }
        
                    # converto i guadagni
                    params["G_ku"] = 10 ** (params["G_ku_dBi"] / 10)
                    params["G_ka"] = 10 ** (params["G_ka_dBi"] / 10)
                    params["G_laser"] = 10 ** (params["G_laser"] / 10)
        
                    downlink_ka, uplink_ku, isl_laser = sat_graph.calculate_total_throughput(
                        shortest_path, city1, city2, load_factor,
                        params["P_t_laser"], params["G_laser"], params["lambda_laser"], params["B_laser"],
                        params["P_t_ka"], params["G_ka"], params["lambda_ka"], params["B_ka"],
                        params["P_t_ku"], params["G_ku"], params["lambda_ku"], params["B_ku"]
                    )
        
                    
                    self.dh.add_result(city1_name, city2_name, range_value, len(shortest_path), half_rtt, rtt,
                                  downlink_ka, uplink_ku, isl_laser)
                """
                self.dh.save_results_to_csv("results.csv")


                # visualizzazione della mappa, mostra tutti i collegamenti solo per range_value di 659.5 km
                viz = SatelliteVisualization(city1_name, city2_name, city1, city2, sat_graph.get_graph(),
                                             satellites, start_node, end_node, E_to_W, False)
                viz.draw_map()
                viz.add_cities()
                viz.plot_edges(shortest_path_dijkstra, shortest_path_minHops, range_value)
                viz.plot_nodes(shortest_path_dijkstra)

                # Genera il nome file unico per questa iterazione
                filename = os.path.join(desktop_folder, f"myplot{i + 1}.png")

                # Se il metodo show() non supporta direttamente il salvataggio, puoi
                # richiamare plt.savefig() subito dopo aver disegnato la figura.
                # Ad esempio, se viz.show() chiama plt.show() alla fine, puoi fare:
                plt.savefig(filename)
                print(f"Plot salvato in: {filename}")

                # Se preferisci visualizzare anche il plot, puoi chiamare plt.show()
                # oppure chiudere la figura per evitare conflitti nelle iterazioni successive:
                plt.close()


                #viz.show(save_as_png=False)




        rtt_list, half_rtt_list, throughput_downlink_list, throughput_uplink_list, throughput_isl_list = self.dh.get_results_lists()
        self.pg.plot_latency(LISL_range, half_rtt_list, rtt_list)
        self.pg.plot_throughput(LISL_range, throughput_downlink_list, throughput_uplink_list, throughput_isl_list)


    def test_multiple_cities_with_fixed_lisl(self, city1_name, city1, cities, fixed_LISL):
        """
        Calcolo dell'RTT per più città con un LISL_range fisso.
        """

        for city2_name, city2, E_to_W in cities:
            print(f"\nTest con LISL {fixed_LISL} km tra {city1_name} e {city2_name}")

            tracker = SatelliteTracker(city1, city2, E_to_W)
            satellites = tracker.filter_satellites()

            print(f"Satelliti validi dentro il range: {len(satellites)}")

            sat_graph = SatelliteGraph(fixed_LISL)
            sat_graph.add_nodes(satellites)
            sat_graph.connect_nodes()

            print(f"Numero di nodi: {sat_graph.get_graph().number_of_nodes()}"
                  f"\nNumero di archi: {sat_graph.get_graph().number_of_edges()}")


            start_node = tracker.find_satellite_more_close(city1.latitude.degrees, city1.longitude.degrees, satellites)
            end_node = tracker.find_satellite_more_close(city2.latitude.degrees, city2.longitude.degrees, satellites)


            print(f"Satellite più vicino a {city1_name}: {start_node[0]}"
                  f"\nSatellite più vicino a {city2_name}: {end_node[0]}")

            shortest_path = sat_graph.find_shortest_path_Dijkstra(start_node[0], end_node[0])
            if shortest_path:
                print("Il percorso più breve è:", shortest_path)

            load_factor=0
            latency = sat_graph.calculate_total_latency(shortest_path, city1, city2, load_factor)
            rtt = 2 * latency * 1000 + (len(shortest_path) * 2)

            print(f"RTT: {rtt:.3f} ms")

            self.dh.add_rtt_value(rtt)

        # Generazione grafico
        self.pg.plot_latency_every_cities([c[0] for c in cities], self.dh.get_rtt_values())
