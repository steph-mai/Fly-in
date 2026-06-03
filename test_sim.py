import sys
from pathlib import Path
from src.simulation_factory import SimulationFactory


def main() -> None:
    # 1. On vérifie que le chemin de la carte est bien passé en argument
    if len(sys.argv) != 2:
        # On écrit sur "stderr" (la sortie d'erreur) pour ne pas polluer
        # la sortie standard "stdout" lue par les correcteurs automatiques.
        print("Usage: python3 test_sim.py <path_to_map.json>", file=sys.stderr)
        sys.exit(1)

    map_path = Path(sys.argv[1])

    # 2. Utilisation de la Factory (Totalement silencieuse)
    sim, error_msg = SimulationFactory.build_from_file(map_path)

    # 3. Si l'usine renvoie une erreur, on l'affiche sur stderr et on quitte
    if error_msg:
        print(error_msg, file=sys.stderr)
        sys.exit(1)

    # 4. Si tout est valide, on lance l'algorithme pur
    if sim:
        sim.run_simulation()


if __name__ == "__main__":
    main()
