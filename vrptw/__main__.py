import os
import glob
import argparse
import logging

from . import SolomonFormatParser, IteratedLocalSearch


logging.basicConfig(
    format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(pathname)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Solving VRPTW with heuristics')
    parser.add_argument('problem_file', type=str, help='Problem file (in Solomon format)')
    parser.add_argument('--benchmark', type=bool, default=False, help="Run solvers on all files in instances folder")
    return parser.parse_args()


if __name__ == '__main__':
    args = arguments()
    if not os.path.exists('solutions'):
        os.mkdir('solutions')
    if args.benchmark:
        for file in glob.glob('instances/*.txt'):
            problem = SolomonFormatParser(file).get_problem()
            solution = IteratedLocalSearch(problem).execute()
            with open(f"""solutions/{file.split(os.sep)[1].split(".")[0]}.sol""", 'w') as f:
                logger.info(file.split(os.sep)[1].split(".")[0], problem.obj_func(solution))
                f.write(problem.print_canonical(solution))
    else:
        assert os.path.exists(args.problem_file), "Problem file doesn't exist"
        problem = SolomonFormatParser(args.problem_file).get_problem()
        logger.info(problem)
        solution = IteratedLocalSearch(problem).execute()

        with open(f"""solutions/{args.problem_file.split(os.sep)[-1].split(".")[0]}.sol""", 'w') as f:
            f.write(problem.print_canonical(solution))
