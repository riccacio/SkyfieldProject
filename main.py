from skyfield.toposlib import Topos

from test import Test

#city1_name = "Vancouver"
#city1 = Topos(latitude_degrees=49.2827, longitude_degrees=-123.1207)

city1_name = "New Tork"
city1 = Topos(latitude_degrees=40.7128, longitude_degrees=-74.0060) # New York

citiy2 = ("London", Topos(latitude_degrees=51.5074, longitude_degrees=-0.1278), True)

#cities = [
    #("London", Topos(latitude_degrees=51.5074, longitude_degrees=-0.1278), True),
    #("Bahrain", Topos(latitude_degrees=26.2010, longitude_degrees=50.6070), False),
    #("Cape Town", Topos(latitude_degrees=-33.9249, longitude_degrees=18.4241), False),
    #("Mumbai", Topos(latitude_degrees=19.0760, longitude_degrees=72.8777), True),
    #("San Francisco", Topos(latitude_degrees=37.7749, longitude_degrees=-122.4194), True),
    #("Sao Paulo", Topos(latitude_degrees=-23.5505, longitude_degrees=-46.6333), True),
    #("Singapore", Topos(latitude_degrees=1.3521, longitude_degrees=103.8198), True),
    #("Istanbul", Topos(latitude_degrees=41.0082, longitude_degrees=28.9784), False),
    #("Sydney", Topos(latitude_degrees=-33.8688, longitude_degrees=151.2093), True),
    #("Tokyo", Topos(latitude_degrees=35.6895, longitude_degrees=139.6917), True)]


t = Test()
# Test 1: Selezionare due città e variare il LISL_range
#LISL_range = [659.5, 1319, 1500, 1700, 2500, 5016]
LISL_range = [2500]
t.test_city_pair_with_lisl_range(city1_name, city1, "London", Topos(51.5074, -0.1278), False, LISL_range)

# Test 2: Calcolare RTT per più città con LISL fisso
#t.test_multiple_cities_with_fixed_lisl(city1_name, city1, cities, LISL_range[0])
