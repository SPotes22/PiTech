import pathlib


def run_scan() -> None:
    project_root = pathlib.Path(__file__).resolve().parents[2]
    print(f"[scanner] Simulación de escaneo sobre: {project_root}")
    print("[scanner] No se detectaron hallazgos críticos en la simulación.")


if __name__ == "__main__":
    run_scan()
