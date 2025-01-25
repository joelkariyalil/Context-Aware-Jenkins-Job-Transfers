from . import config
import pytest
import jenkins_job_transfers as jjt
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_production_cleanup():

    try:

        if not config.productionConn: pytest.skip("Jenkins Servers Not Connected")

        
        




    except Exception as e:
        logger.error("Exception in test_interim_cleanup: %s", e)