import argparse
import logging
import pathlib

from vrptw import SolomonFormatParser, IteratedLocalSearch

logging.basicConfig(level="DEBUG")
log = logging.getLogger(__name__)


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Solving VRPTW with heuristics")
    parser.add_argument(
        "input", type=str, help="Path to input problem file/folder with problem files in Solomon format"
    )
    parser.add_argument("--output", type=str, default="solutions", help="Path to output folder")
    return parser.parse_args()


def process_file(input_file: pathlib.Path, output_folder: pathlib.Path):
    log.info("Processing file: '%s'", input_file)
    problem = SolomonFormatParser(input_file).get_problem()
    solution = IteratedLocalSearch(problem).execute()
    solution_file_path = output_folder.joinpath(input_file.stem + ".sol")
    with open(solution_file_path, "w") as solution_file:
        log.info("Problem name: %s, solution (objective function value): %f", problem.name, problem.obj_func(solution))
        solution_file.write(problem.print_canonical(solution))


def process_folder(input_folder: pathlib.Path, output_folder: pathlib.Path):
    for problem_file_path in input_folder.glob("*.txt"):
        process_file(problem_file_path, output_folder)


if __name__ == "__main__":
    args = arguments()
    log.info("Application started")

    out_folder = pathlib.Path(args.output).resolve()
    out_folder.mkdir(exist_ok=False)
    log.info("Output folder: '%s'", out_folder)

    input_path = pathlib.Path(args.input).resolve()
    if input_path.is_file():
        process_file(input_path, out_folder)
    elif input_path.is_dir():
        process_folder(input_path, out_folder)
    else:
        raise ValueError("Input param should be path to file/folder")
