import matplotlib
matplotlib.use('MacOSX')  # Forza il backend nativo per macOS
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from skyfield.toposlib import Topos
from data_handler import save_map_as_png


class SatelliteVisualization:

    def __init__(self, graph):
        """Inizializza la visualizzazione con il grafo."""
        self.graph = graph

        mng = plt.get_current_fig_manager()
        mng.full_screen_toggle()

        self.m = Basemap(projection='merc',
                        llcrnrlat=10, urcrnrlat=65,
                        llcrnrlon=110, urcrnrlon=260,
                        resolution='i')


    def add_cities(self):
        vancouver = Topos(latitude_degrees=49.2827, longitude_degrees=-123.1207)  # Vancouver
        tokyo = Topos(latitude_degrees=35.6762, longitude_degrees=139.6503)  # Tokyo

        # estraggo latitudine e longitudine delle città
        vancouver_lat = vancouver.latitude.degrees
        vancouver_lon = vancouver.longitude.degrees
        tokyo_lat = tokyo.latitude.degrees
        tokyo_lon = tokyo.longitude.degrees

        if vancouver_lon < 0:
            vancouver_lon += 360

        if tokyo_lon < 0:
            tokyo_lon += 360

        cities = [
            {'name': 'Vancouver', 'lat': vancouver_lat, 'lon': vancouver_lon, 'color': 'orange'},
            {'name': 'Tokyo', 'lat': tokyo_lat, 'lon': tokyo_lon, 'color': 'green'}
        ]

        for city in cities:
            x, y = self.m(city['lon'], city['lat'])  # Converte le coordinate in coordinate della mappa
            self.m.plot(x, y, marker='o', color=city['color'], markersize=6, label=city['name'])

    def draw_map(self):
        """Disegna la mappa di base."""
        self.m.drawcoastlines()
        self.m.drawcountries()

        parallels = range(-20, 71, 10)  # Intervallo ogni 10 gradi
        self.m.drawparallels(parallels, labels=[True, False, False, False], color='lightgray', linewidth=0.5)

        meridians = range(110, 271, 10)  # Intervallo ogni 10 gradi
        self.m.drawmeridians(meridians, labels=[False, False, False, True], color='lightgray', linewidth=0.5)

    def plot_nodes(self):
        """Plotta i nodi sulla mappa."""
        for node, data in self.graph.nodes(data=True):
            x, y = self.m(data['lon'], data['lat'])
            self.m.plot(x, y, marker='o', color='blue', markersize=4)

    def plot_edges(self):
        """Plotta gli archi sulla mappa."""
        for u, v, data in self.graph.edges(data=True):
            node1 = self.graph.nodes[u]
            node2 = self.graph.nodes[v]
            x1, y1 = self.m(node1['lon'], node1['lat'])
            x2, y2 = self.m(node2['lon'], node2['lat'])
            self.m.plot([x1, x2], [y1, y2], color='red', linewidth=0.3)

    def show(self, save_as_png=False):
        """Mostra la mappa e opzionalmente la salva come PNG."""
        plt.title("Tracce dei satelliti e connessioni")
        plt.legend(loc='lower right', fontsize=10)
        if save_as_png:
            save_map_as_png("satellite_map.png")
        else:
            plt.show()