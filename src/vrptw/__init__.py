import os
import pathlib
import argparse
import logging

from .parser import SolomonFormatParser
from .heuristics import IteratedLocalSearch


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

    assert os.path.exists(problem_file_path.exists()), "Problem file doesn't exist"
    
    problem = SolomonFormatParser().get_problem(problem_file_path)
    solution = IteratedLocalSearch(problem).execute()

    with open(output_file_path, 'w') as f:
        f.write(problem.print_canonical(solution))
