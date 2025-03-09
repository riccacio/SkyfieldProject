from skyfield.toposlib import Topos

from satellite_tracker import SatelliteTracker
from graph import SatelliteGraph
from visualization import SatelliteVisualization
from data_handler import save_graph_to_csv

city1 = Topos(latitude_degrees=49.2827, longitude_degrees=-123.1207)  # Vancouver
city2 = Topos(latitude_degrees=35.6895, longitude_degrees=139.6917) # Tokyo

tracker = SatelliteTracker()
satellites = tracker.filter_satellites()

print(f"Satelliti validi dentro il range: {len(satellites)}")

start_node = tracker.find_satellite_more_close(city1.latitude.degrees , city1.longitude.degrees, satellites)
end_node = tracker.find_satellite_more_close(city2.latitude.degrees , city2.longitude.degrees, satellites)
print(f"Satellite più vicino a Vancouver: {start_node[0]}"
      f"\nSatellite più vicino a Tokyo: {end_node[0]}")

sat_graph = SatelliteGraph()
sat_graph.add_nodes(satellites)
sat_graph.connect_nodes()
print(f"Numero di nodi: {sat_graph.get_graph().number_of_nodes()}"
      f"\nNumero di archi: {sat_graph.get_graph().number_of_edges()}")
save_graph_to_csv(sat_graph.get_graph())

# Calcola il cammino minimo tra i due satelliti più vicini alle città
shortest_path = sat_graph.find_shortest_path(start_node[0], end_node[0])
if shortest_path:
    print("Il percorso più breve è:", shortest_path)


# Parametri del collegamento laser
P_t = 0.5  # Potenza trasmessa (Watt)
G_t = 4.11e8  # Guadagno trasmettitore (circa 86 dBi)
G_r = 4.11e8  # Guadagno ricevitore (circa 86 dBi)
lambda_ = 1550e-9  # Lunghezza d'onda (1550 nm)
B = 12.5e9  # Larghezza di banda (12.5 GHz)
N = 1.25e-11  # Potenza del rumore (W)


latency = sat_graph.calculate_total_latency(shortest_path)
print(f"Latenza (RTT/2 , one-way): {latency*1000:.3f} ms")
print(f"Latenza (RTT , two-way): {(latency*2)*1000:.3f} ms")

throughput = sat_graph.calculate_total_throughput(shortest_path, P_t, G_t, G_r, lambda_, B, N)
print(f"Throughput: {throughput:.3f} Gbps")


viz = SatelliteVisualization(city1, city2, sat_graph.get_graph(), satellites, start_node, end_node)
viz.draw_map()
#viz.plot_tracks() # disegna òa traccia del satellite
viz.add_cities()
viz.plot_edges(shortest_path)
viz.plot_nodes(shortest_path)
viz.show(save_as_png=False)