from pathlib import Path
from src.simulation_factory import SimulationFactory


def main() -> None:
    print("Chargement de la configuration...")

    map_path = Path("maps/medium/01_dead_end_trap.txt")

    sim, error_msg = SimulationFactory.build_from_file(map_path)

    # 3. Si l'usine renvoie une erreur, on l'affiche et on s'arrête
    if error_msg:
        print(error_msg)
        return

    if sim:
        print("Lancement de la simulation dans le terminal...")
        sim.run_simulation()


if __name__ == "__main__":
    main()
