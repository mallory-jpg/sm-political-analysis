"""Place widely used test fixtures here."""

import pytest
import requests
import configparser
import pytest_mock

@pytest.fixture(autouse=True)
@pytest.mark.api_call
def disable_network_calls(monkeypatch):
    """Prevent real API network calls during testing"""

    def stunted_get():
        raise RuntimeError("Network access not allowed during testing!")
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: stunted_get())

@pytest.fixture(autouse=True)
@pytest.mark.database_access
def mock_db_connection(mocker, db_connection):
    """Alter database connection settings for all tests in module.
    mocker: pytest-mock plugin fixture
    db_connection: connection class
    returns True if monkeypatch was successful"""

    mocker.patch('database.Database.connection', db_connection)
    return True


@pytest.fixture
def example_news_data():  # must be used in multiple tests
    pass
