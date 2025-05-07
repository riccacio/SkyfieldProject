import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import data_handler
from matplotlib.lines import Line2D  # per la legenda personalizzata


class SatelliteVisualization:

    def __init__(self, city1_name, city2_name, city1, city2, graph, satellite_validated, start, end, E_to_W, fullscreen,
                 plusGrid):
        plt.figure(figsize=(14, 6), dpi=600)

        self.graph = graph
        self.satellite_validated = satellite_validated
        self.start = start
        self.end = end
        self.E_to_W = E_to_W
        self.plusGrid = plusGrid

        self.city1_name = city1_name
        self.city2_name = city2_name

        # Coordinate città in [-180, 180]
        self.city1_lat = city1.latitude.degrees
        self.city1_lon = city1.longitude.degrees
        self.city2_lat = city2.latitude.degrees
        self.city2_lon = city2.longitude.degrees

        if self.E_to_W:
            if self.city1_lon < 0:
                self.city1_lon += 360
            if self.city2_lon < 0:
                self.city2_lon += 360

        # Offset per latitudine e longitudine
        offset_lat = 30
        offset_lon = 30

        # Calcola i limiti della mappa
        llcrnrlat = min(self.city1_lat, self.city2_lat) - offset_lat
        urcrnrlat = max(self.city1_lat, self.city2_lat) + offset_lat - 10
        llcrnrlon = min(self.city1_lon, self.city2_lon) - offset_lon
        urcrnrlon = max(self.city1_lon, self.city2_lon) + offset_lon

        if fullscreen:
            mng = plt.get_current_fig_manager()
            mng.full_screen_toggle()

        # Crea la mappa con i limiti calcolati
        self.m = Basemap(
            projection='merc',
            llcrnrlat=llcrnrlat,
            urcrnrlat=urcrnrlat,
            llcrnrlon=llcrnrlon,
            urcrnrlon=urcrnrlon,
            resolution='i'
        )

    def add_cities(self):
        cities = [
            {'name': self.city1_name, 'lat': self.city1_lat, 'lon': self.city1_lon, 'color': 'magenta'},
            {'name': self.city2_name, 'lat': self.city2_lat, 'lon': self.city2_lon, 'color': 'green'}
        ]
        for city in cities:
            x, y = self.m(city['lon'], city['lat'])
            self.m.plot(x, y, marker='o', color=city['color'], markersize=8)

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
        mer_dict = self.m.drawmeridians(meridians, labels=[False, False, False, True],
                                        color='lightgray', linewidth=0.5)

        # Ruota le etichette dei meridiani per evitare sovrapposizioni
        for (_, text) in mer_dict.values():
            for lbl in text:
                lbl.set_rotation(45)
                lbl.set_horizontalalignment('right')

    def plot_tracks(self):
        # Disegna le traiettorie dei satelliti validati
        for sat in self.satellite_validated:
            track = sat['track']
            lats, lons, alt = zip(*track)
            x, y = self.m(lons, lats)
            self.m.plot(x, y, linewidth=1)

    def plot_nodes(self, path=None):
        # Disegna i nodi del grafo (satelliti).
        for node, data in self.graph.nodes(data=True):
            x, y = self.m(data['lon'], data['lat'])
            if node == self.start[0]:
                self.m.plot(x, y, marker='o', color='red', markersize=6)
            elif node == self.end[0]:
                self.m.plot(x, y, marker='o', color='purple', markersize=6)
            else:
                self.m.plot(x, y, marker='o', color='blue', markersize=4)

    def plot_edges(self, path_d, path_m, range_value, path_label="Percorso"):
        # Disegna gli archi del grafo per entrambi i percorsi calcolati

        # Coordinate città trasformate
        x_city1, y_city1 = self.m(self.city1_lon, self.city1_lat)
        x_city2, y_city2 = self.m(self.city2_lon, self.city2_lat)

        # Disegno le connessioni tra nodi (non in percorso) con linewidth ridotto
        for u, v, data in self.graph.edges(data=True):
            node1 = self.graph.nodes[u]
            node2 = self.graph.nodes[v]
            x1, y1 = self.m(node1['lon'], node1['lat'])
            x2, y2 = self.m(node2['lon'], node2['lat'])
            self.m.plot([x1, x2], [y1, y2], color='red', linewidth=0.2)


        paths = [(path_d, 'cyan', 'Percorso Dijkstra'), (path_m, 'lime', 'Percorso MinHop')]

        for path, color, label in paths:
            if path is None or len(path) == 0:
                continue  # Salta se il percorso non esiste

            # Collega città al primo e all'ultimo satellite del percorso
            first_sat = path[0]
            last_sat = path[-1]
            first_node = self.graph.nodes[first_sat]
            last_node = self.graph.nodes[last_sat]
            x_first, y_first = self.m(first_node['lon'], first_node['lat'])
            x_last, y_last = self.m(last_node['lon'], last_node['lat'])

            # Traccio il percorso con linewidth maggiore
            plotted_label = False
            for i in range(len(path) - 1):
                u = path[i]
                v = path[i + 1]
                node1 = self.graph.nodes[u]
                node2 = self.graph.nodes[v]
                x1, y1 = self.m(node1['lon'], node1['lat'])
                x2, y2 = self.m(node2['lon'], node2['lat'])
                if not plotted_label:
                    self.m.plot([x1, x2], [y1, y2], color=color, linewidth=3, label=label)
                    plotted_label = True
                else:
                    self.m.plot([x1, x2], [y1, y2], color=color, linewidth=3)

    def show(self, save_as_png=False):

        legend_elements = [
            # Città
            Line2D([0], [0], marker='o', color='w', label='New York',
                   markerfacecolor='magenta', markersize=8),
            Line2D([0], [0], marker='o', color='w', label='Londra',
                   markerfacecolor='green', markersize=8),

            # Satellite: nodi generici in blu
            Line2D([0], [0], marker='o', color='w', label='Satellite',
                   markerfacecolor='blue', markersize=4),
            # Source e Destination
            Line2D([0], [0], marker='o', color='w', label='Sorgente',
                   markerfacecolor='red', markersize=6),
            Line2D([0], [0], marker='o', color='w', label='Destinazione',
                   markerfacecolor='purple', markersize=6),
            # Percorsi
            Line2D([0], [0], color='cyan', lw=3, label='Cammino Dijkstra'),
            Line2D([0], [0], color='lime', lw=3, label='Cammino MinHop'),
            # Collegamenti base (archi non in percorso)
            Line2D([0], [0], color='red', lw=1, label='Archi')]

        if self.plusGrid:
            plt.title("Mappa dei satelliti con topologia +Grid")
        else:
            plt.title("Mappa dei satelliti con topologia libera")

        ax = plt.gca()
        ax.legend(handles=legend_elements, loc='upper right', fontsize=10)

        if save_as_png:
            data_handler.DataHandler.save_map_as_png("satellite_map.png")
        else:
            plt.show()