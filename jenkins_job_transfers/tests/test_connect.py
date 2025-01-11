import jenkins_job_transfers as jjt

# Helper function to connect to Jenkins servers
def connectServer(productionURL, interimUrl, productionUsername, interimUsername, productionPassword, interimPassword, mode):
    """Helper function to test server connection."""
    return jjt.connect(productionURL, interimUrl, productionUsername, interimUsername, productionPassword, interimPassword, mode=mode)


# Helper function to validate the response
def validate_response(request, expected=None, isResponseBool = True, strictMatch=True):
    """
    Validates the server connection response.

    Parameters:
    - request: The response object from the server connection attempt.
    - responseType (optional): The expected type of the response.
    - expected: The expected outcome of the response validation.

    Raises:
    AssertionError: If the request is None, indicating a failed connection.
    """
    if isResponseBool:

        assert expected == request, "Connection Failed"

    else:
        if strictMatch:
            assert expected.lower() == request.lower(), "Connection Failed"
        else:
            assert expected.lower() in request.lower(), "Connection Failed"


# Test for valid connection in quiet mode
def test_connect_quiet(jenkinsCreds):
    """Test connection in quiet mode."""

    # Retrieve credentials
    productionUrl = jenkinsCreds["production"]["url"]
    productionUsername = jenkinsCreds["production"]["username"]
    productionPassword = jenkinsCreds["production"]["password"]
    interimUrl = jenkinsCreds["interim"]["url"]
    interimUsername = jenkinsCreds["interim"]["username"]
    interimPassword = jenkinsCreds["interim"]["password"]

    # Connect in quiet mode
    request = connectServer(productionUrl, interimUrl, productionUsername, interimUsername, productionPassword, interimPassword, mode="quiet")

    # Validate response
    validate_response(request, expected=True)

# Test for valid connection in console mode
def test_connect_console(jenkinsCreds, capsys):
    """Test connection in console mode and check console output."""

    # Retrieve credentials
    productionUrl = jenkinsCreds["production"]["url"]
    productionUsername = jenkinsCreds["production"]["username"]
    productionPassword = jenkinsCreds["production"]["password"]
    interimUrl = jenkinsCreds["interim"]["url"]
    interimUsername = jenkinsCreds["interim"]["username"]
    interimPassword = jenkinsCreds["interim"]["password"]

    # Set a smaller window size to capture the output
    jjt.set_console_size(50)

    # Connect in console mode
    request = connectServer(productionUrl, interimUrl, productionUsername, interimUsername, productionPassword, interimPassword, mode="console")

    captured = capsys.readouterr()

    # Validate response
    validate_response(captured.out, isResponseBool=False, expected="Connection established", strictMatch=False)

# Test for invalid credentials
def test_invalid_credentials_console(jenkinsCreds, capsys):
    """Test connection with invalid credentials."""

    # Use invalid credentials
    invalidProductionUsername = "wrong_user"
    invalidProductionPassword = "wrong_password"

    productionUrl = jenkinsCreds["production"]["url"]
    interimUrl = jenkinsCreds["interim"]["url"]
    interimUsername = jenkinsCreds["interim"]["username"]
    interimPassword = jenkinsCreds["interim"]["password"]

    # Test connection with invalid credentials
    request = connectServer(productionUrl, interimUrl, invalidProductionUsername, interimUsername, invalidProductionPassword, interimPassword, mode="console")

    captured = capsys.readouterr()

    # Validate response
    validate_response(captured.out, isResponseBool=False, expected="Connection Falied", strictMatch=False)


def test_invalid_credentials_quiet(jenkinsCreds):
    """Test connection with invalid credentials."""

    # Use invalid credentials
    invalidProductionUsername = "wrong_user"
    invalidProductionPassword = "wrong_password"

    productionUrl = jenkinsCreds["production"]["url"]
    interimUrl = jenkinsCreds["interim"]["url"]
    interimUsername = jenkinsCreds["interim"]["username"]
    interimPassword = jenkinsCreds["interim"]["password"]

    # Test connection with invalid credentials
    request = connectServer(productionUrl, interimUrl, invalidProductionUsername, interimUsername, invalidProductionPassword, interimPassword, mode="quiet")

    # Validate the response
    validate_response(request, expected=False)  # It should fail

# # Test for server unavailability
# def test_server_unavailability(jenkinsCreds):
#     """Test connection when one or both servers are unavailable."""

#     # Use invalid credentials
#     unavailableProductionUrl = "http://invalid-url:8080"

#     productionUrl = jenkinsCreds["production"]["url"]
#     interimUrl = jenkinsCreds["interim"]["url"]
#     productionUsername = jenkinsCreds["production"]["username"]
#     productionPassword = jenkinsCreds["production"]["password"]
#     interimUsername = jenkinsCreds["interim"]["username"]
#     interimPassword = jenkinsCreds["interim"]["password"]

#     # Test unavailable production server
#     request = connectServer(unavailableProductionUrl, interimUrl, productionUsername, interimUsername, productionPassword, interimPassword, mode="console")
#     validate_response(request)  # It should fail

#     # Test unavailable interim server
#     request = connectServer(productionUrl, "http://invalid-url:8081", productionUsername, interimUsername, productionPassword, interimPassword, mode="console")
#     validate_response(request)  # It should fail

# # Test for missing credentials
# def test_missing_credentials(jenkinsCreds):
#     """Test the connection with missing credentials."""

#     # Missing credentials
#     productionUrl = jenkinsCreds["production"]["url"]
#     interimUrl = jenkinsCreds["interim"]["url"]
#     productionUsername = ""  # Empty username
#     productionPassword = ""  # Empty password
#     interimUsername = jenkinsCreds["interim"]["username"]
#     interimPassword = jenkinsCreds["interim"]["password"]

#     # Test missing credentials
#     request = connectServer(productionUrl, interimUrl, productionUsername, interimUsername, productionPassword, interimPassword, mode="console")
#     validate_response(request)

# # Test different modes (quiet vs console)
# def test_connection_modes(jenkinsCreds):
#     """Test the connection in different modes (quiet vs console)."""

#     productionUrl = jenkinsCreds["production"]["url"]
#     productionUsername = jenkinsCreds["production"]["username"]
#     productionPassword = jenkinsCreds["production"]["password"]
#     interimUrl = jenkinsCreds["interim"]["url"]
#     interimUsername = jenkinsCreds["interim"]["username"]
#     interimPassword = jenkinsCreds["interim"]["password"]

#     # Test in quiet mode
#     requestQuiet = connectServer(productionUrl, interimUrl, productionUsername, interimUsername, productionPassword, interimPassword, mode="quiet")
#     validate_response(requestQuiet)

#     # Test in console mode
#     requestConsole = connectServer(productionUrl, interimUrl, productionUsername, interimUsername, productionPassword, interimPassword, mode="console")
#     validate_response(requestConsole)


# def test_invalid_url(jenkinsCreds):
#     """Test connection with invalid URL format."""

#     invalidProductionUrl = "htp://invalid-url"  # Invalid URL format

#     productionUrl = jenkinsCreds["production"]["url"]
#     interimUrl = jenkinsCreds["interim"]["url"]
#     productionUsername = jenkinsCreds["production"]["username"]
#     productionPassword = jenkinsCreds["production"]["password"]
#     interimUsername = jenkinsCreds["interim"]["username"]
#     interimPassword = jenkinsCreds["interim"]["password"]

#     # Test connection with invalid URL
#     request = connectServer(invalidProductionUrl, interimUrl, productionUsername, interimUsername, productionPassword, interimPassword, mode="console")

#     # Validate the response
#     validate_response(request)  # It should fail
