import pathlib
import argparse
import logging

from .solver import VRPTWSolver

logging.basicConfig(
    format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(pathname)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Solving VRPTW with ILS')
    parser.add_argument('problem', type=str, help="Path to the problem file (in Solomon format)")
    parser.add_argument('--out', type=str, default="solution.txt", help="Output file path. Defauts to './solution.txt'")
    return parser.parse_args()


def main():
    args = arguments()

    problem_file_path = pathlib.Path(args.problem).resolve()
    output_file_path = pathlib.Path(args.out).resolve()

    solver = VRPTWSolver(problem_file_path)
    solver.solve()
    solver.save_solution(output_file_path)


if __name__ == "__main__":
    main()
