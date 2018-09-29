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


def two_opt(a, i, j):
    if i == 0:
        return a[j:i:-1] + [a[i]] + a[j + 1:]
    return a[:i] + a[j:i - 1:-1] + a[j + 1:]


def cross(a, b, i, j):
    return a[:i] + b[j:], b[:j] + a[i:]


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
    def __init__(self, problem: Problem):
        super().__init__(problem)
        self.initial_solution = DummyHeuristic(problem).get_solution()

    def perturbation(self, routes: list) -> list:
        best = [Route(self.problem, route.customers) for route in routes]
        is_stucked = False
        while not is_stucked:
            is_stucked = True
            # Для всех возможных пар маршрутов
            for i, j in itertools.combinations(range(len(best)), 2):
                # Для всех возможных индексов в двух маршрутах
                for k, l in itertools.product(range(len(best[i].customers)), range(len(best[j].customers))):
                    c1, c2 = cross(best[i].customers, best[j].customers, k, l)
                    r1, r2 = Route(self.problem, c1), Route(self.problem, c2)
                    if r1.is_feasible and r2.is_feasible:
                        if r1.total_distance + r2.total_distance < best[i].total_distance + best[j].total_distance:
                            best[i] = r1
                            best[j] = r2
                            is_stucked = False
        return best

    def execute(self):
        best = self.optimize(self.initial_solution)
        print("Local search solution:")
        print('\n'.join(r.canonical_view for r in best))
        print("Total distance", self.problem.obj_func(best))

        is_stucked = False
        while not is_stucked:
            is_stucked = True
            new_solution = self.perturbation(best)
            new_solution = self.optimize(new_solution)
            if self.problem.obj_func(new_solution) < self.problem.obj_func(best):
                print('еее')
                is_stucked = False
                best = list(filter(lambda x: len(x.customers) != 0, new_solution))
        return best
