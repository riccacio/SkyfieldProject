"""
from skyfield.api import load, Topos
import networkx as nx
import matplotlib

matplotlib.use('MacOSX')  # Forza il backend nativo per macOS
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.basemap import Basemap
from datetime import timedelta
import csv


def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Raggio medio della Terra in km
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])  # Converti in radianti

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))

    return R * c  # Distanza in km


# URL per i TLE dei satelliti Starlink
#tle_url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle"
satellites = load.tle_file("gp.php")

print(f"Caricati {len(satellites)} satelliti.")

# Carica il time scale
ts = load.timescale()
start_time = ts.now()  # Tempo attuale
end_time = start_time + timedelta(minutes=1)  # Periodo di 1 minuto

# Definizione limiti geografici
min_lat, max_lat = 30, 60  # Limiti latitudine
min_lon, max_lon = 130, 250  # Limiti longitudine -110°W = 250

# Liste per tracciare i satelliti validi
satellite_validated = []

for sat in satellites:
    track = []  # Lista per salvare la traiettoria del satellite
    current_time = start_time
    is_within_range = True  # Assume che il satellite rimanga nel range per tutto il periodo

    while current_time.utc_datetime() <= end_time.utc_datetime() and is_within_range:
        # Ottieni la posizione del satellite
        subpoint = sat.at(current_time).subpoint()
        sat_lat = subpoint.latitude.degrees
        sat_lon = subpoint.longitude.degrees
        sat_alt = subpoint.elevation.km

        # Conversione della longitudine per gestire il range 120°E - 110°W correttamente
        if sat_lon <= 0:
            sat_lon += 360  # Porta le longitudini tra -180° e 180°

        # Controllo della posizione nel range desiderato
        if not ((min_lat <= sat_lat <= max_lat) and (min_lon <= sat_lon <= max_lon)):
            is_within_range = False

        # Controllo dell'altitudine del satellite
        if not (0 < sat_alt <= 550):  # Se sotto l'orizzonte o sopra 550 km, lo escludiamo
            is_within_range = False

        # Aggiungi il punto alla traiettoria se è ancora valido
        if is_within_range:
            track.append((sat_lat, sat_lon, sat_alt))

        # Avanza il tempo di 1 secondo
        current_time = current_time + timedelta(seconds=1)

    # Se il satellite è rimasto SEMPRE nel range per almeno un istante, lo salviamo
    if is_within_range and len(track) > 2:  # Assicura almeno 3 punti per evitare outlier
        satellite_validated.append({'name': sat.name, 'track': track})

# Definizione delle città
vancouver = Topos(latitude_degrees=49.2827, longitude_degrees=-123.1207)  # Vancouver
tokyo = Topos(latitude_degrees=35.6762, longitude_degrees=139.6503)  # Tokyo

# Estrai latitudine e longitudine delle città
vancouver_lat = vancouver.latitude.degrees
vancouver_lon = vancouver.longitude.degrees
tokyo_lat = tokyo.latitude.degrees
tokyo_lon = tokyo.longitude.degrees

# Converti le longitudini di Vancouver e Tokyo nel range 0°:360°
vancouver_lon_adjusted = vancouver_lon if vancouver_lon >= 0 else vancouver_lon + 360
tokyo_lon_adjusted = tokyo_lon if tokyo_lon >= 0 else tokyo_lon + 360

# Crea una mappa 2D per visualizzare i satelliti
mng = plt.get_current_fig_manager()
mng.full_screen_toggle()

# Definizione della mappa
m = Basemap(projection='merc',
            llcrnrlat=10, urcrnrlat=65,  # Limiti latitudine
            llcrnrlon=110, urcrnrlon=260,  # Limiti longitudine
            resolution='i')  # Alta risoluzione

# Disegna le linee costiere e i confini dei paesi
m.drawcoastlines()
m.drawcountries()

# Disegna i paralleli (latitudine)
parallels = range(-20, 71, 10)  # Intervallo ogni 10 gradi
m.drawparallels(parallels, labels=[True, False, False, False], color='lightgray', linewidth=0.5)

# Disegna i meridiani (longitudine)
meridians = range(110, 271, 10)  # Intervallo ogni 10 gradi
m.drawmeridians(meridians, labels=[False, False, False, True], color='lightgray', linewidth=0.5)

# Aggiungi Vancouver e Tokyo come città sulla mappa
cities = [
    {'name': 'Vancouver', 'lat': vancouver_lat, 'lon': vancouver_lon_adjusted, 'color': 'red'},
    {'name': 'Tokyo', 'lat': tokyo_lat, 'lon': tokyo_lon_adjusted, 'color': 'green'}
]

# Aggiunta delle città con marker
for city in cities:
    x, y = m(city['lon'], city['lat'])  # Converte le coordinate in coordinate della mappa
    m.plot(x, y, marker='o', color=city['color'], markersize=6, label=city['name'])

"""
"""
# Traccia le traiettorie dei satelliti
for sat in satellite_validated:
    track = sat['track']
    lats, lons, alt = zip(*track)  # Separare latitudine e longitudine
    x, y = m(lons, lats)  # Converti le coordinate in coordinate della mappa
    m.plot(x, y, linewidth=1)  # Disegna la traiettoria
"""
"""

# Aggiungi il punto medio della traiettoria per ogni satellite

sat_data = []
satellite_validated_data = []

LISL_range = 660  # km

G = nx.Graph()

for sat in satellite_validated:
    track = sat['track']
    if len(track) >= 2:  # Assicurati che ci siano almeno due punti
        first_point = track[0]
        last_point = track[-1]

        # Calcola il punto medio della traiettoria
        mid_lat = (first_point[0] + last_point[0]) / 2
        mid_lon = (first_point[1] + last_point[1]) / 2

        # Converti la longitudine nel range 0°- 360° se necessario
        mid_lon = mid_lon if mid_lon >= 0 else mid_lon + 360

        # Converti le coordinate geografiche in coordinate della mappa
        x, y = m(mid_lon, mid_lat)

        sat_data = {
            'name': sat['name'],
            'lat': mid_lat,
            'lon': mid_lon,
            'x': x,
            'y': y
        }

        satellite_validated_data.append(sat_data)
        # Plotta il punto medio sulla mappa
        m.plot(x, y, marker='o', color='blue', markersize=4)

# Aggiungi i nodi (satelliti)
for sat in satellite_validated_data:
    G.add_node(sat['name'], lat=sat['lat'], lon=sat['lon'])  # aggiungi i nodi

# Connetti i satelliti solo se sono a meno di LISL_range km
for i in range(len(satellite_validated_data)):
    for j in range(i + 1, len(satellite_validated_data)):  # Evita confronti duplicati
        sat1 = satellite_validated_data[i]
        sat2 = satellite_validated_data[j]

        # Calcola la distanza tra i due satelliti
        distance = haversine(sat1['lat'], sat1['lon'], sat2['lat'], sat2['lon'])

        if distance <= LISL_range:
            G.add_edge(sat1['name'], sat2['name'], weight=distance)  # aggiungi al grafo
            m.plot([sat1['x'], sat2['x']], [sat1['y'], sat2['y']], color='red', linewidth=0.3)  # traccia la linea

# Collega tutti i satelliti vicini al primo
sat1 = satellite_validated_data[0]
conta = 0
for j in range(1, len(satellite_validated_data)):  # Evita confronti duplicati
    sat2 = satellite_validated_data[j]

    distance = haversine(sat1['lat'], sat1['lon'], sat2['lat'], sat2['lon'])

    # Se la distanza è inferiore a 600 km, collega i satelliti con una linea
    if distance <= LISL_range:
        conta += 1
        m.plot([sat1['x'], sat2['x']], [sat1['y'], sat2['y']], color='red', linewidth=0.5)

print(f"Numero satelliti collegati: {conta}")

"""
""" 
# TRAITETTORIE per un minuto ogni 1 secondo
print(
    f"Satelliti presenti nel range:\nlat: {min_lat}°N:{max_lat}°N\nlong: {min_lon}°E:{(max_lon - 360) * -1}°W\nNumero satelliti: {len(satellite_validated)}")
print("\nTraiettorie dei satelliti:")
for sat in satellite_validated:
    print(f"Satellite: {sat['name']}")
    lats, lons, alt = zip(*sat['track'])  # Separare latitudine e longitudine
    #print(f"  Traccia: {sat['track']}")
"""
"""

print(f"Nodi nel grafo: {G.number_of_nodes()}")
print(f"Archi nel grafo: {G.number_of_edges()}")

# SALVATAGGIO DEI DATI IN DUE FILE IN CSV
with open("nodes.csv", mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Satellite", "Latitudine", "Longitudine"])  # Intestazione
    for node, data in G.nodes(data=True):
        writer.writerow([node, data["lat"], data["lon"]])

with open("edges.csv", mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Satellite1", "Satellite2", "Distanza_km"])  # Intestazione
    for u, v, data in G.edges(data=True):
        writer.writerow([u, v, data["weight"]])

# Mostra la mappa con il titolo
plt.title("Tracce dei satelliti che restano nel range per 1 minuto (intervallo di 1 secondo)", fontsize=16)
plt.legend(loc='lower right', fontsize=10)
plt.show()

"""

