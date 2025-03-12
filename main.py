from skyfield.toposlib import Topos

import data_handler
import utils
from data_handler import DataHandler
from plotsGenerator import plotGenerator
from satellite_tracker import SatelliteTracker
from graph import SatelliteGraph
from visualization import SatelliteVisualization



"""
Vancouver:
- Latitudine: 49.2827° N
- Longitudine: 123.1207° W

Tokyo:
- Latitudine: 35.6895° N
- Longitudine: 139.6917° E

New York:
- Latitudine: 40.7128° N
- Longitudine: 74.0060° W

Londra:
- Latitudine: 51.5074° N
- Longitudine: 0.1278° W

Istanbul:
- Latitudine: 41.0082° N
- Longitudine: 28.9784° E

Sydney:
- Latitudine: 33.8688° S
- Longitudine: 151.2093° E

Bahrain:
- Latitudine: 26.2010° N
- Longitudine: 50.6070° E

Cape Town (Sudafrica):
- Latitudine: -33.9249° S
- Longitudine: 18.4241° E

Mumbai (India):
- Latitudine: 19.0760° N
- Longitudine: 72.8777° E

Northern California (ad esempio, San Francisco):
- Latitudine: 37.7749° N
- Longitudine: -122.4194° W

São Paulo (Brasile):
- Latitudine: -23.5505° S
- Longitudine: -46.6333° W

Singapore:
- Latitudine: 1.3521° N
- Longitudine: 103.8198° E
"""



city1_name = "Vancouver"
city2_name = "N. California"

#city1 = Topos(latitude_degrees=40.7128, longitude_degrees=-74.0060) # New York

city1 = Topos(latitude_degrees=49.2827, longitude_degrees=-123.1207) # Vancouver

#city2 = Topos(latitude_degrees=51.5074, longitude_degrees=-0.1278) # London
#city2 = Topos(latitude_degrees=26.2010, longitude_degrees=50.6070) # Bahrain
#city2 = Topos(latitude_degrees=-33.9249, longitude_degrees=18.4241) # Cape Town
#city2 = Topos(latitude_degrees=19.0760, longitude_degrees=72.8777) # Mumbai
city2 = Topos(latitude_degrees=37.7749, longitude_degrees=-122.4194) # N. California (San Francisco)
#city2 = Topos(latitude_degrees=-23.5505, longitude_degrees=-46.6333) # São Paulo
# = Topos(latitude_degrees=1.3521, longitude_degrees=103.8198) # Singapore
#city2 = Topos(latitude_degrees=41.0082, longitude_degrees=28.9784) # Istanbul
#city2 = Topos(latitude_degrees=-33.8688, longitude_degrees=151.2093) # Sydney
#city2 = Topos(latitude_degrees=35.6895, longitude_degrees=139.6917) # Tokyo

E_to_W = True # da est a ovest

tracker = SatelliteTracker(city1, city2, E_to_W)
satellites = tracker.filter_satellites()


print(f"Satelliti validi dentro il range: {len(satellites)}")
#tracker.count_orbital_planes()

start_node = tracker.find_satellite_more_close(city1.latitude.degrees , city1.longitude.degrees, satellites)
end_node = tracker.find_satellite_more_close(city2.latitude.degrees , city2.longitude.degrees, satellites)
print(f"Satellite più vicino a New York: {start_node[0]}"
      f"\nSatellite più vicino a Londra: {end_node[0]}")


"""
    LISL_range = 659.5, 1319, 1500, 1700, 2500, e 5016 km
"""
LISL_range = [659.5, 1319, 1500, 1700, 2500, 5016]
for range in LISL_range:
    sat_graph = SatelliteGraph(range)
    sat_graph.add_nodes(satellites)
    sat_graph.connect_nodes()
    print(f"Numero di nodi: {sat_graph.get_graph().number_of_nodes()}"
          f"\nNumero di archi: {sat_graph.get_graph().number_of_edges()}")


    data_handler.DataHandler.save_graph_to_csv(sat_graph.get_graph())

    # Calcola il cammino minimo tra i due satelliti più vicini alle città
    shortest_path = sat_graph.find_shortest_path(start_node[0], end_node[0])
    if shortest_path:
        print("Il percorso più breve è:", shortest_path)


    # Fattore di congestione
    congestion_factor = 0
    print(f"Fattore di congestione: {congestion_factor}")

    latency = sat_graph.calculate_total_latency(shortest_path, city1, city2, congestion_factor)

    rtt = 2 * latency * 1000 + (len(shortest_path) * 2)
    half_rtt = latency * 1000 + len(shortest_path)

    # considero che ogni dato che passa per un satellite ha 1 ms per essere elaborato
    #latency_onBoard = 0
    print(f"Latenza (RTT/2 , one-way): {half_rtt:.3f} ms")
    print(f"Latenza (RTT , two-way): {rtt:.3f} ms")

    # Paramentri per Laser
    P_t_laser = 1 # W, potenza trasmessa
    G_laser = 80  # dBi, guadagno
    lambda_laser = 1.55e-6  # m, lunghezza d'onda
    B_laser = 80e9  # Hz, larghezza di banda

    # Parametri per Downlink banda Ku
    P_t_ku = 50  # W, potenza trasmessa
    G_ku_dBi = 45  # dBi, guadagno
    lambda_ku = 0.0214  # m, lunghezza d'onda
    B_ku = 13e9  # Hz, larghezza di banda

    # Parametri per Uplink banda Ka
    P_t_ka = 30  # W, potenza trasmessa
    G_ka_dBi = 50  # dBi, guadagno
    lambda_ka = 0.011 # m, lunghezza d'onda
    B_ka = 20e9 # Hz, larghezza di banda

    # Conversione dei guadagni da dBi a valore lineare
    G_ku = 10**(G_ku_dBi / 10)
    G_ka = 10**(G_ka_dBi / 10)
    G_laser = 10**(G_laser / 10)

    downlink_ka, uplink_ku, isl_laser = sat_graph.calculate_total_throughput(
        shortest_path, city1, city2, congestion_factor,
        P_t_laser, G_laser, lambda_laser, B_laser,
        P_t_ka, G_ka, lambda_ka, B_ka,
        P_t_ku, G_ku, lambda_ku, B_ku
    )

    dh = DataHandler()

    dh.add_result(
        city1=city1_name,
        city2=city2_name,
        LISL_range=range,
        n_hop = len(shortest_path),
        half_rtt=half_rtt,
        rtt=rtt,
        throughput_downlink=downlink_ka,
        throughput_uplink=uplink_ku,
        throughput_isl=isl_laser
    )

    dh.save_results_to_csv("results.csv")
    """
    viz = SatelliteVisualization(city1_name, city2_name, city1, city2, sat_graph.get_graph(), satellites, start_node, end_node, E_to_W, False)
    viz.draw_map()
    #viz.plot_tracks() # disegna la traccia del satellite
    viz.add_cities()
    viz.plot_edges(shortest_path)
    viz.plot_nodes(shortest_path)
    viz.show(save_as_png=False)
    """

pg = plotGenerator()
rtt_list, half_rtt_list, throughput_downlink_list, throughput_uplink_list, throughput_isl_list = dh.get_results_lists()
pg.plot_latency(LISL_range, half_rtt_list, rtt_list)
pg.plot_throughput(LISL_range, throughput_downlink_list, throughput_uplink_list, throughput_isl_list)


