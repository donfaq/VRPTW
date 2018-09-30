import os
import glob
import argparse

from VRPTW import *


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Solving VRPTW with heuristics')
    parser.add_argument('problem_file', type=str, help='Problem file (in Solomon format)')
    parser.add_argument('--benchmark', type=bool, default=False, help="Run solvers on all files in instances folder")
    return parser.parse_args()


if __name__ == '__main__':
    args = arguments()
    if args.benchmark:
        for file in glob.glob('instances/*.txt'):
            if not os.path.exists('solutions'):
                os.mkdir('solutions')
            problem = SolomonFormatParser(file).get_problem()
            solution = IteratedLocalSearch(problem).execute()
            with open(f"""solutions/{file.split(os.sep)[1].split(".")[0]}.sol""", 'w') as f:
                print(file.split(os.sep)[1].split(".")[0], problem.obj_func(solution))
                f.write(problem.print_canonical(solution))
    else:
        assert os.path.exists(args.problem_file), "Problem file doesn't exist"
        problem = SolomonFormatParser(args.problem_file).get_problem()
        print(problem)
        solution = IteratedLocalSearch(problem).execute()
        # solution = GuidedLocalSearch(problem).execute()
