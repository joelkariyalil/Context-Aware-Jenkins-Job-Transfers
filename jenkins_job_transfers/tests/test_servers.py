import jenkins
import jenkins_job_transfers as jjt
import logging
import pytest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.mark.order(1)
@pytest.mark.dependency()
def test_servers_alive(jenkinsCreds):
    try:

        # Extract all the details for the servers
        productionCreds = jenkinsCreds["production"]
        interimCreds = jenkinsCreds["interim"]

        # Create Jenkins objects for both the servers
        productionConn = jenkins.Jenkins(productionCreds["url"], username=productionCreds["username"], password=productionCreds["password"])
        interimConn = jenkins.Jenkins(interimCreds["url"], username=interimCreds["username"], password=interimCreds["password"])

        assert productionConn.get_info(), "Failed to connect to Production server"
        assert interimConn.get_info(), "Failed to connect to Interim server"
            
    except Exception as e:
        pytest.fail(f"Error in test_servers_alive: {e}")
