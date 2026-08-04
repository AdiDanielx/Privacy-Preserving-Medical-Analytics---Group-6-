"""Phase 3: thin role wrappers so demo.py reads as a narrative of who does
what, instead of raw syft client calls scattered through the script.
"""

import syft as sy

from ppma.budget import PrivacyBudget


class DataOwner:
    """The hospital / data owner: reviews and approves analyst requests."""

    def __init__(self, root_client):
        self.client = root_client

    def pending_requests(self):
        return list(self.client.requests)

    def review_and_approve(self, request):
        return request.approve()


class Analyst:
    """The Third-Party Analyst: only ever sees mock data and DP-noised results."""

    def __init__(self, client, budget: PrivacyBudget):
        self.client = client
        self.budget = budget

    def get_asset(self, asset_name: str, dataset_index: int = -1):
        return self.client.datasets[dataset_index].assets[asset_name]

    def explore_mock(self, asset_name: str, dataset_index: int = -1):
        return self.get_asset(asset_name, dataset_index).mock

    def request_query(self, asset, query_spec: dict, epsilon: float):
        """Submit a DP query for data-owner approval. Spends epsilon up front."""
        self.budget.spend(epsilon)
        decorated = sy.syft_function_single_use(df=asset)(query_spec["fn"])
        return self.client.code.request_code_execution(decorated)

    def collect_result(self, asset, query_spec: dict):
        """Retrieve the (already DP-noised) result of an approved query."""
        code_fn = getattr(self.client.code, query_spec["name"])
        result_ptr = code_fn(df=asset)
        return result_ptr.get()
