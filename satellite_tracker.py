from skyfield.api import load, Topos
from datetime import timedelta
import numpy as np #DA TOGLIERE E METTERE IN UTILS.PY

from utils import haversine_with_altitude as haversine, euclidean_distance

""" 
class SatelliteTracker:

    def __init__(self, tle_file="gp.php", min_lat=30, max_lat=60, min_lon=130, max_lon=250, P=72, F=39, Q=None):
        """"""
        Aggiungi i parametri della costellazione:
          - P: numero di piani orbitali
          - F: phasing factor (fase)
          - Q: numero di satelliti per piano (opzionale, se non fornito, potrai stimarlo)
        """"""
        tle_url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle"
        self.ts = load.timescale()
        self.satellites = load.tle_file(tle_file)
        # self.satellites = load.tle_file(tle_url)
        print(f"Satelliti caricati: {len(self.satellites)}")
        self.min_lat, self.max_lat = min_lat, max_lat
        self.min_lon, self.max_lon = min_lon, max_lon
        self.start_time = self.ts.now()
        self.end_time = self.start_time + timedelta(minutes=1)
        self.satellite_validated = []
        self.P = P
        self.F = F
        self.Q = Q  # se non definito, potresti stimarlo dopo il filtraggio

    def filter_satellites(self):
        """"""
        Filtra i satelliti che rientrano nel range specificato e calcola la traccia (track).
        Oltre a 'lat', 'lon' e 'alt', per ciascun satellite assegna:
          - 'orbit': il piano orbitale calcolato a partire dal RAAN
          - 'index': l’indice all’interno del piano (in questo esempio, impostato a 0,
                     ma in una versione completa si dovrebbe ordinare e assegnare in modo progressivo)
          - 'angle': posizione angolare calcolata dalla posizione media
        """"""
        for sat in self.satellites:
            track = []
            current_time = self.start_time
            is_within_range = True

            while current_time.utc_datetime() <= self.end_time.utc_datetime() and is_within_range:
                subpoint = sat.at(current_time).subpoint()
                sat_lat = subpoint.latitude.degrees
                sat_lon = subpoint.longitude.degrees
                sat_alt = subpoint.elevation.km

                if sat_lon <= 0:
                    sat_lon += 360

                if not ((self.min_lat <= sat_lat <= self.max_lat) and (self.min_lon <= sat_lon <= self.max_lon)) or not (0 <= sat_alt <= 570):
                    is_within_range = False

                if is_within_range:
                    track.append((sat_lat, sat_lon, sat_alt))

                current_time += timedelta(seconds=1)

            if is_within_range and len(track) > 2:
                mid_lat = (track[0][0] + track[-1][0]) / 2
                mid_lon = (track[0][1] + track[-1][1]) / 2
                mid_alt = (track[0][2] + track[-1][2]) / 2

                # Calcola l'angolo per ordinare i satelliti lungo il piano orbitale
                lat_rad = np.radians(mid_lat)
                lon_rad = np.radians(mid_lon)
                x = np.cos(lat_rad) * np.cos(lon_rad)
                y = np.cos(lat_rad) * np.sin(lon_rad)
                angle = np.degrees(np.arctan2(y, x))
                if angle < 0:
                    angle += 360

                # Calcola l'orbita (piano orbitale) usando il RAAN del TLE, se P è definito
                orbit = None
                try:
                    # sat.model.nodeo è il RAAN in radianti; lo converto in gradi
                    raan = np.degrees(sat.model.nodeo)
                    if raan < 0:
                        raan += 360
                    if self.P is not None:
                        delta_raan = 360 / self.P
                        orbit = int(raan // delta_raan)
                except Exception as e:
                    print("Impossibile estrarre RAAN per", sat.name, ":", e)

                # Assegna l'indice all’interno del piano.
                # In questo esempio viene impostato a 0. Per una corretta assegnazione,
                # dovresti raggruppare i satelliti per 'orbit' e ordinarli in base a un criterio (ad es. angle)
                index = 0

                self.satellite_validated.append({
                    'name': sat.name,
                    'track': track,
                    'orbit': orbit,
                    'index': index,
                    'angle': angle
                })

        # Se Q non è definito, lo stimo come il numero di satelliti totali diviso il numero di piani (distribuzione uniforme)
        if self.P is not None and self.Q is None:
            self.Q = len(self.satellite_validated) // self.P

        return self.satellite_validated

    def assign_indices(self, satellites):
        """"""
        Raggruppa i satelliti per 'orbit' e, per ciascun gruppo, ordina i satelliti
        in base al campo 'angle'. Assegna quindi a ciascun satellite un indice (campo 'index')
        in ordine crescente a partire da 0.

        Parametri:
            satellites (list of dict): Lista di satelliti, ognuno con almeno i campi 'orbit' e 'angle'.

        Ritorna:
            list of dict: La lista dei satelliti con il campo 'index' aggiornato.
        """"""
        # Raggruppa per orbit
        grouped = {}
        for sat in satellites:
            orbit = sat.get('orbit')
            if orbit is None:
                continue  # oppure gestisci diversamente i satelliti senza 'orbit'
            if orbit not in grouped:
                grouped[orbit] = []
            grouped[orbit].append(sat)

        # Per ciascun gruppo, ordina per angle e assegna l'indice
        for orbit, sats in grouped.items():
            sats.sort(key=lambda s: s.get('angle', 0))
            for idx, sat in enumerate(sats):
                sat['index'] = idx

        # Appiattisce i gruppi in una lista
        assigned_satellites = []
        for sats in grouped.values():
            assigned_satellites.extend(sats)

        return assigned_satellites

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
"""


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
        calcola la traccia (track) per un minuto ogni secondo.
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
                if not ((self.min_lat <= sat_lat <= self.max_lat) and (self.min_lon <= sat_lon <= self.max_lon)) or not (530 <= sat_alt <= 570):
                    is_within_range = False

                if is_within_range:
                    track.append((sat_lat, sat_lon, sat_alt))

                current_time += timedelta(seconds=1)

            if is_within_range and len(track) > 2:
                self.satellite_validated.append({
                    'name': sat.name,
                    'track': track,
                })
                #print(f"Satellite {sat.name}: orbita={orbit}, angolo={angle:.2f}°")

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



