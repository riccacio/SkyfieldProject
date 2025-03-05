import matplotlib
matplotlib.use('MacOSX')
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from skyfield.toposlib import Topos
from data_handler import save_map_as_png


class SatelliteVisualization:

    def __init__(self, city1, city2,  graph, satellite_validated, start, end):
        self.graph = graph
        self.satellite_validated = satellite_validated
        self.city1 = city1
        self.city2 = city2
        self.start = start
        self.end = end

        # per schermo intero
        mng = plt.get_current_fig_manager()
        mng.full_screen_toggle()

        self.m = Basemap(projection='merc',
                         llcrnrlat=10, urcrnrlat=65,
                         llcrnrlon=110, urcrnrlon=260,
                         resolution='i')


    def add_cities(self):
        # estraggo latitudine e longitudine delle città
        city1_lat = self.city1.latitude.degrees
        city1_lon = self.city1.longitude.degrees
        city2_lat = self.city2.latitude.degrees
        city2_lon = self.city2.longitude.degrees

        if city1_lon < 0:
            city1_lon += 360

        if city2_lon < 0:
            city2_lon += 360

        cities = [
            {'name': 'Vancouver', 'lat': city1_lat, 'lon': city1_lon, 'color': 'magenta'},
            {'name': 'Tokyo', 'lat': city2_lat, 'lon': city2_lon, 'color': 'green'}
        ]

        for city in cities:
            x, y = self.m(city['lon'], city['lat'])  # Converte le coordinate in coordinate della mappa
            self.m.plot(x, y, marker='o', color=city['color'], markersize=8, label=city['name'])

    def draw_map(self):
        self.m.drawcoastlines()
        self.m.drawcountries()

        parallels = range(-20, 71, 10)  # intervallo ogni 10 gradi
        self.m.drawparallels(parallels, labels=[True, False, False, False], color='lightgray', linewidth=0.5)

        meridians = range(110, 271, 10)  # intervallo ogni 10 gradi
        self.m.drawmeridians(meridians, labels=[False, False, False, True], color='lightgray', linewidth=0.5)

    def plot_tracks(self):
        for sat in self.satellite_validated:
            track = sat['track']
            lats, lons, alt = zip(*track)  # separa latitudine e longitudine
            x, y = self.m(lons, lats)  # converto le coordinate in coordinate della mappa
            self.m.plot(x, y, linewidth=1)

    def plot_nodes(self):
        for node, data in self.graph.nodes(data=True):
            x, y = self.m(data['lon'], data['lat'])
            if node == self.start[0]:
                self.m.plot(x, y, marker='o', color='orangered', markersize=4, label='Source')
            elif node == self.end[0]:
                self.m.plot(x, y, marker='o', color='maroon', markersize=4, label='Destination')
            else:
                self.m.plot(x, y, marker='o', color='blue', markersize=4)

    def plot_edges(self, path=None):
        for u, v, data in self.graph.edges(data=True):
            node1 = self.graph.nodes[u]
            node2 = self.graph.nodes[v]
            x1, y1 = self.m(node1['lon'], node1['lat'])
            x2, y2 = self.m(node2['lon'], node2['lat'])

            if path and ((u in path and v in path and path.index(u) + 1 == path.index(v)) or (v in path and u in path and path.index(v) + 1 == path.index(u))):
                self.m.plot([x1, x2], [y1, y2], color='green', linewidth=3)
            else:
                self.m.plot([x1, x2], [y1, y2], color='red', linewidth=0.1)

    def show(self, save_as_png=False):
        plt.title("Tracce dei satelliti e connessioni")
        plt.legend(loc='lower right', fontsize=10)
        if save_as_png:
            save_map_as_png("satellite_map.png")
        else:
            plt.show()