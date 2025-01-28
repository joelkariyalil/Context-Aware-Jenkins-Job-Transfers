import pytest

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
