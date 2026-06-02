from typing import Any
from src.map_graph import MapGraph

# 1. On crée nos fausses classes pour simuler le comportement de Pydantic
class MockZone:
    def __init__(self, name: str, zone_type: str = "normal"):
        self.name = name
        self.zone = zone_type

class MockConfig:
    """Un faux fichier de configuration pour tromper le __init__ de MapGraph"""
    def __init__(self):
        # On donne des listes vides pour que le __init__ ne plante pas
        self.zones = []
        self.connections = []
        self.nb_drones = 10 # Si jamais ton constructeur en a besoin

def run_tests() -> None:
    print("--- DÉMARRAGE DES TESTS DE DIJKSTRA ---\n")

    # ÉTAPE A : Création de la fausse carte

    # Au lieu de passer None, on passe notre fausse configuration
    fake_config = MockConfig()
    graph = MapGraph(map_config=fake_config)

    # À ce stade, graph est initialisé, mais vide.
    # On écrase ses variables avec notre scénario de test (le losange)
    graph.zones = {
        "Start": MockZone("Start"),
        "A": MockZone("A", zone_type="normal"),       # Coût = 1
        "B": MockZone("B", zone_type="restricted"),   # Coût = 2
        "End": MockZone("End")
    }

    graph.graph_adj = {
        "Start": {"A": 1, "B": 1},
        "A": {"Start": 1, "End": 1},
        "B": {"Start": 1, "End": 1},
        "End": {"A": 1, "B": 1}
    }

    # ÉTAPE B : Lancement des scénarios

    print("TEST 1 : Route dégagée (Devrait passer par A car plus rapide)")
    path1 = graph.find_best_path("Start", "End", blocked_zones=())
    print(f"Résultat : {path1}")
    assert path1 == ["Start", "A", "End"], "Erreur Test 1"
    print("-> ✅ Succès\n")

    print("TEST 2 : Trafic sur A (Devrait contourner par B)")
    blocked = {"A"}
    path2 = graph.find_best_path("Start", "End", blocked_zones=blocked)
    print(f"Résultat : {path2}")
    assert path2 == ["Start", "B", "End"], "Erreur Test 2"
    print("-> ✅ Succès\n")

    print("TEST 3 : Tout est bouché (Devrait renvoyer une liste vide)")
    blocked_all = {"A", "B"}
    path3 = graph.find_best_path("Start", "End", blocked_zones=blocked_all)
    print(f"Résultat : {path3}")
    assert path3 == [], "Erreur Test 3"
    print("-> ✅ Succès\n")

    print("TEST 4 : Départ == Arrivée")
    path4 = graph.find_best_path("Start", "Start", blocked_zones=())
    print(f"Résultat : {path4}")
    assert path4 == ["Start"], "Erreur Test 4"
    print("-> ✅ Succès\n")

    print("--- TOUS LES TESTS SONT AU VERT ! ---")

if __name__ == "__main__":
    run_tests()






