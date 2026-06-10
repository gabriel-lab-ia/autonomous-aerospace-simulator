from aerospace_sim.evaluation.controller_benchmark import run_controller_benchmark


if __name__ == "__main__":
    comparison = run_controller_benchmark()
    print(comparison.to_string(index=False))
