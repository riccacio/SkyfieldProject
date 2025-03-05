from skyfield.toposlib import Topos

from satellite_tracker import SatelliteTracker
from graph import SatelliteGraph
from visualization import SatelliteVisualization
from data_handler import save_graph_to_csv

city1 = Topos(latitude_degrees=49.2827, longitude_degrees=-123.1207)  # Vancouver
city2 = Topos(latitude_degrees=35.6762, longitude_degrees=139.6503) # Tokyo

tracker = SatelliteTracker()
satellites = tracker.filter_satellites()
print(f"Satelliti validi dentro il range: {len(satellites)}")

start_node = tracker.find_satellite_more_close(city1.latitude.degrees , city1.longitude.degrees, satellites)
end_node = tracker.find_satellite_more_close(city2.latitude.degrees , city2.longitude.degrees, satellites)

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

viz = SatelliteVisualization(city1, city2, sat_graph.get_graph(), satellites, start_node, end_node)
viz.draw_map()
#viz.plot_tracks() # disegna òa traccia del satellite
viz.add_cities()
viz.plot_edges(shortest_path)
viz.plot_nodes()
viz.show(save_as_png=False)