from datetime import datetime
import pytz

from dfys.core.tests.test_factory import UserFactory


def create_user_request(test_method):
    request = test_method('testpath/')
    user = UserFactory()
    request.user = user

    return request


def mock_now():
    timezone = pytz.timezone("America/Los_Angeles")
    return datetime(2019, 10, 1, 0, 0, 0, 0, timezone)
