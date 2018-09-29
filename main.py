import os
import argparse

from VRPTW import *


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Solving VRPTW with heuristics')
    parser.add_argument('problem_file', type=str, help='Problem file (in Solomon format)')
    return parser.parse_args()


if __name__ == '__main__':
    args = arguments()
    assert os.path.exists(args.problem_file), "Problem file doesn't exist"
    problem = SolomonFormatParser(args.problem_file).get_problem()
    print(problem)
    solution = IteratedLocalSearch(problem).execute()
    print(problem.print_canonical(solution))
    print("Total distance:", problem.obj_func(solution))
