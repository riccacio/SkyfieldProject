import numpy as np


def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Raggio medio della Terra in km
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    distance = R * c

    return distance


def haversine_with_altitude(lat1, lon1, alt1, lat2, lon2, alt2):
    R = 6371  # Raggio medio della Terra in km
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    dalt = alt2 - alt1

    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    distance = R * c

    total_distance = np.sqrt(distance**2 + dalt**2)

    return total_distance


import numpy as np


def euclidean_distance(lat1, lon1, alt1, lat2, lon2, alt2):
    R = 6378.137 # Raggio medio della Terra in km

    # Converte latitudine e longitudine in radianti
    lat1_rad = np.radians(lat1)
    lon1_rad = np.radians(lon1)
    lat2_rad = np.radians(lat2)
    lon2_rad = np.radians(lon2)

    # Calcola le coordinate cartesiane per il primo punto
    x1 = (R + alt1) * np.cos(lat1_rad) * np.cos(lon1_rad)
    y1 = (R + alt1) * np.cos(lat1_rad) * np.sin(lon1_rad)
    z1 = (R + alt1) * np.sin(lat1_rad)

    # Calcola le coordinate cartesiane per il secondo punto
    x2 = (R + alt2) * np.cos(lat2_rad) * np.cos(lon2_rad)
    y2 = (R + alt2) * np.cos(lat2_rad) * np.sin(lon2_rad)
    z2 = (R + alt2) * np.sin(lat2_rad)

    # Calcola la distanza euclidea
    distance = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)

    return distance

# calcolo latenza
# per calcolare la latenza devo prendere la distanza tra due satelliti e dividere per la velocità della luce
def latency_calculation(distance):
    c = 299792.458 # velocità della luce in km/s
    return distance / c

# calcolo throughput
# per calcolare il throughput devo utilizzare la capacità del canale, usando il teoteore di Shannon
# C = B * log2(1 + S/N)
def throughput(bandwidth, snr):
    return bandwidth * np.log2(1 + snr)