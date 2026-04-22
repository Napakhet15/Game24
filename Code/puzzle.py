"""
puzzle.py
generates numbers and target for each game round
makes sure the puzzle is always solvable before giving it to the player
"""

import random
import math


class Puzzle:

    BASIC_OPS    = ["+", "-", "*", "/"]
    ADVANCED_OPS = ["+", "-", "*", "/", "^", "sqrt"]

    def __init__(self, mode_config: dict):
        # mode_config has settings like num_count, num_range, target_range etc.
        self.mode_config = mode_config
        self.advanced    = mode_config.get("advanced", False)
        self.numbers     = []
        self.target      = 0

        # pick operator set based on mode
        self.ops = self.ADVANCED_OPS if self.advanced else self.BASIC_OPS

    def generate(self):
        # keep generating until we find a solvable puzzle
        seed = self.mode_config.get("daily_seed", None)
        if seed is not None:
            random.seed(seed)

        while True:
            numbers = self._pick_numbers()
            target  = self._pick_target()

            # only use this puzzle if it has at least one valid solution
            if self._is_solvable(numbers, target):
                self.numbers = numbers
                self.target  = target
                return

    def validate(self, numbers_used: list) -> str:
        # check that player used exactly the right numbers
        if sorted(numbers_used) == sorted(self.numbers):
            return ""  # ok

        return (
            f"Use exactly these numbers: {self.numbers} "
            f"(found {numbers_used})"
        )

    def _pick_numbers(self) -> list:
        # generate random numbers within the mode's range
        low, high = self.mode_config["num_range"]
        count     = self.mode_config["num_count"]
        return [random.randint(low, high) for _ in range(count)]

    def _pick_target(self) -> int:
        # pick target value within allowed range
        low, high = self.mode_config["target_range"]
        if low == high:
            return low
        return random.randint(low, high)

    def _is_solvable(self, numbers: list, target: int) -> bool:
        # check if numbers can reach the target using allowed operators
        visited = set()
        return self._solve(
            nums=[float(n) for n in numbers],
            target=float(target),
            visited=visited
        )

    def _solve(self, nums: list, target: float, visited: set) -> bool:
        # recursive solver - tries all combinations of numbers and operators

        # base case - only one number left, check if it equals target
        if len(nums) == 1:
            return abs(nums[0] - target) < 1e-6

        # skip states we already checked (memoization to speed things up)
        state = tuple(sorted(round(n, 6) for n in nums))
        if state in visited:
            return False
        visited.add(state)

        # try sqrt (unary - applies to one number at a time)
        if self.advanced:
            for i in range(len(nums)):
                a = nums[i]
                # only apply sqrt to non-negative whole numbers
                if a < 0 or a != int(a):
                    continue
                result   = math.sqrt(a)
                new_nums = [nums[k] for k in range(len(nums)) if k != i] + [result]
                if self._solve(new_nums, target, visited):
                    return True

        # try all pairs of numbers with all binary operators
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):

                a    = nums[i]
                b    = nums[j]
                rest = [nums[k] for k in range(len(nums)) if k != i and k != j]

                binary_ops = [op for op in self.ops if op != "sqrt"]

                for op in binary_ops:

                    if op in ("+", "*"):
                        # commutative - only need to try one direction
                        result = self._apply_binary(a, b, op)
                        if result is not None:
                            if self._solve(rest + [result], target, visited):
                                return True
                    else:
                        # non-commutative - try both a op b and b op a
                        for x, y in [(a, b), (b, a)]:
                            result = self._apply_binary(x, y, op)
                            if result is not None:
                                if self._solve(rest + [result], target, visited):
                                    return True

        return False

    def _apply_binary(self, a: float, b: float, op: str):
        # apply operator to two numbers, return None if not valid
        try:
            if op == "+":
                return a + b
            elif op == "-":
                return a - b
            elif op == "*":
                return a * b
            elif op == "/":
                if abs(b) < 1e-9:
                    return None  # skip division by zero
                return a / b
            elif op == "^":
                if abs(a) > 1e6 or abs(b) > 10:
                    return None  # skip if result would be too large
                return math.pow(a, b)

        except (OverflowError, ZeroDivisionError, ValueError):
            return None

        return None
