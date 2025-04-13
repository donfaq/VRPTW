import argparse
import os

from .structure import Problem
from .parser import SolomonFormatParser


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Solutions validator for VRPTW problem')
    parser.add_argument('problem', type=str, help='Problem file (in Solomon format)')
    parser.add_argument('solution', type=str, default=False, help="Solution file")
    return parser.parse_args()


def check_route(problem, line):
    route_customers, timestamps = line.split()[::2], line.split()[1::2]
    assert route_customers[0] == route_customers[-1] == '0', "Each route should begins and ends at the DEPOT"
    customers = []
    for c, t in zip(route_customers, timestamps):
        customer = list(filter(lambda x: x.number == int(c), problem.customers))[0]
        customers.append(customer)
        customer.is_serviced = True
        assert customer.ready_time <= float(t) < customer.due_date, f"Time violation for customer {c}"
    assert sum([x.demand for x in customers]) <= problem.vehicle_capacity, f"Capacity violation for line {line}"


def check_solution(problem: Problem, solution_file: str):
    with open(solution_file, 'r') as f:
        routes = f.readlines()
    assert len(routes) <= problem.vehicle_number, "Vehicle number violation"

    for route in routes:
        check_route(problem, route)
    assert all(map(lambda x: x.is_serviced, problem.customers)), "Each customer must be served"


if __name__ == '__main__':
    args = arguments()
    assert os.path.exists(args.problem), "Incorrect problem file"
    assert os.path.exists(args.solution), "Incorrect solution file"
    problem = SolomonFormatParser(os.path.abspath(args.problem)).get_problem()
    check_solution(problem, os.path.abspath(args.solution))
    print("Well done")
