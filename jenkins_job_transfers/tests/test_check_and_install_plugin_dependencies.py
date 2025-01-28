import jenkins_job_transfers as jjt
import jenkins
from importlib.resources import files
import logging
import pytest
from . import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def loadJobInServers(jenkinsCreds, jobName, fileNameForProduction, fileNameForInterim):
    """
    Load a job in both interim and production servers given the job name and filenames for the XML files that contain the job configuration.

    Args:
        jenkinsCreds (dict): A dictionary containing the credentials for the interim and production servers.
        jobName (str): The name of the job to be transferred.
        fileNameForProduction (str): The filename of the XML file containing the job configuration for the production server.
        fileNameForInterim (str): The filename of the XML file containing the job configuration for the interim server.

    Returns:
        tuple: A tuple containing the interim and production Jenkins connections.
    """
    try:

        # Connect to Jenkins servers
        interimConn = config.interimConn
        productionConn = config.productionConn

        # Resolve path to XML file
        jobPathProduction = files("jenkins_job_transfers.tests.assets.xmlFilesForJobs").joinpath(fileNameForProduction)
        jobPathInterim = files("jenkins_job_transfers.tests.assets.xmlFilesForJobs").joinpath(fileNameForInterim)

        
        with jobPathInterim.open("r") as xmlFile: 
            if not interimConn.job_exists(jobName): interimConn.create_job(jobName, xmlFile.read())

        with jobPathProduction.open("r") as xmlFile:
            if not productionConn.job_exists(jobName): productionConn.create_job(jobName, xmlFile.read())

        return True

    except Exception as e:
        logger.error(f"Error in loadJobInServers: {e}")
        return False

# Negative Test Case in Quiet Mode
def test_check_and_install_plugin_dependencies_quiet_negative(jenkinsCreds):
    """
    Test check_and_install_plugin_dependencies() function in quiet mode with no plugin dependencies.

    Verifies that the function will not detect any plugins when there are no plugins in the job configuration.
    """
    try:
    
        if not config.interimConn or not config.productionConn: pytest.skip("Jenkins Servers Not Connected")
        interimConn, productionConn = config.interimConn, config.productionConn

        jobName = "Test Plugin Dependency - Quiet"
        # Load jobs
        if not loadJobInServers(jenkinsCreds, jobName=jobName, fileNameForInterim="jobWithNoPluginsNoViews.xml", fileNameForProduction="jobWithNoPluginsNoViews.xml"):
            pytest.fail("Failed to load job in servers")

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
        result = jjt.check_and_install_plugin_dependencies([jobName], ftype="job", mode="quiet")
        assert len(result[jobName])==0, "Negative Test Failed. Non-Job Specific Plugins Detected"

    except Exception as e:
        logger.error(f"Error in test_check_and_install_plugin_dependencies_quiet_negative: {e}")
    
    finally:
        for conn in [interimConn, productionConn]:
            if conn:
                if conn.job_exists(jobName):
                    conn.delete_job(jobName)

# Positive Test Case in Quiet Mode
def test_check_and_install_plugin_dependencies_quiet_positive(jenkinsCreds):
    """
    Positive Test Case in Quiet Mode

    Verifies that the function will detect plugins when there are plugins in the job configuration.
    """
    try:

        if not config.interimConn or not config.productionConn: pytest.skip("Jenkins Servers Not Connected")
        interimConn, productionConn = config.interimConn, config.productionConn

        jobName = "Test Plugin Dependency - Quiet"

        # Load jobs
        if not loadJobInServers(jenkinsCreds, jobName=jobName, fileNameForInterim="jobWithPluginsNoViews.xml", fileNameForProduction="jobWithNoPluginsNoViews.xml"):
            pytest.fail("Failed to load job in servers")

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
        result = jjt.check_and_install_plugin_dependencies([jobName], ftype="job", mode="quiet")
        assert len(result[jobName])!=0, "Positive Test Failed: Plugins Not Detected"

    except Exception as e:
        logger.error(f"Error in test_check_and_install_plugin_dependencies_quiet_positive: {e}")
    
    finally:
        for conn in [interimConn, productionConn]:
            if conn:
                if conn.job_exists(jobName):
                    conn.delete_job(jobName)
        

