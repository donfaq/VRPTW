import math


class Customer:
    def __init__(self, number, x, y, demand, ready_time, due_date, service_time):
        self.number = number
        self.x = x
        self.y = y
        self.demand = demand
        self.ready_time = ready_time
        self.due_date = due_date
        self.service_time = service_time
        self.is_serviced = False

    def __repr__(self):
        return f"C_{self.number}"

    def distance(self, target):
        return math.sqrt(math.pow(self.x - target.x, 2) + math.pow(target.y - self.y, 2))


class Problem:
    def __init__(self, name, customers: list, vehicle_number, vehicle_capacity):
        self.name = name
        self.customers = customers
        self.vehicle_number = vehicle_number
        self.vehicle_capacity = vehicle_capacity
        self.depot: Customer = list(filter(lambda x: x.number == 0, customers))[0]
        self.depot.is_serviced = True

    def __repr__(self):
        return f"Instance: {self.name}\n" \
               f"Vehicle number: {self.vehicle_number}\n" \
               f"Vehicle capacity: {self.vehicle_capacity}\n"

    def obj_func(self, routes):
        return sum(map(lambda x: x.total_distance, routes))

    def print_canonical(self, routes):
        return "\n".join(list(map(lambda x: x.canonical_view, routes)))


class Route:
    def __init__(self, problem: Problem, customers: list):
        self.problem: Problem = problem
        self._customers: list = [self.problem.depot, *customers, self.problem.depot]

    def __repr__(self):
        return " ".join(str(customer.number) for customer in self._customers)

    @property
    def canonical_view(self):
        time = 0
        result = [0, 0.0]
        for source, target in zip(self._customers, self._customers[1:]):
            start_time = max([target.ready_time, time + source.distance(target)])
            time = start_time + target.service_time
            result.append(target.number)
            result.append(start_time)
        return " ".join(str(x) for x in result)

    @property
    def customers(self):
        return self._customers[1:-1]

    @property
    def total_distance(self):
        return sum(a.distance(b) for (a, b) in zip(self._customers, self._customers[1:]))

    @property
    def edges(self):
        return list(zip(self._customers, self._customers[1:]))

    @property
    def is_feasible(self):
        time = 0
        capacity = self.problem.vehicle_capacity
        is_feasible = True
        for source, target in zip(self._customers, self._customers[1:]):
            start_service_time = max([target.ready_time, time + source.distance(target)])
            if start_service_time >= target.due_date:
                is_feasible = False
            time = start_service_time + target.service_time
            capacity -= target.demand
        if time >= self.problem.depot.due_date or capacity < 0:
            is_feasible = False
        return is_feasible
