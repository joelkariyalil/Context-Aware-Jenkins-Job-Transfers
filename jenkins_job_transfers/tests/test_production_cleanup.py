from . import config
import pytest
import jenkins_job_transfers as jjt
from importlib.resources import files
from lxml import etree
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""

Production Cleanup is basically required for places where the jobs have been deleted, then running the cleanup, should basically ensure that the view is deleted, as there are no jobs associated with it.

1. Load View in Production Server
2. Delete the Associated Job
3. Run Interim Cleanup
4. Assert the View is Deleted

"""

def loadViewInProductionServer(viewName=None, viewFileNameForProduction=None, jobFileNamesForViewInProduction=None):

    jobNames = []

    try:

        if not config.productionConn    : pytest.skip("Jenkins Servers Not Connected")

        productionConn = config.productionConn

        # Resolve path to XML file
        viewPathProduction = files("jenkins_job_transfers.tests.assets.xmlFilesForViews").joinpath(viewFileNameForProduction)

        # Load view in the Production Server

        with open (viewPathProduction, "r") as xmlFile:
            root = etree.fromstring(xmlFile)
            jobNames = root.xpath("//jobNames/string")

            if not productionConn.view_exists(viewName):
                productionConn.create_view(viewName, xmlFile.read())

            jobCount = 0

            for jobName in jobNames:
                if not productionConn.job_exists(jobName.text):

                    # Load job in interim server
                    jobPathInterim = files("jenkins_job_transfers.tests.assets.xmlFilesForJobs").joinpath(jobFileNamesForViewInProduction[jobCount])
                    with open (jobPathInterim, "r") as xmlFile:
                        if not productionConn.job_exists(jobName):
                            productionConn.create_job(jobName, xmlFile)

                    jobCount += 1
                     
        return True, jobNames

    except Exception as e:
        logger.error("Exception in loadViewInInterimServer: %s", e)
        return False, jobNames

def test_production_cleanup():

    viewName = "Production Cleanup View"    
    jobNames = []

    try:
        if not config.productionConn: pytest.skip("Jenkins Servers Not Connected")

        # Load View in Interim Server
        chk, jobNames = loadViewInProductionServer(viewName=viewName, viewFileNameForProduction="viewWithJobsWithPlugins.xml", jobFileNamesForViewInInterim=["jobWithPluginsNoViews.xml", "jobWithNoPluginsNoViews.xml"])

        if not chk: pytest.fail("Failed to Load View in Interim Server")

        # Delete the Associated Job
        for jobName in jobNames:
            config.productionConn.delete_job(jobName)

        # Run Interim Cleanup
        jjt.production_cleanup()

        # Assert the View is Deleted
        assert not config.productionConn.view_exists(viewName), "View Not Deleted from Interim Server"

    except Exception as e:
        logger.error("Exception in test_production_cleanup: %s", e)

    finally:
        for conn in [config.productionConn, config.productionConn]:
            if conn:
                if conn.view_exists(viewName):
                    conn.delete_view(viewName)
                for jobName in jobNames:
                    if conn.job_exists(jobName):
                        conn.delete_job(jobName)
