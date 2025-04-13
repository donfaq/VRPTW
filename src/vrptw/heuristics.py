import itertools
import logging

from .structure import Problem, Route

logger = logging.getLogger()


class DummyHeuristic:
    """
    Simple heuristic for creating initial VRPTW solution.
    Creates a solution by sorting customers by service window end time
    and sequentially adding them to routes.
    """
    def __init__(self, problem: Problem):
        # Initialize with problem instance
        self.problem: Problem = problem

    def get_solution(self):
        """
        Creates initial solution for VRPTW problem.
        Returns a list of routes, where each route is a list of customers
        sorted by service window end time.
        """
        def get_available_customers():
            """
            Returns a list of unserviced customers sorted by service window end time.
            """
            return sorted(
                filter(lambda x: not x.is_serviced, self.problem.customers),
                key=lambda x: x.due_date,
            )

        solution = []  # List to store routes
        # While there are unserviced customers
        while len(get_available_customers()) > 0:
            customers = get_available_customers()  # Get available customers
            route = []  # Create new route
            # Add customers to route while possible
            for customer in customers:
                if Route(self.problem, route + [customer]).is_feasible:
                    customer.is_serviced = True
                    route.append(customer)
            solution.append(Route(self.problem, route))
        return solution


def two_opt(a, i, j):
    """
    Applies 2-opt operator to list a.
    Reverses subsequence between indices i and j.
    Used for local search in route.
    
    Args:
        a: list of route elements
        i: start index
        j: end index
    
    Returns:
        New list with reversed subsequence
    """
    if i == 0:
        return a[j:i:-1] + [a[i]] + a[j + 1 :]
    return a[:i] + a[j : i - 1 : -1] + a[j + 1 :]


def cross(a, b, i, j):
    """
    Exchanges subsequences between two routes.
    Cuts routes a and b at points i and j respectively and exchanges their tails.
    
    Args:
        a: first route
        b: second route
        i: cut point in first route
        j: cut point in second route
    
    Returns:
        Two new routes after subsequence exchange
    """
    return a[:i] + b[j:], b[:j] + a[i:]


def insertion(a, b, i, j):
    """
    Inserts customer from route a to route b.
    Removes customer at index i from route a and inserts it into route b at position j.
    
    Args:
        a: source route
        b: target route
        i: customer index in source route
        j: insertion position in target route
    
    Returns:
        Two new routes after insertion operation
    """
    if len(a) == 0:
        return a, b
    while i >= len(a):
        i -= len(a)
    return a[:i] + a[i + 1 :], b[:j] + [a[i]] + b[j:]


def swap(a, b, i, j):
    """
    Exchanges customers between two routes.
    Swaps customers at indices i and j in routes a and b respectively.
    
    Args:
        a: first route
        b: second route
        i: index in first route
        j: index in second route
    
    Returns:
        Two new routes after customer exchange
    """
    if i >= len(a) or j >= len(b):
        return a, b
    a, b = a.copy(), b.copy()
    a[i], b[j] = b[j], a[i]
    return a, b


class LocalSearch:
    """
    Class for local search in VRPTW solution.
    Applies 2-opt operator to each route to improve solution.
    """
    def __init__(self, problem: Problem):
        # Initialize with problem instance
        self.problem: Problem = problem

    def optimize(self, solution: list) -> list:
        """
        Optimizes solution using local search.
        Applies 2-opt operator to each route while improvement is possible.
        
        Args:
            solution: initial solution (list of routes)
        
        Returns:
            Optimized solution
        """
        new_solution = list(solution)  # Create solution copy
        # Optimize each route
        for i in range(len(new_solution)):
            is_stucked = False
            # While improvement is possible
            while not is_stucked:
                route = new_solution[i]
                is_stucked = True
                # Try all possible index pairs
                for k, j in itertools.combinations(range(len(route.customers)), 2):
                    # Try to apply 2-opt
                    new_route = Route(self.problem, two_opt(route.customers, k, j))
                    if new_route.is_feasible:
                        if new_route.total_distance < route.total_distance:
                            new_solution[i] = new_route
                            is_stucked = False
        return new_solution


class IteratedLocalSearch(LocalSearch):
    """
    Class for Iterated Local Search (ILS).
    Extends basic local search by adding perturbation phase to escape local optima.
    """
    def __init__(self, problem: Problem, obj_func=None):
        # Initialize base class
        super().__init__(problem)
        # Set objective function
        if not obj_func:
            obj_func = self.problem.obj_func
        self.obj_func = obj_func
        # Create initial solution
        self.initial_solution = DummyHeuristic(problem).get_solution()

    def perturbation(self, routes: list) -> list:
        """
        Perturbation phase in ILS.
        Applies various operators (cross, insertion, swap) to route pairs
        to create new solution different from current one.
        
        Args:
            routes: current solution (list of routes)
        
        Returns:
            New solution after perturbation
        """
        best = [Route(self.problem, route.customers) for route in routes]
        is_stucked = False
        # While improvement is possible
        while not is_stucked:
            is_stucked = True
            # Try all possible route pairs
            for i, j in itertools.combinations(range(len(best)), 2):
                # Try all possible indices in routes
                for k, l in itertools.product(range(len(best[i].customers) + 2), range(len(best[j].customers) + 2)):
                    # Try different operators
                    for func in [cross, insertion, swap]:
                        c1, c2 = func(best[i].customers, best[j].customers, k, l)
                        r1, r2 = Route(self.problem, c1), Route(self.problem, c2)
                        # Check feasibility and improvement
                        if r1.is_feasible and r2.is_feasible:
                            if r1.total_distance + r2.total_distance < best[i].total_distance + best[j].total_distance:
                                best[i] = r1
                                best[j] = r2
                                is_stucked = False
            # Remove empty routes
            best = list(filter(lambda x: len(x.customers) != 0, best))
        return best

    def execute(self):
        """
        Main method for executing Iterated Local Search.
        Alternates between local search and perturbation phases until local optimum is reached.
        
        Returns:
            Best found solution
        """
        # Initial optimization
        best = self.optimize(self.initial_solution)
        logger.info("Local search solution:")
        logger.info(self.problem.print_canonical(best))
        logger.info("Total distance %s", self.obj_func(best))

        is_stucked = False
        # Main ILS loop
        while not is_stucked:
            is_stucked = True
            # Perturbation phase
            new_solution = self.perturbation(best)
            # Local search
            new_solution = self.optimize(new_solution)
            # Check improvement
            if self.obj_func(new_solution) < self.obj_func(best):
                is_stucked = False
                best = list(filter(lambda x: len(x.customers) != 0, new_solution))
                logger.info("ILS step")
                logger.info(self.problem.print_canonical(best))
                logger.info("Total distance %s", self.obj_func(best))
        return best
