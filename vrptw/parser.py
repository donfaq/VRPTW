from .structure import Problem, Customer


class SolomonFormatParser:
    """Parsing file with following structure:
    ```txt
    <Instance name>
    <empty line>
    VEHICLE
    NUMBER     CAPACITY
    K           Q
    <empty line>
    CUSTOMER
    CUST NO.  XCOORD.   YCOORD.    DEMAND   READY TIME  DUE DATE   SERVICE TIME
    <empty line>
        0       x0        y1         q0         e0          l0            s0  
        1       x1        y2         q1         e1          l1            s1  
        ...     ...        ...        ...        ...         ...           ... 
        100     x100      y100       q100       e100        l100          s100
    ```
    """

    def get_problem(self, problem_file) -> Problem:

        with open(problem_file, "r") as f:
            lines = list(map(lambda line: line.replace("\n", "").split(), f.readlines()))

        name = lines[0][0]
        vehicle_number, vehicle_capacity = list(map(int, lines[4]))
        customers = []

        for line in lines[9:]:
            customers.append(Customer(*list(map(int, line))))

        return Problem(name, customers, vehicle_number, vehicle_capacity)
