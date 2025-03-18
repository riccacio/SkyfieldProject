import matplotlib
import numpy as np

#matplotlib.use('MacOSX')
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from skyfield.toposlib import Topos
import data_handler


class SatelliteVisualization:

    def __init__(self, city1_name, city2_name, city1, city2, graph, satellite_validated, start, end, E_to_W, fullscreen):
        self.graph = graph
        self.satellite_validated = satellite_validated
        self.start = start
        self.end = end
        self.E_to_W = E_to_W

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
        offset_lat = 10
        offset_lon = 20

        # Calcola i limiti della mappa
        llcrnrlat = min(self.city1_lat, self.city2_lat) - offset_lat-10
        urcrnrlat = max(self.city1_lat, self.city2_lat) + offset_lat
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
            {'name': self.city2_name,  'lat': self.city2_lat, 'lon': self.city2_lon, 'color': 'green'}
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
                self.m.plot(x, y, marker='o', color='red', markersize=6, label='Source')
            elif node == self.end[0]:
                self.m.plot(x, y, marker='o', color='purple', markersize=6, label='Destination')
            elif path and node in path:
                if not plotted_node_first:
                    self.m.plot(x, y, marker='o', color='black', markersize=6, label='Satellites in shortest path')
                    plotted_node_first = True
                else:
                    self.m.plot(x, y, marker='o', color='black', markersize=6)
            else:
                self.m.plot(x, y, marker='o', color='blue', markersize=4)

    def plot_edges(self, path_d, path_m, range_value, path_label="Shortest path"):
        """
        Disegna gli archi del grafo per due percorsi (ad es. path_d e path_m)
        sulla stessa mappa. Per ogni percorso:
          - Collega la città al primo e all'ultimo satellite (in lime).
          - Colora gli archi che fanno parte del percorso con un colore specifico
            (cyan per path_d e magenta per path_m).
          - Gli altri archi li colora in rosso (con linewidth ridotto, se il range_value è 659.5).
        """
        # Coordinate città trasformate
        x_city1, y_city1 = self.m(self.city1_lon, self.city1_lat)
        x_city2, y_city2 = self.m(self.city2_lon, self.city2_lat)

        # Lista di percorsi da plottare con il colore associato
        paths = [(path_d, 'cyan'), (path_m, 'magenta')]

        for path, color in paths:
            if path is None or len(path) == 0:
                continue  # Salta se il percorso non esiste

            # Collega città al primo e all'ultimo satellite del percorso
            first_sat = path[0]
            last_sat = path[-1]
            first_node = self.graph.nodes[first_sat]
            last_node = self.graph.nodes[last_sat]
            x_first, y_first = self.m(first_node['lon'], first_node['lat'])
            x_last, y_last = self.m(last_node['lon'], last_node['lat'])

            self.m.plot([x_city1, x_first], [y_city1, y_first], color='lime', linewidth=3,
                        label='City-Satellite Connection')
            self.m.plot([x_city2, x_last], [y_city2, y_last], color='lime', linewidth=3)

            # Flag per plottare l'etichetta del percorso una sola volta
            plotted_label = False

            # Itera su tutti gli archi del grafo
            for u, v, data in self.graph.edges(data=True):
                node1 = self.graph.nodes[u]
                node2 = self.graph.nodes[v]
                x1, y1 = self.m(node1['lon'], node1['lat'])
                x2, y2 = self.m(node2['lon'], node2['lat'])

                # Se l'arco fa parte del percorso corrente (ovvero, u e v sono adiacenti nella lista path)
                if (u in path and v in path and abs(path.index(u) - path.index(v)) == 1):
                    if not plotted_label:
                        self.m.plot([x1, x2], [y1, y2], color=color, linewidth=3, label=path_label)
                        plotted_label = True
                    else:
                        self.m.plot([x1, x2], [y1, y2], color=color, linewidth=3)
                else:
                    # Disegna gli archi che non fanno parte del percorso con un colore sottile, ma solo se il range_value è 659.5
                    if range_value == 659.5:
                        self.m.plot([x1, x2], [y1, y2], color='red', linewidth=0.1)

        # (Eventualmente, se vuoi anche disegnare tutti gli archi in rosso per contesto, puoi farlo dopo)
        for u, v, data in self.graph.edges(data=True):
            node1 = self.graph.nodes[u]
            node2 = self.graph.nodes[v]
            x1, y1 = self.m(node1['lon'], node1['lat'])
            x2, y2 = self.m(node2['lon'], node2['lat'])
            self.m.plot([x1, x2], [y1, y2], color='red', linewidth=0.1)

    def show(self, save_as_png=False):
        plt.title("Tracce dei satelliti e connessioni")
        #plt.legend(loc='lower right', fontsize=10)
        if save_as_png:
            data_handler.DataHandler.save_map_as_png("satellite_map.png")
        else:
            plt.show()