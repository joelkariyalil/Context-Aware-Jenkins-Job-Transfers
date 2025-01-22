import jenkins_job_transfers as jjt
import pytest
import logging
from . import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper function to validate the response
def validate_response(request, expected=None, isResponseBool=True, strictMatch=True):
    """
    Validates the server connection response.

    Parameters:
    - request: The response object from the server connection attempt.
    - expected: The expected outcome of the response validation.
    - isResponseBool: Indicates if the response is expected to be a boolean.
    - strictMatch: For string validation, checks for an exact match if True.

    Raises:
    AssertionError: If the request validation fails.
    """
    assert request is not None, "Validation Failed: Response is None."

    if isResponseBool:
        assert request == expected, "Validation Failed: Connection unsuccessful."
    else:
        if strictMatch:
            assert expected.lower() == request.lower(), "Validation Failed: Exact match not found."
        else:
            assert expected.lower() in request.lower(), "Validation Failed: Partial match not found."


def get_credentials(jenkinsCreds, env):
    """
    Retrieve Jenkins server credentials for a specified environment.

    Parameters:
    - jenkinsCreds: Dictionary containing Jenkins credentials for different environments.
    - env: The environment key for which credentials are to be retrieved (e.g., "production" or "interim").

    Returns:
    Dictionary containing "url", "username", and "password" for the specified environment.
    """
    return {
        "url": jenkinsCreds[env]["url"],
        "username": jenkinsCreds[env]["username"],
        "password": jenkinsCreds[env]["password"],
    }

# Test connection with specified mode
def connectServers(jenkinsCreds, mode, capsys=None, invalid=False):
    """
    Test Jenkins connection based on mode and credentials.

    Parameters:
    - jenkinsCreds: Dictionary containing Jenkins credentials.
    - mode: Connection mode ("quiet" or "console").
    - capsys: For capturing console output in tests (optional).
    - invalid: Whether to use invalid credentials for the test.

    Raises:
    AssertionError: If validation fails.
    """
    # Use valid or invalid credentials
    production = get_credentials(jenkinsCreds, "production")
    interim = get_credentials(jenkinsCreds, "interim")

    if invalid:
        production["username"] = "wrong_user"
        production["password"] = "wrong_password"

    # Connect to Jenkins

    jjt.set_console_size(50)

    request = jjt.connect(
        production["url"],
        interim["url"],
        production["username"],
        interim["username"],
        production["password"],
        interim["password"],
        mode=mode,
    )

    if mode == "console" and capsys:
        captured = capsys.readouterr()
        validate_response(
            captured.out,
            isResponseBool=False,
            expected="Established" if not invalid else "Failed",
            strictMatch=False,
        )
    else:

        validate_response(
            request, 
            expected=not invalid
        )




# Test Cases

def test_connect_quiet(jenkinsCreds):
    """Test valid connection in quiet mode."""
    if not config.chkEchServerConnected: pytest.skip(" Jenkins Servers Not Connected")
    connectServers(jenkinsCreds, mode="quiet")

def test_connect_console(jenkinsCreds, capsys):
    """Test valid connection in console mode."""
    if not config.chkEchServerConnected: pytest.skip("Jenkins Servers Not Connected")
    connectServers(jenkinsCreds, mode="console", capsys=capsys)


def test_invalid_credentials_quiet(jenkinsCreds):
    """Test invalid credentials in quiet mode."""
    if not config.chkEchServerConnected: pytest.skip("Jenkins Servers Not Connected")
    connectServers(jenkinsCreds, mode="quiet", invalid=True)


def test_invalid_credentials_console(jenkinsCreds, capsys):
    """Test invalid credentials in console mode."""
    if not config.chkEchServerConnected: pytest.skip("Jenkins Servers Not Connected")
    connectServers(jenkinsCreds, mode="console", capsys=capsys, invalid=True)
