import jenkins
import jenkins_job_transfers as jjt
import logging
import pytest
from . import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_servers_alive(jenkinsCreds):
    """
    Test to check if Jenkins servers are alive and if they are connected using the given credentials.

    Connects to both the production and interim servers using the Jenkins python library, and checks if the servers are alive and connected using the given credentials. If the connection fails, the test fails.

    :param jenkinsCreds: A dictionary containing the credentials for both the production and interim servers.
    :type jenkinsCreds: dict

    :return: None
    :rtype: None
    """
    productionConn, interimConn = None, None
    try:

        # Extract all the details for the servers
        productionCreds = jenkinsCreds["production"]
        interimCreds = jenkinsCreds["interim"]

        # Create Jenkins objects for both the servers
        productionConn = jenkins.Jenkins(productionCreds["url"], username=productionCreds["username"], password=productionCreds["password"])
        interimConn = jenkins.Jenkins(interimCreds["url"], username=interimCreds["username"], password=interimCreds["password"])

        if productionConn.get_info() and interimConn.get_info(): config.chkEchServerConnected = True
        else: pytest.fail("Failed to Connect to Jenkins servers", pytrace=False)

        assert productionConn.get_version(), "Failed to connect to Production server"
        assert interimConn, "Failed to connect to Interim server"
            
    except Exception as e:
        logger.error("Exception in test_servers_alive: %s", e)
        pytest.fail(f"Failed to Connect to Jenkins Servers", pytrace=False)

    finally:
        config.productionConn = productionConn
        config.interimConn = interimConn
