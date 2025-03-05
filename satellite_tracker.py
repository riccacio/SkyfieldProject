from skyfield.api import load, Topos
from datetime import timedelta

from utils import haversine_with_altitude as haversine


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
       #filtra i satelliti che rientrano nel range specificato
        avg = 0
        for sat in self.satellites:
            track = []
            current_time = self.start_time
            is_within_range = True

            while current_time.utc_datetime() <= self.end_time.utc_datetime() and is_within_range:
                subpoint = sat.at(current_time).subpoint()
                # estrazione dei dati di latitudine, longitudine e altitudine di ogni satellite
                sat_lat = subpoint.latitude.degrees
                sat_lon = subpoint.longitude.degrees
                sat_alt = subpoint.elevation.km

                # gestione longitudine negativa
                if sat_lon <= 0:
                    sat_lon += 360

                # controllo posizione e altitudine (550km)
                if not ((self.min_lat <= sat_lat <= self.max_lat) and (
                        self.min_lon <= sat_lon <= self.max_lon)) or not (530 <= sat_alt <= 570):
                    is_within_range = False

                # se resta dentro il range aggiungi alla lista track
                if is_within_range:
                    track.append((sat_lat, sat_lon, sat_alt))

                current_time = current_time + timedelta(seconds=1) # incremento di 1 secondo

            if is_within_range and len(track) > 2:
                avg += track[-1][2]
                self.satellite_validated.append({'name': sat.name, 'track': track})

        return self.satellite_validated


    def find_satellite_more_close(self, city_lan, city_lon, satellites):
        min_distance = 1000000
        for sat in satellites:
            mid_lat = (sat['track'][0][0] + sat['track'][-1][0]) / 2
            mid_lon = (sat['track'][0][1] + sat['track'][-1][1]) / 2
            distance = haversine(city_lan, city_lon, 0, mid_lat, mid_lon, 0)
            if distance < min_distance:
                node = sat['name'], mid_lat, mid_lon
                min_distance = distance

        return node