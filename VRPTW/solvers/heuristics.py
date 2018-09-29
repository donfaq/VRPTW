from VRPTW.structure import Problem, Route
import itertools


class DummyHeuristic:
    def __init__(self, problem: Problem):
        self.problem: Problem = problem

    def get_solution(self):
        def get_available_customers():
            return sorted(filter(lambda x: not x.is_serviced, self.problem.customers), key=lambda x: x.demand)

        solution = []
        while len(get_available_customers()) > 0:
            customers = get_available_customers()
            route = []
            for customer in customers:
                if Route(self.problem, route + [customer]).is_feasible:
                    customer.is_serviced = True
                    route.append(customer)
            solution.append(Route(self.problem, route))
        return solution


def two_opt(customers, i, j):
    if j - i > 1:
        return customers[:i] + [customers[j]] + customers[j - 1:i:-1] + [customers[i]] + customers[j + 1:]
    return customers[:i] + [customers[j]] + [customers[i]] + customers[j + 1:]


class LocalSearch:
    def __init__(self, problem: Problem):
        self.problem: Problem = problem

    def optimize(self, solution: list) -> list:
        new_solution = list(solution)
        for i in range(len(new_solution)):
            is_stucked = False
            while not is_stucked:
                route = new_solution[i]
                is_stucked = True
                for k, j in itertools.combinations(range(len(route.customers) - 1), 2):
                    new_route = Route(self.problem, two_opt(route.customers, k, j))
                    if new_route.is_feasible:
                        if new_route.total_distance < route.total_distance:
                            new_solution[i] = new_route
                            is_stucked = False
        return new_solution


class IteratedLocalSearch(LocalSearch):
    def __init__(self, problem: Problem):
        super().__init__(problem)
        self.initial_solution = DummyHeuristic(problem).get_solution()

    def execute(self):
        best = self.optimize(self.initial_solution)
        print('\n'.join(r.canonical_view for r in best))
        print("Total distance", sum(map(lambda x: x.total_distance, best)))
