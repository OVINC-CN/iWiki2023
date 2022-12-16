import json

import requests
from django.conf import settings
from requests import HTTPError

from core.logger import logger
from core.models import Empty


class OVINCClient:
    """
    OVINC Client
    """

    def __init__(self):
        self._app_code = settings.APP_CODE
        self._app_secret = settings.APP_SECRET
        self._ovinc_api_url = settings.OVINC_API_DOMAIN

    @property
    def account(self):
        from ovinc.account import Account

        return Account(self)

    def request(self, method: str, url: str, *args, **kwargs):
        url = self._ovinc_api_url + url
        response = requests.request(method=method, url=url, headers=self._headers, *args, **kwargs)
        data = response.json()
        try:
            response.raise_for_status()
            return data["data"]
        except HTTPError as err:
            logger.info("[OVINCApiError] Err => %s; Data => %s", str(err), data)
            return Empty()

    @property
    def _headers(self):
        return {"ovinc-app": json.dumps({"app_code": self._app_code, "app_secret": self._app_secret})}


ovinc_client = OVINCClient()
