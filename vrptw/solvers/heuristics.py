from ..structure import Problem, Route
import itertools
import logging

logger = logging.getLogger()


class DummyHeuristic:
    def __init__(self, problem: Problem):
        self.problem: Problem = problem

    def get_solution(self):
        """Solution sampled from customer list, sorted by demand"""

        def get_available_customers():
            return sorted(
                filter(lambda x: not x.is_serviced, self.problem.customers),
                key=lambda x: x.due_date,
            )

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


def two_opt(a, i, j):
    if i == 0:
        return a[j:i:-1] + [a[i]] + a[j + 1 :]
    return a[:i] + a[j : i - 1 : -1] + a[j + 1 :]


def cross(a, b, i, j):
    return a[:i] + b[j:], b[:j] + a[i:]


def insertion(a, b, i, j):
    # print(a, b, i, j)
    if len(a) == 0:
        return a, b
    while i >= len(a):
        i -= len(a)
    return a[:i] + a[i + 1 :], b[:j] + [a[i]] + b[j:]


def swap(a, b, i, j):
    # print(a, b, i, j)
    if i >= len(a) or j >= len(b):
        return a, b
    a, b = a.copy(), b.copy()
    a[i], b[j] = b[j], a[i]
    return a, b


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
                for k, j in itertools.combinations(range(len(route.customers)), 2):
                    new_route = Route(self.problem, two_opt(route.customers, k, j))
                    if new_route.is_feasible:
                        if new_route.total_distance < route.total_distance:
                            new_solution[i] = new_route
                            is_stucked = False
        return new_solution


class IteratedLocalSearch(LocalSearch):
    def __init__(self, problem: Problem, obj_func=None):
        super().__init__(problem)
        if not obj_func:
            obj_func = self.problem.obj_func
        self.obj_func = obj_func
        self.initial_solution = DummyHeuristic(problem).get_solution()

    def perturbation(self, routes: list) -> list:
        best = [Route(self.problem, route.customers) for route in routes]
        is_stucked = False
        while not is_stucked:
            is_stucked = True
            # Для всех возможных пар маршрутов
            for i, j in itertools.combinations(range(len(best)), 2):
                # Для всех возможных индексов в двух маршрутах
                for k, l in itertools.product(range(len(best[i].customers) + 2), range(len(best[j].customers) + 2)):
                    for func in [cross, insertion, swap]:
                        c1, c2 = func(best[i].customers, best[j].customers, k, l)
                        r1, r2 = Route(self.problem, c1), Route(self.problem, c2)
                        if r1.is_feasible and r2.is_feasible:
                            if r1.total_distance + r2.total_distance < best[i].total_distance + best[j].total_distance:
                                best[i] = r1
                                best[j] = r2
                                is_stucked = False
            best = list(filter(lambda x: len(x.customers) != 0, best))
        return best

    def execute(self):
        best = self.optimize(self.initial_solution)
        print("Local search solution:")
        print(self.problem.print_canonical(best))
        print("Total distance", self.obj_func(best))

        is_stucked = False
        while not is_stucked:
            is_stucked = True
            new_solution = self.perturbation(best)
            new_solution = self.optimize(new_solution)
            if self.obj_func(new_solution) < self.obj_func(best):
                is_stucked = False
                best = list(filter(lambda x: len(x.customers) != 0, new_solution))
                print("ILS step")
                print(self.problem.print_canonical(best))
                print("Total distance", self.obj_func(best))
        return best
