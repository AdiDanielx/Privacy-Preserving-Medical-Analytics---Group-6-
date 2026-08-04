"""A minimal per-session differential-privacy budget accountant."""


class PrivacyBudgetExceeded(Exception):
    pass


class PrivacyBudget:
    def __init__(self, total_epsilon: float):
        self.total_epsilon = total_epsilon
        self.spent = 0.0

    def spend(self, epsilon: float) -> None:
        if self.spent + epsilon > self.total_epsilon:
            raise PrivacyBudgetExceeded(
                f"Privacy budget exceeded: requested {epsilon:.3f}, "
                f"already spent {self.spent:.3f} of {self.total_epsilon:.3f}"
            )
        self.spent += epsilon

    @property
    def remaining(self) -> float:
        return self.total_epsilon - self.spent
