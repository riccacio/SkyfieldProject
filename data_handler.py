import csv
import matplotlib.pyplot as plt

def save_graph_to_csv(graph):
    with open("nodes.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Satellite", "Latitudine", "Longitudine"])
        for node, data in graph.nodes(data=True):
            writer.writerow([node, data["lat"], data["lon"]])

    with open("edges.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Satellite1", "Satellite2", "Distanza_km"])
        for u, v, data in graph.edges(data=True):
            writer.writerow([u, v, data["weight"]])

def save_map_as_png(filename="map.png"):
    plt.savefig(filename, dpi=600, bbox_inches='tight')
    print(f"Mappa salvata come {filename}")