"""
SATELLITI COMPRESI NEL RANGE DI LONG E LAT PER UN PERIODO DI 1 MIN CON UN INTERVALLI DI 1 SECOND0
quindi abbiamo una "striscia" che percorre il satellite per un minuto, lo spazio che percorre il satellite in un minuto
from skyfield.api import load, Topos
import matplotlib
matplotlib.use('MacOSX')  # Forza il backend nativo per macOS
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from datetime import timedelta

# URL per i TLE dei satelliti Starlink
#url = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle'

# Scarica i dati TLE
#print("Scaricando i dati TLE...")

satellites = load.tle_file("gp.php")

print(f"Caricati {len(satellites)} satelliti.")

# Tempo attuale
ts = load.timescale()
start_time = ts.now()  # Tempo attuale
end_time = start_time + timedelta(minutes=1)  # Periodo di 1 minuto

# Definisci i limiti di latitudine e longitudine
min_lat, max_lat = 20, 60  # Latitudine tra 20°N e 60°N
min_lon, max_lon = 120, -110  # Longitudine tra 120°E e 110°W

# Liste per immagazzinare i satelliti e le loro traiettorie
satellite_tracks = []

for sat in satellites:
    track = []  # Lista per salvare la traiettoria del satellite
    current_time = start_time
    is_within_range = True  # Assume che il satellite rimanga nel range

    while current_time.utc_datetime() <= end_time.utc_datetime() and is_within_range:
        # Ottieni il subpoint del satellite al tempo corrente
        subpoint = sat.at(current_time).subpoint()
        sat_lat = subpoint.latitude.degrees
        sat_lon = subpoint.longitude.degrees

        # Gestisci la longitudine negativa
        sat_lon = sat_lon if sat_lon >= 0 else sat_lon + 360
        min_lon_adjusted = min_lon if min_lon >= 0 else min_lon + 360
        max_lon_adjusted = max_lon if max_lon >= 0 else max_lon + 360

        # Controlla se il satellite esce dai limiti
        if not (min_lat <= sat_lat <= max_lat and min_lon_adjusted <= sat_lon <= max_lon_adjusted):
            is_within_range = False  # Il satellite è fuori dal range

        # Aggiungi il punto alla traiettoria
        track.append((sat_lat, sat_lon))

        # Incrementa il tempo di 1 secondo
        current_time = current_time + timedelta(seconds=1)

    # Aggiungi la traiettoria solo se il satellite è rimasto sempre nel range
    if is_within_range and len(track) > 1:
        satellite_tracks.append({'name': sat.name, 'track': track})

# Definizione delle città
vancouver = Topos(latitude_degrees=49.2827, longitude_degrees=-123.1207)  # Vancouver
tokyo = Topos(latitude_degrees=35.6762, longitude_degrees=139.6503)  # Tokyo

# Estrai latitudine e longitudine delle città
vancouver_lat = vancouver.latitude.degrees
vancouver_lon = vancouver.longitude.degrees
tokyo_lat = tokyo.latitude.degrees
tokyo_lon = tokyo.longitude.degrees

# Converti le longitudini di Vancouver e Tokyo nel range 0°:360°
vancouver_lon_adjusted = vancouver_lon if vancouver_lon >= 0 else vancouver_lon + 360
tokyo_lon_adjusted = tokyo_lon if tokyo_lon >= 0 else tokyo_lon + 360


# Crea una mappa 2D per visualizzare i satelliti
plt.figure(figsize=(10, 8))

# Definizione della mappa
m = Basemap(projection='merc',
            llcrnrlat=-20, urcrnrlat=70,  # Limiti latitudine
            llcrnrlon=110, urcrnrlon=270,  # Limiti longitudine
            resolution='i')  # Alta risoluzione

# Disegna le linee costiere e i confini dei paesi
m.drawcoastlines()
m.drawcountries()

# Disegna i paralleli (latitudine)
parallels = range(-20, 71, 10)  # Intervallo ogni 10 gradi
m.drawparallels(parallels, labels=[True, False, False, False], color='lightgray', linewidth=0.5)

# Disegna i meridiani (longitudine)
meridians = range(110, 271, 10)  # Intervallo ogni 10 gradi
m.drawmeridians(meridians, labels=[False, False, False, True], color='lightgray', linewidth=0.5)

# Aggiungi Vancouver e Tokyo come città sulla mappa
cities = [
    {'name': 'Vancouver', 'lat': vancouver_lat, 'lon': vancouver_lon_adjusted, 'color': 'red'},
    {'name': 'Tokyo', 'lat': tokyo_lat, 'lon': tokyo_lon_adjusted, 'color': 'green'}
]

# Aggiunta delle città con marker
for city in cities:
    x, y = m(city['lon'], city['lat'])  # Converte le coordinate in coordinate della mappa
    m.plot(x, y, marker='o', color=city['color'], markersize=6, label=city['name'])

# Traccia le traiettorie dei satelliti
for sat in satellite_tracks:
    track = sat['track']
    lats, lons = zip(*track)  # Separare latitudine e longitudine
    x, y = m(lons, lats)  # Converti le coordinate in coordinate della mappa
    m.plot(x, y, linewidth=1)  # Disegna la traiettoria

# Stampa le traiettorie dei satelliti
print(f"Satelliti presenti nel range:\nlat: {min_lat}°N:{max_lat}°N\nlong: {min_lon}°E:{(max_lon-360)*-1}°W\nNumero satelliti: {len(satellite_tracks)}")
print("\nTraiettorie dei satelliti:")
for sat in satellite_tracks:
    print(f"Satellite: {sat['name']}")
    print(f"  Traccia: {sat['track']}")

# Mostra la mappa con il titolo
plt.title("Tracce dei satelliti che restano nel range per 1 minuto (intervallo di 1 secondo)", fontsize=16)
plt.legend(loc='lower right', fontsize=10)
plt.show()
"""

