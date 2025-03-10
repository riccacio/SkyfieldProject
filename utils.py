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
    c = 299792458 # velocità della luce in km/s
    return distance*1000 / c

# calcolo throughput
# per calcolare il throughput devo utilizzare la capacità del canale, usando il teorema di Shannon

def calculate_capacity(P_t, G_t, G_r, lambda_, d, B, N):
    P_r = P_t * G_t * G_r * (lambda_ / (4 * np.pi * d))**2  # Potenza ricevuta
    SNR = P_r / N  # Rapporto segnale-rumore
    C = B * np.log2(1 + SNR)  # Formula di Shannon
    return C / 1e9  # converto in Gbps






# Esempio di utilizzo:
# Supponiamo di avere un percorso definito (lista di nomi satellitari) e un grafo G con le informazioni dei satelliti.
# Inoltre, definiamo le coordinate (latitudine, longitudine) per le città di origine e destinazione.
# (I valori reali dovranno essere estratti dal tuo sistema, questo è solo un esempio.)
path = ["Sat1", "Sat2", "Sat3"]
city_origin = (49.2827, -123.1207)  # Vancouver (lat, lon)
city_dest = (35.6895, 139.6917)  # Tokyo (lat, lon)

# Supponiamo che G sia il grafo che hai creato e popolato con i nodi satellitari
# (ad esempio, G = sat_graph.get_graph())

# Calcola il throughput totale per Ka e Ku band
total_ka, total_ku = calculate_total_comm_throughput(path, G, city_origin, city_dest,
                                                     isl_params, ground_ka_params, ground_ku_params)