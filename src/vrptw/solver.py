from pathlib import Path

from .parser import SolomonFormatParser
from .structure import Problem
from .heuristics import IteratedLocalSearch


class VRPTWSolver:
    def __init__(self, problem_file_path: str):
        self.problem_file_path = problem_file_path
        self.problem = self._parse_solomon_format(self.problem_file_path)
    
    def _parse_solomon_format(self, file_path: Path) -> Problem:
        assert file_path.exists(), f"File {file_path} does not exist"
        return SolomonFormatParser().get_problem(file_path)
    
    def solve(self) -> bool:
        self.solution = IteratedLocalSearch(self.problem).execute()
        return True
    
    def save_solution(self, file_path: str):
        with open(file_path, 'w') as f:
            f.write(self.problem.print_canonical(self.solution))