""" SATELLITI COMPRESI NEL RANGE DI LONG E LAT PER 10 MIN
from skyfield.api import load, Topos
import matplotlib
matplotlib.use('MacOSX')  # Forza il backend nativo per macOS
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from datetime import timedelta

# URL per i TLE dei satelliti Starlink
url = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle'

# Scarica i dati TLE
print("Scaricando i dati TLE...")
satellites = load.tle_file(url)

print(f"Caricati {len(satellites)} satelliti.")

# Tempo attuale
ts = load.timescale()
start_time = ts.now()  # Tempo attuale
end_time = start_time + timedelta(minutes=10)  # Periodo di 10 minuti

# Definisci i limiti di latitudine e longitudine
min_lat, max_lat = 20, 60  # Latitudine tra 20° e 60°
min_lon, max_lon = 120, 290  # Longitudine tra 120°E e 110°W

# Lista per immagazzinare i satelliti che restano nel range per 10 minuti
satellites_in_range = []

for sat in satellites:
    is_within_range = True  # Assume che il satellite sia nel range
    current_time = start_time

    while current_time.utc_datetime() <= end_time.utc_datetime():
        # Ottieni il subpoint del satellite al tempo corrente
        subpoint = sat.at(current_time).subpoint()
        sat_lat = subpoint.latitude.degrees
        sat_lon = subpoint.longitude.degrees

        # Gestisci la longitudine negativa (converti -110W a 250E per consistenza)
        sat_lon = sat_lon if sat_lon >= 0 else sat_lon + 360  # Converte da -180:180 a 0:360
        min_lon_adjusted = min_lon if min_lon >= 0 else min_lon + 360
        max_lon_adjusted = max_lon if max_lon >= 0 else max_lon + 360

        # Controlla se il satellite è fuori dai limiti
        if not (min_lat <= sat_lat <= max_lat and min_lon_adjusted <= sat_lon <= max_lon_adjusted):
            is_within_range = False
            break  # Interrompi il ciclo se il satellite esce dal range

        # Incrementa il tempo di 1 minuto
        current_time = current_time + timedelta(minutes=1)

    # Aggiungi il satellite alla lista solo se è rimasto sempre nel range
    if is_within_range:
        satellites_in_range.append(sat)

# Debug: Stampa il numero di satelliti trovati
print(f"Satelliti che rimangono nel range lat({min_lat}:{max_lat}) e long({min_lon}E:{max_lon}W) per 10 minuti: {len(satellites_in_range)}")

# Definisci le città
vancouver = Topos(latitude_degrees=49.2827, longitude_degrees=-123.1207)  # Vancouver
tokyo = Topos(latitude_degrees=35.6762, longitude_degrees=139.6503)  # Tokyo

# Estrai latitudine e longitudine
vancouver_lat = vancouver.latitude.degrees
vancouver_lon = vancouver.longitude.degrees
tokyo_lat = tokyo.latitude.degrees
tokyo_lon = tokyo.longitude.degrees

# Calcola il punto centrale tra le due città
center_lat = (vancouver_lat + tokyo_lat) / 2
center_lon = (vancouver_lon + tokyo_lon) / 2

# Funzione per convertire longitudini negative in longitudini equivalenti (0°-360°)
def adjust_longitude(lon):
    if lon < 0:
        return lon + 360
    return lon

# Converti le longitudini di Vancouver e Tokyo nel range 0°-360°
vancouver_lon_adjusted = adjust_longitude(vancouver_lon)
tokyo_lon_adjusted = adjust_longitude(tokyo_lon)


# Crea una mappa 2D per visualizzare i satelliti
plt.figure(figsize=(10, 8))

# Definizione della mappa
m = Basemap(projection='merc',
            llcrnrlat=-20, urcrnrlat=70,  # Limiti latitudine
            llcrnrlon=110, urcrnrlon=270,  # Limiti longitudine
            resolution='i')  # Alta risoluzione

# Disegna le linee costiere e i confini dei paesi
m.drawcoastlines()
m.drawcountries()

# Disegna i paralleli (latitudine)
parallels = range(-20, 71, 10)  # Intervallo ogni 10 gradi
m.drawparallels(parallels, labels=[True, False, False, False], color='lightgray', linewidth=0.5)

# Disegna i meridiani (longitudine)
meridians = range(110, 271, 10)  # Intervallo ogni 10 gradi
m.drawmeridians(meridians, labels=[False, False, False, True], color='lightgray', linewidth=0.5)


# Aggiungi Vancouver e Tokyo come città sulla mappa
cities = [
    {'name': 'Vancouver', 'lat': vancouver_lat, 'lon': vancouver_lon_adjusted, 'color': 'blue'},
    {'name': 'Tokyo', 'lat': tokyo_lat, 'lon': tokyo_lon_adjusted, 'color': 'green'}
]

# Aggiunta delle città con marker
for city in cities:
    x, y = m(city['lon'], city['lat'])  # Converte le coordinate in coordinate della mappa
    m.plot(x, y, marker='*', color=city['color'], markersize=6, label=city['name'])
    plt.text(x, y, city['name'], fontsize=12, ha='right', color=city['color'])

# Aggiungi i satelliti alla mappa
for sat in satellites_in_range:
    lat = sat.at(start_time).subpoint().latitude.degrees
    lon = sat.at(start_time).subpoint().longitude.degrees
    lon = lon if lon >= 0 else lon + 360  # Regola la longitudine
    x, y = m(lon, lat)  # Converte le coordinate in coordinate della mappa
    m.plot(x, y, marker='o', color='red', markersize=2)  # Satelliti visibili

# Mostra la mappa con il titolo
plt.title("Satelliti che restano nel range per 10 minuti", fontsize=16)
plt.show()

# Stampa i risultati
print("\nSatelliti che rimangono nel range:")
for sat in satellites_in_range:
    print(f"  - {sat.name}")
"""

