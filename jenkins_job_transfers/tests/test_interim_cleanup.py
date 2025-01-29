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
    """
    Load a view and its associated jobs in the interim server.

    Args:
        viewName (str, optional): The name of the view to be created in the interim server.
        viewFileNameForInterim (str, optional): The filename of the XML file containing the view configuration.
        jobFileNamesForViewInInterim (list, optional): A list of filenames of the XML files containing the job configurations.

    Returns:
        tuple: A tuple containing a boolean indicating the success of the operation and a list of job names associated with the view.
    """
    jobNames = []

    if not config.interimConn:
        pytest.skip("Jenkins Interim Server Not Connected")

    interimConn = config.interimConn

    viewPathInterim = files("jenkins_job_transfers.tests.assets.xmlFilesForViews").joinpath(viewFileNameForInterim)

    with open(viewPathInterim, "rb") as xmlFile:
        xmlContent = xmlFile.read()
        root = etree.fromstring(xmlContent)
        jobNames = root.xpath("//jobNames/string")

        if not interimConn.view_exists(viewName):
            interimConn.create_view(viewName, xmlContent.decode())
        jobCount = 0
        for jobName in jobNames:
            if not interimConn.job_exists(jobName):
                # Load job in interim server
                jobPathInterim = files("jenkins_job_transfers.tests.assets.xmlFilesForJobs").joinpath(
                    jobFileNamesForViewInInterim[jobCount]
                )
                with open(jobPathInterim, "rb") as jobXmlFile:
                    interimConn.create_job(jobName, jobXmlFile.read())
                jobCount += 1

    return True, jobNames


def test_interim_cleanup():
    """
    Test Interim Cleanup.

    This test will load a view with two jobs in the interim server, delete the associated job, run the interim cleanup, and assert that the view is deleted from the interim server.

    1. Load a view with two jobs in the interim server.
    2. Delete the associated job.
    3. Run the interim cleanup.
    4. Assert that the view is deleted from the interim server.
    """
    viewName = "Interim Cleanup View"
    jobNames = []

    try:
        if not config.interimConn: pytest.skip("Jenkins Servers Not Connected")

        # Load View in Interim Server
        chk, jobNames = loadViewInInterimServer(
            viewName=viewName,
            viewFileNameForInterim="viewWithJobsWithPlugins.xml",
            jobFileNamesForViewInInterim=["jobWithPluginsNoViews.xml", "jobWithNoPluginsNoViews.xml"]
        )

        if not chk: pytest.fail("Failed to Load View in Interim Server")

        # Delete the Associated Job
        for jobName in jobNames:
            config.interimConn.delete_job(jobName)

        # Run Interim Cleanup
        jjt.interim_cleanup()

        # Assert the View is Deleted
        assert not config.interimConn.view_exists(viewName), "View Not Deleted from Interim Server"

    except Exception as e:
        logger.error("Exception in test_interim_cleanup: %s", e)

    finally:
        if config.interimConn:
            if config.interimConn.view_exists(viewName):
                config.interimConn.delete_view(viewName)
            for jobName in jobNames:
                if config.interimConn.job_exists(jobName):
                    config.interimConn.delete_job(jobName)
