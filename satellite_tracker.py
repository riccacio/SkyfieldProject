from skyfield.api import load
from datetime import timedelta
import numpy as np  # Se lo sposti in utils.py, ricordati di importarlo anche qui se necessario

from utils import euclidean_distance
from collections import defaultdict

class SatelliteTracker:

    def __init__(self, city1, city2, start_time, E_to_W, tle_file="gp.php"):
        # Carica i TLE (se è da aggiornare usare l'URL - ricordarsi di cambiare la data di test)
        tle_url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle"
        self.ts = load.timescale()
        self.satellites = load.tle_file(tle_file)
        # self.satellites = load.tle_file(tle_url)
        print(f"\nSatelliti caricati: {len(self.satellites)}")

        self.E_to_W = E_to_W

        # Coordinate delle città in [-180,180]
        self.city1_lat = city1.latitude.degrees
        self.city1_lon = city1.longitude.degrees
        self.city2_lat = city2.latitude.degrees
        self.city2_lon = city2.longitude.degrees

        if E_to_W:
            if self.city1_lon < 0:
                self.city1_lon += 360
            if self.city2_lon < 0:
                self.city2_lon += 360

        offset = 20
        self.min_lat = min(self.city1_lat, self.city2_lat) - offset
        self.max_lat = max(self.city1_lat, self.city2_lat) + offset+10
        self.min_lon = min(self.city1_lon, self.city2_lon) - offset
        self.max_lon = max(self.city1_lon, self.city2_lon) + offset

        # Intervallo di tempo per la traccia
        self.start_time = start_time
        self.end_time = self.start_time + timedelta(minutes=5)

        self.satellite_validated = []

    def filter_satellites(self):
        """
        Filtra i satelliti che rientrano nel range specificato e, per ciascuno,
        calcola la traccia (track) per un minuto (campionando ogni secondo).
        """
        for sat in self.satellites:
            track = []
            current_time = self.start_time
            is_within_range = True

            while current_time.utc_datetime() <= self.end_time.utc_datetime() and is_within_range:
                subpoint = sat.at(current_time).subpoint()
                sat_lat = subpoint.latitude.degrees
                sat_lon = subpoint.longitude.degrees
                sat_alt = subpoint.elevation.km

                if self.E_to_W:
                    if sat_lon < 0:
                        sat_lon += 360

                # Controllo lat, lon, alt
                if not ((self.min_lat <= sat_lat <= self.max_lat) and
                        (self.min_lon <= sat_lon <= self.max_lon)) or not (500 <= sat_alt <= 570):
                    is_within_range = False

                if is_within_range:
                    track.append((sat_lat, sat_lon, sat_alt))

                current_time += timedelta(seconds=1)

            if is_within_range and len(track) > 2:
                # RAAN in gradi (memorizzato in 'plane')
                orbital_plane = np.degrees(sat.model.nodeo) % 360
                self.satellite_validated.append({
                    'name': sat.name,
                    'track': track,
                    'plane': orbital_plane
                })

        # Assegna plane_index e sat_index_in_plane ai satelliti validati
        self.assign_plane_and_position(angle_threshold=10)
        return self.satellite_validated

    def assign_plane_and_position(self, angle_threshold=10):

        for sat in self.satellite_validated:
            sat['plane_index'] = int(sat['plane'] // angle_threshold)

        plane_dict = defaultdict(list)
        for sat in self.satellite_validated:
            plane_dict[sat['plane_index']].append(sat)

        for p_idx, sat_list in plane_dict.items():
            # Ordina per latitudine media calcolata dal track
            for sat in sat_list:
                lat_values = [pos[0] for pos in sat['track']]
                mid_lat = sum(lat_values) / len(lat_values)
                sat['mid_lat'] = mid_lat

            sat_list.sort(key=lambda x: x['mid_lat'])
            for i, sat in enumerate(sat_list):
                sat['sat_index_in_plane'] = i

    def find_satellite_more_close(self, city_lat, city_lon, satellites):
        """
        Trova il satellite la cui posizione media (calcolata dal track) è la più vicina
        al punto (city_lat, city_lon)
        """
        min_distance = float('inf')
        node = None
        for sat in satellites:
            mid_lat = (sat['track'][0][0] + sat['track'][-1][0]) / 2
            mid_lon = (sat['track'][0][1] + sat['track'][-1][1]) / 2
            mid_alt = (sat['track'][0][2] + sat['track'][-1][2]) / 2
            distance = euclidean_distance(city_lat, city_lon, 0, mid_lat, mid_lon, mid_alt)
            if distance < min_distance:
                node = (sat['name'], mid_lat, mid_lon)
                min_distance = distance

        return node