""" SOLO SATELLITI SOPRA VANCOUVER E TOKYO
from skyfield.api import load, Topos
import networkx as nx
import matplotlib
matplotlib.use('MacOSX')  # Forza il backend nativo per macOS
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from datetime import timedelta
from math import radians

# URL per i TLE dei satelliti Starlink
url = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle'

# Scarica i dati TLE
print("Scaricando i dati TLE...")
satellites = load.tle_file(url)

print(f"Caricati {len(satellites)} satelliti.")

# Definisci le città
vancouver = Topos(latitude_degrees=49.2827, longitude_degrees=-123.1207)  # Vancouver
tokyo = Topos(latitude_degrees=35.6762, longitude_degrees=139.6503)  # Tokyo


# Tempo attuale
ts = load.timescale()
time = ts.now()

# Trova i satelliti visibili sopra Vancouver e Tokyo
visible_satellites_vancouver = []
visible_satellites_tokyo = []

for sat in satellites:
    # Per Vancouver
    difference_vancouver = sat - vancouver
    topocentric_vancouver = difference_vancouver.at(time)
    alt_vancouver, az_vancouver, distance_vancouver = topocentric_vancouver.altaz()

    if alt_vancouver.degrees > 10.0:  # Altitudine > 10° sopra Vancouver
        visible_satellites_vancouver.append(sat)

    # Per Tokyo
    difference_tokyo = sat - tokyo
    topocentric_tokyo = difference_tokyo.at(time)
    alt_tokyo, az_tokyo, distance_tokyo = topocentric_tokyo.altaz()

    if alt_tokyo.degrees > 10.0:  # Altitudine > 10° sopra Tokyo
        visible_satellites_tokyo.append(sat)

# Debug: Controlla i satelliti visibili
print(f"Satelliti visibili sopra Vancouver: {len(visible_satellites_vancouver)}")
print(f"Satelliti visibili sopra Tokyo: {len(visible_satellites_tokyo)}")

# Crea un grafo
G = nx.Graph()

# Aggiungi satelliti visibili come nodi
for sat in visible_satellites_vancouver + visible_satellites_tokyo:
    G.add_node(sat.name, lat=sat.at(time).subpoint().latitude.degrees, lon=sat.at(time).subpoint().longitude.degrees)


# Estrai latitudine e longitudine
vancouver_lat = vancouver.latitude.degrees
vancouver_lon = vancouver.longitude.degrees
tokyo_lat = tokyo.latitude.degrees
tokyo_lon = tokyo.longitude.degrees

# Calcola il punto centrale tra le due città
center_lat = (vancouver_lat + tokyo_lat) / 2
center_lon = (vancouver_lon + tokyo_lon) / 2

# Funzione per convertire longitudini negative in longitudini equivalenti (0°-360°)
def adjust_longitude(lon):
    if lon < 0:
        return lon + 360
    return lon

# Converti le longitudini di Vancouver e Tokyo nel range 0°-360°
vancouver_lon_adjusted = adjust_longitude(vancouver_lon)
tokyo_lon_adjusted = adjust_longitude(tokyo_lon)


# Crea una mappa 2D centrata sull'Oceano Pacifico
plt.figure(figsize=(12, 9))

# Definizione della mappa
m = Basemap(projection='merc',
            llcrnrlat=-20, urcrnrlat=70,  # Limiti latitudine
            llcrnrlon=110, urcrnrlon=270,  # Limiti longitudine
            resolution='i')  # Alta risoluzione

# Disegna le linee costiere e i confini dei paesi
m.drawcoastlines()
m.drawcountries()

# **Aggiungi meridiani e paralleli**
# Disegna i paralleli (latitudine)
parallels = range(-20, 71, 10)  # Intervallo ogni 10 gradi
m.drawparallels(parallels, labels=[True, False, False, False], color='lightgray', linewidth=0.5)

# Disegna i meridiani (longitudine)
meridians = range(110, 271, 10)  # Intervallo ogni 10 gradi
m.drawmeridians(meridians, labels=[False, False, False, True], color='lightgray', linewidth=0.5)


# Aggiungi Vancouver e Tokyo come città sulla mappa
cities = [
    {'name': 'Vancouver', 'lat': vancouver_lat, 'lon': vancouver_lon_adjusted, 'color': 'blue'},
    {'name': 'Tokyo', 'lat': tokyo_lat, 'lon': tokyo_lon_adjusted, 'color': 'green'}
]

# Aggiunta delle città con marker
for city in cities:
    x, y = m(city['lon'], city['lat'])  # Converte le coordinate in coordinate della mappa
    m.plot(x, y, marker='*', color=city['color'], markersize=6, label=city['name'])
    plt.text(x, y, city['name'], fontsize=12, ha='right', color=city['color'])


# Aggiungi i satelliti visibili sopra Vancouver
for sat in visible_satellites_vancouver:
    lat = sat.at(time).subpoint().latitude.degrees
    lon = adjust_longitude(sat.at(time).subpoint().longitude.degrees)  # Regola la longitudine
    x, y = m(lon, lat)  # Converte le coordinate in coordinate della mappa
    m.plot(x, y, marker='o', color='red', markersize=2)  # Satelliti visibili sopra Vancouver

# Aggiungi i satelliti visibili sopra Tokyo
for sat in visible_satellites_tokyo:
    lat = sat.at(time).subpoint().latitude.degrees
    lon = adjust_longitude(sat.at(time).subpoint().longitude.degrees)  # Regola la longitudine
    x, y = m(lon, lat)  # Converte le coordinate in coordinate della mappa
    m.plot(x, y, marker='o', color='orange', markersize=2)  # Satelliti visibili sopra Tokyo

# Aggiungi la legenda per distinguere satelliti e città
plt.legend(loc='lower left', fontsize=10)

# Mostra la mappa con il titolo
plt.title("Posizione dei satelliti visibili tra Vancouver e Tokyo", fontsize=16)
plt.show()


"""

