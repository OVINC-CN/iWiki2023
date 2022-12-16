from typing import Union

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.authentication import BaseAuthentication, SessionAuthentication

from core.exceptions import LoginRequired
from core.logger import logger
from core.models import Empty
from ovinc.client import ovinc_client

USER_MODEL = get_user_model()


class SessionAuthenticate(SessionAuthentication):
    """
    Session Auth
    """

    def authenticate(self, request) -> Union[tuple, None]:
        # Get Auth Token
        auth_token = request.COOKIES.get(settings.AUTH_TOKEN_NAME, None)
        if not auth_token:
            return None
        # Verify Auth Token
        user = self.check_token(auth_token)
        if not user:
            return None
        return user, None

    def check_token(self, token) -> USER_MODEL:
        # Cache First
        user = cache.get(token)
        if user:
            return user
        # OSB Auth
        try:
            # Request
            result = ovinc_client.account.verify_token(token)
            # Verify Failed
            if isinstance(result, Empty):
                logger.info("[OSBAuthFailed] Result => %s", result)
                return None
            # Create User
            username = result["data"]["username"]
            user = USER_MODEL.objects.get_or_create(username=username)[0]
            for key, val in result["data"].items():
                setattr(user, key, val)
            user.save(update_fields=result["data"].keys())
            cache.set(token, user)
            return self.check_token(token)
        except Exception as err:
            logger.exception(err)
            return None


class AuthTokenAuthenticate(BaseAuthentication):
    """
    Auth Token Authenticate
    """

    def authenticate(self, request) -> (USER_MODEL, None):
        # User Auth Token
        raise LoginRequired()
