import matplotlib
import numpy as np

matplotlib.use('MacOSX')
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from skyfield.toposlib import Topos
from data_handler import save_map_as_png


class SatelliteVisualization:

    def __init__(self, city1, city2, graph, satellite_validated, start, end):
        self.graph = graph
        self.satellite_validated = satellite_validated
        self.start = start
        self.end = end

        # Coordinate città in [-180, 180]
        self.city1_lat = city1.latitude.degrees
        self.city1_lon = city1.longitude.degrees
        self.city2_lat = city2.latitude.degrees
        self.city2_lon = city2.longitude.degrees

        # Normalizza le longitudini delle città nel range [-180, 180]
        if self.city1_lon < -180 or self.city1_lon > 180:
            self.city1_lon = ((self.city1_lon + 180) % 360) - 180
        if self.city2_lon < -180 or self.city2_lon > 180:
            self.city2_lon = ((self.city2_lon + 180) % 360) - 180

        # Offset per latitudine e longitudine
        offset_lat = 15
        offset_lon = 20

        # Calcola i limiti della mappa
        llcrnrlat = min(self.city1_lat, self.city2_lat) - offset_lat
        urcrnrlat = max(self.city1_lat, self.city2_lat) + offset_lat
        llcrnrlon = min(self.city1_lon, self.city2_lon) - offset_lon
        urcrnrlon = max(self.city1_lon, self.city2_lon) + offset_lon

        # Apri a schermo intero (opzionale)
        mng = plt.get_current_fig_manager()
        mng.full_screen_toggle()

        # Crea la mappa con i limiti calcolati
        # lon_0=-40 serve a centrare la proiezione intorno a 40°W (Atlantico)
        self.m = Basemap(
            projection='merc',
            llcrnrlat=llcrnrlat,
            urcrnrlat=urcrnrlat,
            llcrnrlon=llcrnrlon,
            urcrnrlon=urcrnrlon,
            lon_0=-40,
            resolution='i'
        )

    def add_cities(self):
        cities = [
            {'name': 'New York', 'lat': self.city1_lat, 'lon': self.city1_lon, 'color': 'magenta'},
            {'name': 'London',  'lat': self.city2_lat, 'lon': self.city2_lon, 'color': 'green'}
        ]
        for city in cities:
            x, y = self.m(city['lon'], city['lat'])
            self.m.plot(x, y, marker='o', color=city['color'], markersize=8, label=city['name'])

    def draw_map(self):
        self.m.drawcoastlines()
        self.m.drawcountries()
        self.m.fillcontinents(color='lightgray')

        # Calcola i paralleli in base ai limiti della mappa
        llcrnrlat = int(np.floor(self.m.llcrnrlat / 10.0) * 10)
        urcrnrlat = int(np.ceil(self.m.urcrnrlat / 10.0) * 10)
        parallels = np.arange(llcrnrlat, urcrnrlat + 1, 10)

        # Calcola i meridiani in base ai limiti della mappa
        llcrnrlon = int(np.floor(self.m.llcrnrlon / 10.0) * 10)
        urcrnrlon = int(np.ceil(self.m.urcrnrlon / 10.0) * 10)
        meridians = np.arange(llcrnrlon, urcrnrlon + 1, 10)

        self.m.drawparallels(parallels, labels=[True, False, False, False],
                             color='lightgray', linewidth=0.5)
        self.m.drawmeridians(meridians, labels=[False, False, False, True],
                             color='lightgray', linewidth=0.5)

    def plot_tracks(self):
        """
        Disegna le traiettorie dei satelliti validati (track).
        """
        for sat in self.satellite_validated:
            track = sat['track']
            lats, lons, alt = zip(*track)
            x, y = self.m(lons, lats)
            self.m.plot(x, y, linewidth=1)

    def plot_nodes(self, path=None):
        """
        Disegna i nodi del grafo (satelliti), colorando diversamente
        quelli di start, end e quelli sul cammino minimo.
        """
        plotted_node_first = False
        for node, data in self.graph.nodes(data=True):
            x, y = self.m(data['lon'], data['lat'])

            if node == self.start[0]:
                self.m.plot(x, y, marker='o', color='purple', markersize=6, label='Source')
            elif node == self.end[0]:
                self.m.plot(x, y, marker='o', color='red', markersize=6, label='Destination')
            elif path and node in path:
                if not plotted_node_first:
                    self.m.plot(x, y, marker='o', color='black', markersize=6, label='Satellites in shortest path')
                    plotted_node_first = True
                else:
                    self.m.plot(x, y, marker='o', color='black', markersize=6)
            else:
                self.m.plot(x, y, marker='o', color='blue', markersize=4)

    def plot_edges(self, path=None, path_label="Shortest path"):
        """
        Disegna gli archi del grafo. Se un arco fa parte del percorso
        minimo (path), lo colora in cyan, altrimenti in rosso.
        """
        plotted_path_first = False
        for u, v, data in self.graph.edges(data=True):
            node1 = self.graph.nodes[u]
            node2 = self.graph.nodes[v]
            x1, y1 = self.m(node1['lon'], node1['lat'])
            x2, y2 = self.m(node2['lon'], node2['lat'])

            if path and (
                (u in path and v in path and path.index(u) + 1 == path.index(v)) or
                (v in path and u in path and path.index(v) + 1 == path.index(u))
            ):
                if not plotted_path_first:
                    self.m.plot([x1, x2], [y1, y2], color='cyan', linewidth=3, label=path_label)
                    plotted_path_first = True
                else:
                    self.m.plot([x1, x2], [y1, y2], color='cyan', linewidth=3)
            else:
                self.m.plot([x1, x2], [y1, y2], color='red', linewidth=0.1)

    def show(self, save_as_png=False):
        plt.title("Tracce dei satelliti e connessioni")
        plt.legend(loc='lower right', fontsize=10)
        if save_as_png:
            save_map_as_png("satellite_map.png")
        else:
            plt.show()