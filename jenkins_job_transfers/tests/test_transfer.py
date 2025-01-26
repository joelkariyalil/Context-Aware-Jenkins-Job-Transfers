import jenkins
import jenkins_job_transfers as jjt
from importlib.resources import files
from jenkins_job_transfers import baseModule as bMod
from jenkins_job_transfers import utils
import logging
import pytest
from . import config
from lxml import etree

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""

    Testing Stratergy here

    Jobs (For both Console and Quiet Mode)
        1. Invalid Jobs
        2. Job with Plugins
        3. Job without Plugins

    Views (For both Console and Quiet Mode)
        1. Invalid Views
        2. Views with Jobs
        3. (Extra) Views containing Jobs with Plugins
        
"""

def loadJobInInterimServer(jobName=None, jobFileNameForInterim=None):

    try:

        if not config.interimConn or not config.productionConn: pytest.skip("Jenkins Servers Not Connected")

        interimConn = config.interimConn

        # Resolve path to XML file
        jobPathInterim = files("jenkins_job_transfers.tests.assets.xmlFilesForJobs").joinpath(jobFileNameForInterim)

        # Load job in interim server
        with open (jobPathInterim, "r") as xmlFile:
            if not interimConn.job_exists(jobName):
                interimConn.create_job(jobName, xmlFile.read())

        return interimConn
    
    except Exception as e:
        logger.error("Exception in loadJobInInterimServer: %s", e)
        return False
    

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
                interimConn.create_view(viewName, xmlFile)

            jobCount = 0

            for jobName in jobNames:
                if not interimConn.job_exists(jobName):

                    # Load job in interim server
                    jobPathInterim = files("jenkins_job_transfers.tests.assets.xmlFilesForJobs").joinpath(jobFileNamesForViewInInterim[jobCount])
                    with open (jobPathInterim, "r") as xmlFile:
                        if not interimConn.job_exists(jobName):
                            interimConn.create_job(jobName, xmlFile)

                    jobCount += 1
                    
        return True, jobNames

    except Exception as e:
        logger.error("Exception in loadViewInInterimServer: %s", e)
        return False, jobNames

def test_transfer_job_with_plugins_no_views_quiet():

    jobName = "Transfer Job with Plugins and No Views - Quiet"

    try:
    
        if not config.interimConn or not config.productionConn: pytest.skip("Jenkins Servers Not Connected")

        if not loadJobInInterimServer(jobName=jobName, jobFileNameForInterim="jobWithPluginsNoViews.xml"):
            pytest.fail("Failed to Load Jobs in Interim Server")
        
        jjt.transfer([jobName], "job", allowDuplicates=False, mode="quiet")

        assert config.productionConn.job_exists(jobName), "Job not transferred to production server"

    except Exception as e:
        logger.error("Exception in test_transfer_job_quiet: %s", e)

    finally:
        for conn in [config.interimConn, config.productionConn]:
            if conn:
                if conn.job_exists(jobName):
                    conn.delete_job(jobName)

def test_transfer_job_without_plugins_no_views():

    jobName = "Transfer Job without Plugins and No Views - Quiet"

    try:
    
        if not config.interimConn or not config.productionConn: pytest.skip("Jenkins Servers Not Connected")

        if not loadJobInInterimServer(jobName=jobName, jobFileNameForInterim="jobWithNoPluginsNoViews.xml"):
            pytest.fail("Failed to Load Job in Interim Server")
        
        jjt.transfer([jobName], "job", allowDuplicates=True, mode="quiet")

        assert config.productionConn.job_exists(jobName), "Job Not Transferred to the Production Server"

    except Exception as e:
        logger.error("Exception in test_transfer_job_quiet: %s", e)

    finally:
        for conn in [config.interimConn, config.productionConn]:
            if conn:
                if conn.job_exists(jobName):
                    conn.delete_job(jobName)


def test_transfer_job_with_plugins_with_views():

    jobName = "Transfer Job with Plugins and Views - Quiet"

    try:
    
        if not config.interimConn or not config.productionConn: pytest.skip("Jenkins Servers Not Connected")

        if not loadJobInInterimServer(jobName=jobName, jobFileNameForInterim="jobWithPluginsNoViews.xml"):
            pytest.fail("Failed to Load Job in Interim Server")
        
        jjt.transfer([jobName], "view", allowDuplicates=False, mode="quiet")

        assert config.productionConn.job_exists(jobName), "Job with Plugins and Views Not Transferred to the Production Server"

    except Exception as e:
        logger.error("Exception in test_transfer_job_quiet: %s", e)

    finally:
        for conn in [config.interimConn, config.productionConn]:
            if conn:
                if conn.job_exists(jobName):
                    conn.delete_job(jobName)
        

    
def test_transfer_views():

    viewName = "Transfer View - Quiet"
    jobNames = []

    try:
    
        if not config.interimConn or not config.productionConn: pytest.skip("Jenkins Servers Not Connected")

        chk, jobNames = loadViewInInterimServer(viewName=viewName, viewFileNameForInterim="viewWithJobsWithPlugins.xml", jobFileNamesForViewInInterim=["jobWithPluginsNoViews.xml", "jobWithNoPluginsNoViews.xml"])

        if not chk:
            pytest.fail("Failed to Load View in Interim Server")

        jjt.transfer([viewName], "view", allowDuplicates=False, mode="quiet")

        assert config.productionConn.view_exists(viewName) and all([config.productionConn.job_exists(jobName) for jobName in jobNames]), "View and Jobs not transferred to production server"

    except Exception as e:
        logger.error("Exception in test_transfer_job_quiet: %s", e)

    finally:
        for conn in [config.interimConn, config.productionConn]:
            if conn:
                if conn.view_exists(viewName):
                    conn.delete_view(viewName)
                for jobName in jobNames:
                    if conn.job_exists(jobName):
                        conn.delete_job(jobName)
