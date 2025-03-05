import numpy as np

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
