from ovinc.client import OVINCClient


class Account:
    """
    Account Api
    """

    def __init__(self, client: OVINCClient):
        self.client = client

    def verify_token(self, token: str):
        return self.client.request(method="POST", url="/account/verify_token/", json={"token": token})
