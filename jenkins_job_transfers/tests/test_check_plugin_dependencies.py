import jenkins_job_transfers as jjt
import jenkins
from importlib.resources import files
import logging
import pytest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def loadJobInServers(jenkinsCreds, fileName):
    try:
        # Extract credentials for the servers
        interimCreds = jenkinsCreds["interim"]
        productionCreds = jenkinsCreds["production"]

        # Connect to Jenkins servers
        interimConn = jenkins.Jenkins(interimCreds["url"], username=interimCreds["username"], password=interimCreds["password"])
        productionConn = jenkins.Jenkins(productionCreds["url"], username=productionCreds["username"], password=productionCreds["password"])

        # Resolve path to XML file
        jobPath = files("jenkins_job_transfers.tests.assets.xmlFilesForJobs").joinpath(fileName)

        # Create jobs in both servers
        jobName = fileName.split(".")[0]
        with jobPath.open("r") as xmlFile:
            if interimConn.job_exists(jobName):
                interimConn.delete_job(jobName)
            interimConn.create_job(jobName, xmlFile.read())

            if productionConn.job_exists(jobName):
                productionConn.delete_job(jobName)
            productionConn.create_job(jobName, xmlFile.read())

        return interimConn, productionConn

    except Exception as e:
        logger.error(f"Error in loadJobInServers: {e}")
        print(f"Error in loadJobInServers: {e}")
        return None, None  # Return None to indicate failure


def connectServers(jenkinsCreds):
    try:
        # Extract credentials
        productionCreds = jenkinsCreds["production"]
        interimCreds = jenkinsCreds["interim"]

        # Connect servers using jenkins_job_transfers
        jjt.connect(
            productionCreds["url"],
            interimCreds["url"],
            productionCreds["username"],
            interimCreds["username"],
            productionCreds["password"],
            interimCreds["password"]
        )
        return True

    except Exception as e:
        logger.error(f"Error in connectServers: {e}")
        return False


# Negative Test Case
@pytest.mark.dependency(depends=["test_servers.test_servers_alive"])
def test_check_plugin_dependencies_quiet_negative(jenkinsCreds):
    interimConn, productionConn = None, None
    try:
        # Load jobs
        interimConn, productionConn = loadJobInServers(jenkinsCreds, "jobWithNoPluginsNoViews.xml")
        assert interimConn and productionConn, "Failed to create jobs in servers"

        # Connect servers
        assert connectServers(jenkinsCreds), "Failed to connect Jenkins servers"

        # Check dependencies
        result = jjt.check_plugin_dependencies("jobWithNoPluginsNoViews", ftype="job", mode="quiet")
        assert len(result) == 0, "Negative test failed: unexpected plugins detected"
    finally:
        # Cleanup jobs
        if interimConn:
            interimConn.delete_job("jobWithNoPluginsNoViews")
        if productionConn:
            productionConn.delete_job("jobWithNoPluginsNoViews")


# Positive Test Case
@pytest.mark.dependency(depends=["test_servers.test_servers_alive"])
def test_check_plugin_dependencies_quiet_positive(jenkinsCreds):
    interimConn, productionConn = None, None
    try:
        # Load jobs
        interimConn, productionConn = loadJobInServers(jenkinsCreds, "jobWithPluginsNoViews.xml")
        assert interimConn and productionConn, "Failed to create jobs in servers"

        # Connect servers
        assert connectServers(jenkinsCreds), "Failed to connect Jenkins servers"

        # Check dependencies
        result = jjt.check_plugin_dependencies("jobWithPluginsNoViews", ftype="job", mode="quiet")
        assert len(result) != 0, "Positive test failed: plugins not detected"
    finally:
        # Cleanup jobs
        if interimConn:
            interimConn.delete_job("jobWithPluginsNoViews")
        if productionConn:
            productionConn.delete_job("jobWithPluginsNoViews")
