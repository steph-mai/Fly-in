# Test Map : The Highway Detour
# Objectif : Prouver que l'algorithme sacrifie de la distance pour gagner du temps.
nb_drones: 15

# --- LES HUBS ---
start_hub: start_base 0 0 [color=green]
hub: split_zone 1 0 [color=yellow max_drones=15]

# La Voie Express (Chemin le plus court, mais goulot d'étranglement)
hub: main_1 2 0 [color=red max_drones=1]
hub: main_2 3 0 [color=red max_drones=1]

# La Voie de Contournement (Plus longue, mais très large)
hub: detour_1 1 1 [color=blue max_drones=10]
hub: detour_2 2 1 [color=blue max_drones=10]
hub: detour_3 3 1 [color=blue max_drones=10]

end_hub: destination 4 0 [color=green]

# --- LES CONNEXIONS ---
connection: start_base-split_zone [max_link_capacity=5]

# Connexions Voie Express (Capacité de 1 : très lent)
connection: split_zone-main_1 [max_link_capacity=1]
connection: main_1-main_2 [max_link_capacity=1]
connection: main_2-destination [max_link_capacity=1]

# Connexions Voie de Contournement (Capacité de 5 : très fluide)
connection: split_zone-detour_1 [max_link_capacity=5]
connection: detour_1-detour_2 [max_link_capacity=5]
connection: detour_2-detour_3 [max_link_capacity=5]
connection: detour_3-destination [max_link_capacity=5]
