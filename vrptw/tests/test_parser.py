from vrptw.parser import SolomonFormatParser


EXAMPLE_PROBLEM = """
C108

VEHICLE
NUMBER     CAPACITY
  25         200

CUSTOMER
CUST NO.   XCOORD.   YCOORD.   DEMAND    READY TIME   DUE DATE   SERVICE TIME
 
    0      40         50          0          0       1236          0   
    1      45         68         10        830       1049         90   
    2      45         70         30        756        939         90   
    3      42         66         10         16        336         90   
    4      42         68         10        643        866         90   
    5      42         65         10         15        226         90  
"""

def test_(tmp_path):
    problem_file_path = tmp_path / "example_problem.txt"
    problem_file_path.write_text(EXAMPLE_PROBLEM)
    
    parser = SolomonFormatParser(problem_file=problem_file_path)

    problem = parser.get_problem()

    assert problem