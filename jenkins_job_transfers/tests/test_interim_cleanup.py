from . import config
import pytest
import jenkins_job_transfers as jjt
from importlib.resources import files
from lxml import etree
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""

Interim Cleanup is basically required for places where the jobs have been deleted, then running the cleanup, should basically ensure that the view is deleted, as there are no jobs associated with it.

1. Load View in Interim Server
2. Delete the Associated Job
3. Run Interim Cleanup
4. Assert the View is Deleted

"""

def loadViewInInterimServer(viewName=None, viewFileNameForInterim=None, jobFileNamesForViewInInterim=None):

    jobNames = []

    try:

        if not config.interimConn or not config.productionConn: pytest.skip("Jenkins Servers Not Connected")

        interimConn = config.interimConn

        # Resolve path to XML file
        viewPathInterim = files("jenkins_job_transfers.tests.assets.xmlFilesForViews").joinpath(viewFileNameForInterim)

        # Load view in interim server
        with open (viewPathInterim, "r") as xmlFile:
            root = etree.fromstring(xmlFile)
            jobNames = root.xpath("//jobNames/string")
            if not interimConn.view_exists(viewName):
                interimConn.create_view(viewName, xmlFile.read())

            jobCount = 0

            for jobName in jobNames:
                if not interimConn.job_exists(jobName.text):

                    # Load job in interim server
                    jobPathInterim = files("jenkins_job_transfers.tests.assets.xmlFilesForJobs").joinpath(jobFileNamesForViewInInterim[jobCount])
                    with open (jobPathInterim, "r") as xmlFile:
                        interimConn.create_job(jobName, xmlFile.read())

                    jobCount += 1
                    
        return True, jobNames

    except Exception as e:
        logger.error("Exception in loadViewInInterimServer: %s", e)
        return False, jobNames
    

def test_interim_cleanup():

    try:
        if not config.interimConn or not config.productionConn: pytest.skip("Jenkins Servers Not Connected")


        




    except Exception as e:
        logger.error("Exception in test_interim_cleanup: %s", e)