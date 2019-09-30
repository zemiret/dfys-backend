from datetime import datetime, timezone, timedelta
# from functools import wraps
from unittest import mock

from dfys.core.tests.test_factory import UserFactory


def create_user_request(test_method):
    request = test_method('testpath/')
    user = UserFactory()
    request.user = user

    return request


def mock_timezone_now(func):
    testtime = datetime.now(tz=timezone.utc) - timedelta(days=30)

#    @wraps(func)
    def wrapper(*args, **kwargs):
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = testtime
            return func(*args, **kwargs, testtime=testtime)

    return wrapper