#Negative Test Case in the Console Mode

def test_check_and_install_plugin_dependencies_console_negative(jenkinsCreds, capsys):
    """
    Test check_and_install_plugin_dependencies() function in console mode with no plugin dependencies.

    Verifies that the check_and_install_plugin_dependencies() function does not detect any plugins when
    there are no plugins in the job configuration. Connects to Jenkins servers, loads a job 
    with no plugins, and captures console output to ensure the absence of plugin dependencies.
    """
    try:

        if not config.interimConn or not config.productionConn: pytest.skip("Jenkins Servers Not Connected")
        interimConn, productionConn = config.interimConn, config.productionConn

        jobName = "Test Plugin Dependency - Console"

        if not loadJobInServers(jenkinsCreds, jobName=jobName, fileNameForInterim="jobWithNoPluginsNoViews.xml", fileNameForProduction="jobWithNoPluginsNoViews.xml"):
            pytest.fail("Failed to load job in servers")

        # Extract credentials
        productionCreds = jenkinsCreds["production"]
        interimCreds = jenkinsCreds["interim"]

        jjt.set_console_size(100)

        assert jjt.connect(
            productionCreds["url"],
            interimCreds["url"],
            productionCreds["username"],
            interimCreds["username"],
            productionCreds["password"],
            interimCreds["password"]
        ), "Failed to Connect to Servers"


        # Check dependencies
        result = jjt.check_and_install_plugin_dependencies([jobName], ftype="job", mode="console")
        assert result and "success" in capsys.readouterr().out.lower(), "Positive Test Failed: Plugins Not Detected"

    except Exception as e:
        logger.error(f"Error in test_check_and_install_plugin_dependencies_console_negative: {e}")
    
    finally:
        for conn in [interimConn, productionConn]:
            if conn:
                if conn.job_exists(jobName):
                    conn.delete_job(jobName)



# Positive Test Case in the Console Mode


def test_check_and_install_plugin_dependencies_console_positive(jenkinsCreds, capsys):

    """
    Positive Test Case in the Console Mode

    Verifies that the function will detect plugins when there are plugins in the job configuration.
    """
    try:

        if not config.interimConn or not config.productionConn: pytest.skip("Jenkins Servers Not Connected")
        interimConn, productionConn = config.interimConn, config.productionConn

        jobName = "Test Plugin Dependency - Console"

        if not loadJobInServers(jenkinsCreds, jobName=jobName, fileNameForInterim="jobWithPluginsNoViews.xml", fileNameForProduction="jobWithNoPluginsNoViews.xml"):
            pytest.fail("Failed to load job in servers")

        # Extract credentials
        productionCreds = jenkinsCreds["production"]
        interimCreds = jenkinsCreds["interim"]

        jjt.set_console_size(100)

        assert jjt.connect(
            productionCreds["url"],
            interimCreds["url"],
            productionCreds["username"],
            interimCreds["username"],
            productionCreds["password"],
            interimCreds["password"]
        ), "Failed to Connect to Servers"

        # Check dependencies
        result = jjt.check_and_install_plugin_dependencies([jobName], ftype="job", mode="console")

        captured = capsys.readouterr().out
        
        assert len(result[jobName])!=0 and "Plugins to be Installed".lower() in captured.lower(), "Positive Test Failed: Plugins Not Detected"

    except Exception as e:
        logger.error(f"Error in test_check_and_install_plugin_dependencies_console_positive: {e}")

    finally:
        for conn in [interimConn, productionConn]:
            if conn:
                if conn.job_exists(jobName):
                    conn.delete_job(jobName)
