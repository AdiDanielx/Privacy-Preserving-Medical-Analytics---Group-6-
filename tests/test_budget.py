import pytest

from ppma.budget import PrivacyBudget, PrivacyBudgetExceeded


def test_spend_reduces_remaining():
    budget = PrivacyBudget(10.0)
    budget.spend(3.0)
    assert budget.remaining == pytest.approx(7.0)
    assert budget.spent == pytest.approx(3.0)


def test_spend_raises_once_exceeded():
    budget = PrivacyBudget(1.0)
    budget.spend(0.7)
    with pytest.raises(PrivacyBudgetExceeded):
        budget.spend(0.5)


def test_exact_budget_boundary_allowed():
    budget = PrivacyBudget(1.0)
    budget.spend(1.0)
    assert budget.remaining == pytest.approx(0.0)
