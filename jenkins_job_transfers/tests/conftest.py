import pytest
import os

def pytest_addoption(parser):
    """Define custom command-line options for pytest."""
    parser.addoption("--production_url", action="store", help="URL for Production Jenkins Server")
    parser.addoption("--interim_url", action="store", help="URL for Interim Jenkins Server")
    parser.addoption("--production_username", action="store", help="Username for Production Jenkins Server")
    parser.addoption("--production_password", action="store", help="Password for Production Jenkins Server")
    parser.addoption("--interim_username", action="store", help="Username for Interim Jenkins Server")
    parser.addoption("--interim_password", action="store", help="Password for Interim Jenkins Server")

@pytest.fixture
def jenkinsCreds(request):
    """Retrieve and validate Jenkins server credentials from pytest command-line options."""
    production_machine_url = request.config.getoption("--production_url")
    interim_machine_url = request.config.getoption("--interim_url")
    production_username = request.config.getoption("--production_username")
    production_password = request.config.getoption("--production_password")
    interim_username = request.config.getoption("--interim_username")
    interim_password = request.config.getoption("--interim_password")

    # Assert that all credentials are provided and valid
    assert production_machine_url is not None, "Production URL must be provided using --production_url."
    assert interim_machine_url is not None, "Interim URL must be provided using --interim_url."
    assert production_username is not None, "Production username must be provided using --production_username."
    assert production_password is not None, "Production password must be provided using --production_password."
    assert interim_username is not None, "Interim username must be provided using --interim_username."
    assert interim_password is not None, "Interim password must be provided using --interim_password."

    return {
        "production": {
            "url": production_machine_url,
            "username": production_username,
            "password": production_password,
        },
        "interim": {
            "url": interim_machine_url,
            "username": interim_username,
            "password": interim_password,
        },
    }

def pytest_collection_modifyitems(items):
    """Sort tests in the order they should be run.
    
    This hook is used to sort the tests in the order they should be run. The order is as follows:
    
    1. test_servers.py
    2. test_connect.py
    3. test_check_plugin_dependencies.py
    4. test_check_and_install_plugin_dependencies.py
    5. test_check_publish_standards.py
    6. test_transfer.py
    7. test_interim_cleanup.py
    8. test_production_cleanup.py
    
    This is done to ensure that the tests are run in a way that minimizes the number of times the servers need to be connected to and disconnected from.
    """
    order = {
        "test_servers.py": 1,
        "test_connect.py": 2,
        "test_check_plugin_dependencies.py": 3,
        "test_check_and_install_plugin_dependencies.py": 4,
        "test_check_publish_standards.py": 5,
        "test_transfer.py": 6,
        "test_interim_cleanup.py": 7,
        "test_production_cleanup.py": 8
    }
    
    items.sort(key=lambda item: order.get(os.path.basename(item.nodeid.split("::")[0]), 999))
