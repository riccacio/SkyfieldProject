from skyfield.api import load, Topos
from datetime import timedelta
import numpy as np #DA TOGLIERE E METTERE IN UTILS.PY

from utils import haversine_with_altitude as haversine, euclidean_distance


class SatelliteTracker:

    def __init__(self, tle_file="gp.php", min_lat=30, max_lat=60, min_lon=130, max_lon=250):
        tle_url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle"
        self.ts = load.timescale()
        self.satellites = load.tle_file(tle_file)
        #self.satellites = load.tle_file(tle_url)
        print(f"Satelliti caricati: {len(self.satellites)}")
        self.min_lat, self.max_lat = min_lat, max_lat
        self.min_lon, self.max_lon = min_lon, max_lon
        self.start_time = self.ts.now()
        self.end_time = self.start_time + timedelta(minutes=1)
        self.satellite_validated = []


    def filter_satellites(self):
        """
        Filtra i satelliti che rientrano nel range specificato e, per ciascuno,
        calcola la traccia (track) e ne stima:
          - la posizione media (usata per calcolare l'angolo),
          - il RAAN (in gradi) come identificativo dell'orbita,
          - l'angolo nel piano equatoriale.
        """
        for sat in self.satellites:
            track = []
            current_time = self.start_time
            is_within_range = True

            while current_time.utc_datetime() <= self.end_time.utc_datetime() and is_within_range:
                subpoint = sat.at(current_time).subpoint()
                # Estrazione di latitudine, longitudine e altitudine
                sat_lat = subpoint.latitude.degrees
                sat_lon = subpoint.longitude.degrees
                sat_alt = subpoint.elevation.km

                # Gestione della longitudine negativa
                if sat_lon <= 0:
                    sat_lon += 360

                # Controllo che la posizione e l'altitudine siano nel range desiderato (altitudine fino a ~570 km)
                if not ((self.min_lat <= sat_lat <= self.max_lat) and (self.min_lon <= sat_lon <= self.max_lon)) or not (0 <= sat_alt <= 570):
                    is_within_range = False

                if is_within_range:
                    track.append((sat_lat, sat_lon, sat_alt))

                current_time += timedelta(seconds=1)

            if is_within_range and len(track) > 2:
                # Calcolo della posizione media (si usa la media tra il primo e l'ultimo punto, semplificando)
                mid_lat = (track[0][0] + track[-1][0]) / 2
                mid_lon = (track[0][1] + track[-1][1]) / 2
                mid_alt = (track[0][2] + track[-1][2]) / 2

                #TODO OPERAZIONI DA TOGLIERE E METTERE IN UTILS.PY


                # Calcolo dell'angolo: si proietta la posizione media nel piano equatoriale.
                lat_rad = np.radians(mid_lat)
                lon_rad = np.radians(mid_lon)
                x = np.cos(lat_rad) * np.cos(lon_rad)
                y = np.cos(lat_rad) * np.sin(lon_rad)
                angle = np.degrees(np.arctan2(y, x))
                if angle < 0:
                    angle += 360

                # Estrae il RAAN (Right Ascension of the Ascending Node) dal TLE e lo converte in gradi
                try:
                    orbit = np.degrees(sat.model.nodeo)
                    if orbit < 0:
                        orbit += 360
                except Exception:
                    orbit = None

                self.satellite_validated.append({
                    'name': sat.name,
                    'track': track,
                    'orbit': orbit,
                    'angle': angle
                })
                print(f"Satellite {sat.name}: orbita={orbit}, angolo={angle:.2f}°")

        return self.satellite_validated

    def find_satellite_more_close(self, city_lan, city_lon, satellites):
        min_distance = 1e6
        node = None
        for sat in satellites:
            mid_lat = (sat['track'][0][0] + sat['track'][-1][0]) / 2
            mid_lon = (sat['track'][0][1] + sat['track'][-1][1]) / 2
            mid_alt = (sat['track'][0][2] + sat['track'][-1][2]) / 2
            distance = euclidean_distance(city_lan, city_lon, 0, mid_lat, mid_lon, mid_alt)
            if distance < min_distance:
                node = (sat['name'], mid_lat, mid_lon)
                min_distance = distance

        return node