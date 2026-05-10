import random
import math


class Puzzle:

    BASIC_OPS    = ["+", "-", "*", "/"]
    ADVANCED_OPS = ["+", "-", "*", "/", "^", "sqrt"]

    def __init__(self, mode_config: dict):
        # mode_config
        self.mode_config = mode_config
        self.advanced    = mode_config.get("advanced", False)
        self.numbers     = []
        self.target      = 0

        # pick operator 
        self.ops = self.ADVANCED_OPS if self.advanced else self.BASIC_OPS

    def generate(self):
        # generating until find puzzle
        seed = self.mode_config.get("daily_seed", None)
        if seed is not None:
            random.seed(seed)

        while True:
            numbers = self._pick_numbers()
            target  = self._pick_target()

            if self._is_solvable(numbers, target):
                self.numbers = numbers
                self.target  = target
                return

    def validate(self, numbers_used: list) -> str:
        # check right numbers
        if sorted(numbers_used) == sorted(self.numbers):
            return "" 

        return (
            f"Use exactly these numbers: {self.numbers} "
            f"(found {numbers_used})"
        )

    def _pick_numbers(self) -> list:
        low, high = self.mode_config["num_range"]
        count     = self.mode_config["num_count"]
        return [random.randint(low, high) for _ in range(count)]

    def _pick_target(self) -> int:
        low, high = self.mode_config["target_range"]
        if low == high:
            return low
        return random.randint(low, high)

    def _is_solvable(self, numbers: list, target: int) -> bool:
        # check numbers
        visited = set()
        return self._solve(
            nums=[float(n) for n in numbers],
            target=float(target),
            visited=visited
        )

    def _solve(self, nums: list, target: float, visited: set) -> bool:
        # recursive
        if len(nums) == 1:
            return abs(nums[0] - target) < 1e-6

        # skip
        state = tuple(sorted(round(n, 6) for n in nums))
        if state in visited:
            return False
        visited.add(state)

        # try sqrt
        if self.advanced:
            for i in range(len(nums)):
                a = nums[i]
                if a < 0 or a != int(a):
                    continue
                result   = math.sqrt(a)
                new_nums = [nums[k] for k in range(len(nums)) if k != i] + [result]
                if self._solve(new_nums, target, visited):
                    return True

        # try all pairs 
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):

                a    = nums[i]
                b    = nums[j]
                rest = [nums[k] for k in range(len(nums)) if k != i and k != j]

                binary_ops = [op for op in self.ops if op != "sqrt"]

                for op in binary_ops:

                    if op in ("+", "*"):
                        result = self._apply_binary(a, b, op)
                        if result is not None:
                            if self._solve(rest + [result], target, visited):
                                return True
                    else:
                        for x, y in [(a, b), (b, a)]:
                            result = self._apply_binary(x, y, op)
                            if result is not None:
                                if self._solve(rest + [result], target, visited):
                                    return True

        return False

    def _apply_binary(self, a: float, b: float, op: str):
        try:
            if op == "+":
                return a + b
            elif op == "-":
                return a - b
            elif op == "*":
                return a * b
            elif op == "/":
                if abs(b) < 1e-9:
                    return None  # skip
                return a / b
            elif op == "^":
                if abs(a) > 1e6 or abs(b) > 10:
                    return None  # skip if too large
                return math.pow(a, b)

        except (OverflowError, ZeroDivisionError, ValueError):
            return None

        return None
