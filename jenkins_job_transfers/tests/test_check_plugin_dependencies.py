import jenkins_job_transfers as jjt
import jenkins
from importlib.resources import files
import logging
import pytest
from . import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def loadJobInServers(jenkinsCreds, jobName, fileNameForProduction, fileNameForInterim):
    
    # try:

    # Extract credentials for the servers
    interimCreds = jenkinsCreds["interim"]
    productionCreds = jenkinsCreds["production"]

    # Connect to Jenkins servers
    interimConn = jenkins.Jenkins(interimCreds["url"], username=interimCreds["username"], password=interimCreds["password"])
    productionConn = jenkins.Jenkins(productionCreds["url"], username=productionCreds["username"], password=productionCreds["password"])

    assert interimConn.get_info() and productionConn.get_info(), "Failed to Connect to Jenkins Servers"

    # Resolve path to XML file
    jobPathProduction = files("jenkins_job_transfers.tests.assets.xmlFilesForJobs").joinpath(fileNameForProduction)
    jobPathInterim = files("jenkins_job_transfers.tests.assets.xmlFilesForJobs").joinpath(fileNameForInterim)

    
    with jobPathInterim.open("r") as xmlFile: 
        if not interimConn.job_exists(jobName): interimConn.create_job(jobName, xmlFile.read())

    with jobPathProduction.open("r") as xmlFile:
        if not productionConn.job_exists(jobName): productionConn.create_job(jobName, xmlFile.read())

    return interimConn, productionConn

    # except Exception as e:

    #     logger.error(f"Error in loadJobInServers: {e}")
    #     return None, None

# Negative Test Case
def test_check_plugin_dependencies_quiet_negative(jenkinsCreds):

    if not config.chkEchServerConnected: pytest.skip("Jenkins Servers Not Connected")

    interimConn, productionConn = None, None

    try:

        jobName = "Test Check Plugin Dependency"
        # Load jobs
        interimConn, productionConn = loadJobInServers(jenkinsCreds, jobName=jobName, fileNameForInterim="jobWithNoPluginsNoViews.xml", fileNameForProduction="jobWithNoPluginsNoViews.xml")

        # Extract credentials
        productionCreds = jenkinsCreds["production"]
        interimCreds = jenkinsCreds["interim"]

        assert jjt.connect(
            productionCreds["url"],
            interimCreds["url"],
            productionCreds["username"],
            interimCreds["username"],
            productionCreds["password"],
            interimCreds["password"]
        ), "Failed to Connect to Servers"

        # Check dependencies
        result = jjt.check_plugin_dependencies(jobName, ftype="job", mode="quiet")
        assert len(result) == 0, "Negative Test Failed. Non-Job Specific Plugins Detected"
    finally:
        for conn in [interimConn, productionConn]:
            if conn:
                if conn.job_exists(jobName):
                    conn.delete_job(jobName)

# Positive Test Case
def test_check_plugin_dependencies_quiet_positive(jenkinsCreds):

    if not config.chkEchServerConnected: pytest.skip("Jenkins Servers Not Connected")
    
    interimConn, productionConn = None, None

    try:

        jobName = "Test Check Plugin Dependency"

        jjt.set_console_size(200)
        # Load jobs
        interimConn, productionConn = loadJobInServers(jenkinsCreds, jobName=jobName, fileNameForInterim="jobWithPluginsNoViews.xml", fileNameForProduction="jobWithNoPluginsNoViews.xml")

        # Extract credentials
        productionCreds = jenkinsCreds["production"]
        interimCreds = jenkinsCreds["interim"]

        assert jjt.connect(
            productionCreds["url"],
            interimCreds["url"],
            productionCreds["username"],
            interimCreds["username"],
            productionCreds["password"],
            interimCreds["password"]
        ), "Failed to Connect to Servers"


        # Check dependencies
        result = jjt.check_plugin_dependencies(jobName, ftype="job", mode="quiet")
        with open("debug.log", "w") as f:
            f.write(str(result))
        assert len(result) != 0, "Positive Test Failed: Plugins Not Detected"
    finally:
        for conn in [interimConn, productionConn]:
            if conn:
                if conn.job_exists(jobName):
                    conn.delete_job(jobName)
        