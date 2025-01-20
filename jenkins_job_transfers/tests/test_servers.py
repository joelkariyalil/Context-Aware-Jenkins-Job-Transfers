import jenkins
import jenkins_job_transfers as jjt
import logging
import pytest
from . import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.mark.order(1)
def test_servers_alive(jenkinsCreds):

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
        pytest.fail(f"Failed to Connect to Jenkins Servers", pytrace=False)
