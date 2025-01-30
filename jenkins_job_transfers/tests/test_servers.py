import jenkins
import jenkins_job_transfers as jjt
import logging
import pytest
from . import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_servers_alive():
    """
    Test that both production and interim servers are alive and that the test can connect to them.

    This test is required for all other tests in this module to run.
    """
    try:
        assert config.productionConn.get_version(), "Failed to Connect to Production Server"
        assert config.interimConn.get_version(), "Failed to Connect to Interim Server"
            
    except Exception as e:
        logger.error("Exception in test_servers_alive: %s", e)
        pytest.fail(f"Failed to Connect to Jenkins Servers", pytrace=False)
