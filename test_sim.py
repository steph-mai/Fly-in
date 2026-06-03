from pathlib import Path
from src.simulation_factory import SimulationFactory


def main() -> None:
    print("Chargement de la configuration...")

    map_path = Path("maps/challenger/01_the_impossible_dream.txt")

    sim, error_msg = SimulationFactory.build_from_file(map_path)

    if error_msg:
        print(error_msg)
        return

    if sim:
        print("Lancement de la simulation dans le terminal...")
        sim.run_simulation()


if __name__ == "__main__":
    main()
