"""
Stability Controller - Detects low improvement and prevents runaway evolution.
"""

from typing import Dict, Any


class StabilityController:
    """Monitor evolution and decide whether to stop the loop."""

    def __init__(self, improvement_threshold: float = 0.03, max_no_improve_cycles: int = 2):
        self.improvement_threshold = improvement_threshold
        self.max_no_improve_cycles = max_no_improve_cycles
        self.no_improve_counter = 0

    def evaluate_cycle(self, last_score: float, previous_score: float) -> Dict[str, Any]:
        """Evaluate whether system is improving."""
        improvement = last_score - previous_score if previous_score is not None else last_score

        is_improving = improvement >= self.improvement_threshold
        if is_improving:
            self.no_improve_counter = 0
        else:
            self.no_improve_counter += 1

        should_stop = self.no_improve_counter > self.max_no_improve_cycles

        return {
            "improvement": improvement,
            "no_improve_counter": self.no_improve_counter,
            "should_stop": should_stop,
            "threshold": self.improvement_threshold,
        }

    def reset(self):
        self.no_improve_counter = 0
