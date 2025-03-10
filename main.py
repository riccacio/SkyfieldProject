from skyfield.toposlib import Topos

from satellite_tracker import SatelliteTracker
from graph import SatelliteGraph
from visualization import SatelliteVisualization
from data_handler import save_graph_to_csv
"""

city1 = Topos(latitude_degrees=49.2827, longitude_degrees=-123.1207)  # Vancouver
city2 = Topos(latitude_degrees=35.6895, longitude_degrees=139.6917) # Tokyo
"""
"""
• New York City:
- Latitudine: 40.7128° N
- Longitudine: 74.0060° W

• Londra:
- Latitudine: 51.5074° N
- Longitudine: 0.1278° W
"""


city1 = Topos(latitude_degrees=40.7128, longitude_degrees=-74.006)  # New York
city2 = Topos(latitude_degrees=51.5074, longitude_degrees=-0.1278) # London


tracker = SatelliteTracker(city1, city2)
satellites = tracker.filter_satellites()


print(f"Satelliti validi dentro il range: {len(satellites)}")
#tracker.count_orbital_planes()

start_node = tracker.find_satellite_more_close(city1.latitude.degrees , city1.longitude.degrees, satellites)
end_node = tracker.find_satellite_more_close(city2.latitude.degrees , city2.longitude.degrees, satellites)
print(f"Satellite più vicino a New York: {start_node[0]}"
      f"\nSatellite più vicino a Londra: {end_node[0]}")

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
B = 1.92e9  # Larghezza di banda (12.5 GHz)
N = 1.25e-11  # Potenza del rumore (W)


latency = sat_graph.calculate_total_latency(shortest_path)
# considero che ogni dato che passa per un satellite ha 1 ms per essere elaborato
latency_onBoard = len(shortest_path)
print(f"Latenza (RTT/2 , one-way): {(latency*1000)+latency_onBoard:.3f} ms")
print(f"Latenza (RTT , two-way): {((latency*2)*1000)+latency_onBoard*2:.3f} ms")



# Esempio di parametri (valori medi ipotetici, da regolare in base a fonti affidabili):
isl_params = {
    'P_t': 0.5,  # Potenza trasmessa in Watt
    'G_t': 4.11e8,  # Guadagno trasmettitore (lineare, corrispondente a circa 86 dBi)
    'G_r': 4.11e8,  # Guadagno ricevitore (lineare)
    'lambda': 1550e-9,  # Lunghezza d'onda in metri (tipica per link laser ISL)
    'B': 12.5e9,  # Banda in Hz (12.5 GHz)
    'N': 1.25e-11  # Potenza del rumore in Watt
}

# Parametri per il link a terra in Ka band (valori di esempio)
ground_ka_params = {
    'P_t': 1.0,  # Potenza trasmessa in Watt (ipotetica)
    'G_t': 3e4,  # Guadagno trasmettitore (lineare)
    'G_r': 3e4,  # Guadagno ricevitore (lineare)
    'lambda': 0.015,  # Lunghezza d'onda in metri (circa 15 mm)
    'B': 1e9,  # Banda in Hz (1 GHz)
    'N': 1e-10  # Potenza del rumore in Watt
}

# Parametri per il link a terra in Ku band (valori di esempio)
ground_ku_params = {
    'P_t': 1.0,  # Potenza trasmessa in Watt (ipotetica)
    'G_t': 1e4,  # Guadagno trasmettitore (lineare)
    'G_r': 1e4,  # Guadagno ricevitore (lineare)
    'lambda': 0.025,  # Lunghezza d'onda in metri (circa 25 mm)
    'B': 1e9,  # Banda in Hz (1 GHz)
    'N': 1e-10  # Potenza del rumore in Watt
}




throughput = sat_graph.calculate_total_throughput(shortest_path, P_t, G_t, G_r, lambda_, B, N)
print(f"Throughput: {throughput:.3f} Gbps")


viz = SatelliteVisualization(city1, city2, sat_graph.get_graph(), satellites, start_node, end_node)
viz.draw_map()
#viz.plot_tracks() # disegna òa traccia del satellite
viz.add_cities()
viz.plot_edges(shortest_path)
viz.plot_nodes(shortest_path)
viz.show(save_as_png=False)