from skyfield.api import load, Topos
from datetime import timedelta

class SatelliteTracker:
    def __init__(self, tle_file="gp.php", min_lat=30, max_lat=60, min_lon=130, max_lon=250):
        """Inizializza il tracker con i parametri di latitudine e longitudine."""
        self.ts = load.timescale()
        self.satellites = load.tle_file(tle_file)
        self.min_lat, self.max_lat = min_lat, max_lat
        self.min_lon, self.max_lon = min_lon, max_lon
        self.start_time = self.ts.now()
        self.end_time = self.start_time + timedelta(minutes=1)
        self.satellite_validated = []

    def filter_satellites(self):
        """Filtra i satelliti che rientrano nel range specificato."""
        for sat in self.satellites:
            track = []
            current_time = self.start_time
            is_within_range = True

            while current_time.utc_datetime() <= self.end_time.utc_datetime() and is_within_range:
                subpoint = sat.at(current_time).subpoint()
                sat_lat = subpoint.latitude.degrees
                sat_lon = subpoint.longitude.degrees
                sat_alt = subpoint.elevation.km

                # Gestione longitudine
                if sat_lon <= 0:
                    sat_lon += 360

                # Controllo posizione e altitudine
                if not ((self.min_lat <= sat_lat <= self.max_lat) and (self.min_lon <= sat_lon <= self.max_lon)) or not (0 < sat_alt <= 550):
                    is_within_range = False

                if is_within_range:
                    track.append((sat_lat, sat_lon, sat_alt))

                current_time = current_time + timedelta(seconds=1)

            if is_within_range and len(track) > 2:
                self.satellite_validated.append({'name': sat.name, 'track': track})

        return self.satellite_validated