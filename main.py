from skyfield.toposlib import Topos

from test import Test

#city1_name = "Vancouver"
#city1 = Topos(latitude_degrees=49.1539, longitude_degrees=-123.0650)


city1_name = "New Tork"
city1 = Topos(latitude_degrees=40.7128, longitude_degrees=-74.0060) # New York

cities = [
    ("San Francisco", Topos(latitude_degrees=37.7749, longitude_degrees=-122.4194), True),
    ("Tokyo", Topos(latitude_degrees=35.6895, longitude_degrees=139.6917), True),
    ("London", Topos(latitude_degrees=51.3026, longitude_degrees=-0.0739), False),
    ("Sydney", Topos(latitude_degrees=-33.8688, longitude_degrees=151.2093), True),
    ("Singapore", Topos(latitude_degrees=1.3521, longitude_degrees=103.8198), True),
    ("Sao Paulo", Topos(latitude_degrees=-23.5505, longitude_degrees=-46.6333), True),
    ("Mumbai", Topos(latitude_degrees=19.0760, longitude_degrees=72.8777), True),
    ("CapeTown", Topos(latitude_degrees=-33.9249, longitude_degrees=18.4241), False)
    #("Istanbul", Topos(latitude_degrees=41.0082, longitude_degrees=28.9784), False),
]

# RTT terrestre (ms) da Vancouver
rtt_terrestrial = [
    23.031, # San Francisco
    104.814, # Tokyo
    135.861, # London
    141.332, # Sydney
    166.346, # Singapore
    176.081, # Sao Paulo
    252.229,  # Mumbai
    279.845 # CapeTown
    #180.855, # Istanbul
]


#fonte sito: https://wondernetwork.com/pings

t = Test()
# Test 1: Selezionare due città e variare il LISL_range
LISL_range = [1300, 1700, 2500, 3800, 5000]
plusGrid = True
load_factor = 0.15
t.test_city_pair_with_lisl_range(city1_name, city1, "London", cities[2][1], False, LISL_range, plusGrid, load_factor)

# Test 2: Calcolare RTT per più città con LISL fisso
#t.test_multiple_cities_with_fixed_lisl(city1_name, city1, cities, LISL_range[0], rtt_terrestrial, plusGrid, load_factor)
