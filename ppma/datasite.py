"""Phase 2: the Data Pointer layer, built on real PySyft.

All raw `syft` calls live in this module so the rest of the codebase reads
at a higher level (see roles.py). API confirmed against the OpenMined
PySyft 0.9.5 "hello-syft" tutorial.
"""

import syft as sy

from ppma.config import (
    ANALYST_EMAIL,
    ANALYST_INSTITUTION,
    ANALYST_NAME,
    ANALYST_PASSWORD,
    ANALYST_WEBSITE,
    DATASITE_NAME,
    DATASITE_PORT,
    ROOT_EMAIL,
    ROOT_PASSWORD,
)


def launch_datasite():
    """Launch a local datasite server and log in as its root/data-owner user."""
    server = sy.orchestra.launch(name=DATASITE_NAME, port=DATASITE_PORT, reset=True)
    root_client = server.login(email=ROOT_EMAIL, password=ROOT_PASSWORD)
    return server, root_client


def register_analyst(server, root_client):
    """Register the Third-Party Analyst account and return its logged-in client."""
    root_client.register(
        name=ANALYST_NAME,
        email=ANALYST_EMAIL,
        password=ANALYST_PASSWORD,
        password_verify=ANALYST_PASSWORD,
        institution=ANALYST_INSTITUTION,
        website=ANALYST_WEBSITE,
    )
    return server.login(email=ANALYST_EMAIL, password=ANALYST_PASSWORD)


def upload_sealed_dataset(root_client, sealed_df, mock_df, *, name: str, description: str):
    """Upload the enclave's sealed (real) data alongside a non-identifying mock."""
    dataset = sy.Dataset(
        name=name,
        description=description,
        asset_list=[
            sy.Asset(
                name=name,
                data=sealed_df,
                mock=mock_df,
                mock_is_real=False,
            )
        ],
    )
    root_client.upload_dataset(dataset)