""" SOLO SATELLITI SOPRA VANCOUVER IN 10 MIN
# Definisci Vancouver e Tokyo
vancouver = Topos(latitude_degrees=49.2827, longitude_degrees=-123.1207)  # Vancouver
tokyo = Topos(latitude_degrees=35.6895, longitude_degrees=139.6917)  # Tokyo

# Tempo attuale
ts = load.timescale()
start_time = ts.now()  # Tempo attuale
end_time = start_time + timedelta(minutes=5)  # Simula per 5 minuti

# Calcola i satelliti visibili e i loro tempi di visibilità
visible_vancouver = {}

# Trova i satelliti visibili
for satellite in satellites:
    t, events = satellite.find_events(vancouver, start_time, end_time, altitude_degrees=10.0)

    # Inizializza variabili
    rise_time = None
    set_time = None

    for ti, event in zip(t, events):
        if event == 0:  # Satellite sorge
            rise_time = ti
        elif event == 2:  # Satellite tramonta
            set_time = ti

    # Verifica che entrambi i tempi siano stati definiti
    if rise_time is not None and set_time is not None:
        # Calcola la durata in secondi
        duration_seconds = (set_time - rise_time) * 86400  # Durata in secondi

        # Calcola il tempo medio di passaggio
        avg_time = rise_time + (set_time - rise_time) / 2

        # Calcola la posizione media del satellite durante il passaggio
        difference = satellite - vancouver
        topocentric = difference.at(avg_time)
        alt, az, distance = topocentric.altaz()

        # Salva i dati del passaggio del satellite
        visible_vancouver[satellite.name] = {
            'rise_time': rise_time.utc_strftime('%Y-%m-%d %H:%M:%S'),
            'set_time': set_time.utc_strftime('%Y-%m-%d %H:%M:%S'),
            'duration_seconds': duration_seconds,
            'max_altitude_degrees': alt.degrees,
            'distance_km': distance.km,
        }



# Stampa i risultati
print(f"\nSatelliti visibili sopra Vancouver entro 10 minuti:{len(visible_vancouver)}")
for sat_name, data in visible_vancouver.items():
    print(f"\nSatellite: {sat_name}")
    print(f"  - Sorgere: {data['rise_time']} UTC")
    print(f"  - Tramontare: {data['set_time']} UTC")
    print(f"  - Durata: {data['duration_seconds']:.2f} secondi")
    print(f"  - Altitudine massima: {data['max_altitude_degrees']:.2f}°")
    print(f"  - Distanza minima: {data['distance_km']:.2f} km")
"""