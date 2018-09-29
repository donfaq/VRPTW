from VRPTW.structure import Problem, Customer


class SolomonFormatParser:
    """Parsing file in Solomon format
    https://www.sintef.no/projectweb/top/vrptw/solomon-benchmark/documentation/
    """

    def __init__(self, problem_file):
        self.problem_file = problem_file

    def get_problem(self) -> Problem:
        with open(self.problem_file, 'r') as f:
            lines = list(map(lambda l: l.replace('\n', '').split(), f.readlines()))
        name = lines[0][0]
        vehicle_number, vehicle_capacity = list(map(int, lines[4]))
        customers = []
        for line in lines[9:]:
            customers.append(Customer(*list(map(int, line))))
        return Problem(name, customers, vehicle_number, vehicle_capacity)
