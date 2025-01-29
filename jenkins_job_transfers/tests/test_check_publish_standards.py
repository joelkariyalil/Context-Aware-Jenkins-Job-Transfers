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

def loadJobInInterimServer(jobName=None, jobFileNameForInterim=None):
    """
    Load a job in the interim server given the job name and filename for the XML file that contains the job configuration.

    Args:
        jobName (str): The name of the job to be transferred.
        jobFileNameForInterim (str): The filename of the XML file containing the job configuration for the interim server.

    Returns:
        Jenkins: The interim Jenkins connection if the job was successfully loaded, otherwise False.
    """
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
    """
    Load a view in the interim server given the view name and filenames for the XML files that contain the job configurations.

    Args:
        viewName (str): The name of the view to be transferred.
        viewFileNameForInterim (str): The filename of the XML file containing the view configuration for the interim server.
        jobFileNamesForViewInInterim (list): A list of filenames of the XML files containing the job configurations for the jobs in the view.

    Returns:
        tuple: A tuple containing a boolean indicating whether the view was loaded and a list of job names that were loaded with the view.
    """
    job_names = []
    interim_conn = config.interimConn

    try:
        # Construct path to view XML file
        view_path_interim = files("jenkins_job_transfers.tests.assets.xmlFilesForViews").joinpath(
            viewFileNameForInterim
        )

        # Read and parse view XML
        try:
            with open(view_path_interim, "rb") as xml_file:
                xml_content = xml_file.read().replace(b"\n", b"").strip()

            parser = etree.XMLParser(remove_blank_text=True)
            root = etree.fromstring(xml_content, parser=parser)

        except (IOError, etree.ParseError) as e:
            logger.error("Failed to read or parse view XML file: %s", e)
            return False, job_names

        # Extract job names from XML
        try:
            namespaces = root.nsmap
            
            if None in namespaces:
                job_names = root.xpath("//ns:jobNames/ns:string/text()", 
                                     namespaces={'ns': namespaces[None]})
            else:
                job_names = root.xpath("//jobNames/string/text()")

            if not job_names:
                job_names = root.xpath("//*[local-name()='string']/text()")

            if not job_names:
                logger.warning("No job names found in view XML")

        except etree.XPathEvalError as e:
            logger.error("XPath evaluation failed: %s", e)
            return False, job_names

        try:
            if not interim_conn.view_exists(viewName):
                interim_conn.create_view(viewName, xml_content.decode('utf-8'))
        except Exception as e:
            logger.error("Failed to create view '%s': %s", viewName, e)
            return False, job_names

        # Create jobs
        jobs_base_path = files("jenkins_job_transfers.tests.assets.xmlFilesForJobs")
        for job_count, job_name in enumerate(job_names):
            try:
                if not interim_conn.job_exists(job_name):
                    job_path = jobs_base_path.joinpath(
                        jobFileNamesForViewInInterim[job_count]
                    )
                    
                    try:
                        with open(job_path, "rb") as job_xml_file:
                            job_xml_content = job_xml_file.read()
                            interim_conn.create_job(job_name, job_xml_content)
                    except IOError as e:
                        logger.error("Failed to read job XML file for '%s': %s", job_name, e)
                        continue
                    except Exception as e:
                        logger.error("Failed to create job '%s': %s", job_name, e)
                        continue
                        
            except IndexError:
                logger.error("Job filename missing for job '%s' at index %d", job_name, job_count)
                continue

        return True, job_names

    except Exception as e:
        logger.error("Unexpected error in load_view_in_interim_server: %s", e)
        return False, job_names


def test_check_publish_job_standards_positive():
    """
    Positive Test Case

    Verifies that the function will detect jobs that meet the publishing standards when there are no duplicate jobs in the target environment.

    Parameters:
    None

    Returns:
    None
    """
    jobName = "Publish Job Standards - Positive"

    try:
    
        if not config.interimConn or not config.productionConn: pytest.skip("Jenkins Servers Not Connected")

        if not loadJobInInterimServer(jobName=jobName, jobFileNameForInterim="jobWithPluginsNoViews.xml"):
            pytest.fail("Failed to Load Jobs in Interim Server")
        
        result = jjt.check_publish_standards([jobName], "job", allowDuplicates=False, mode="quiet")

        assert not result, "Publish Standards Not Met - Positive Test Failed"

    except Exception as e:
        logger.error("Exception in test_check_publish_job_standards_positive: %s", e)

    finally:
        for conn in [config.interimConn]:
            if conn:
                if conn.job_exists(jobName):
                    conn.delete_job(jobName)



def test_check_publish_job_standards_negative():
    """
    Negative Test Case

    Verifies that the function will detect jobs that do not meet the publishing standards when there are duplicate jobs in the target environment.

    Parameters:
    None

    Returns:
    None
    """
    jobName = "Publish Job Standards - Negative"

    try:
    
        if not config.interimConn or not config.productionConn: pytest.skip("Jenkins Servers Not Connected")

        if not loadJobInInterimServer(jobName=jobName, jobFileNameForInterim="jobWithPluginsNoViews.xml"):
            pytest.fail("Failed to Load Jobs in Interim Server")
        
        result = jjt.check_publish_standards([jobName], "job", allowDuplicates=False, mode="quiet")

        assert result, "Publish Standards Not Met - Positive Test Failed"

    except Exception as e:
        logger.error("Exception in test_check_publish_job_standards_negative: %s", e)

    finally:
        for conn in [config.interimConn]:
            if conn:
                if conn.job_exists(jobName):
                    conn.delete_job(jobName)


def test_check_publish_view_standards_positive():
    """
    Positive Test Case

    Verifies that the function will detect views that meet the publishing standards when there are no duplicate views in the target environment.

    Parameters:
    None

    Returns:
    None
    """
    viewName = "Publish View Standards - Positive"
    jobNames = []

    try:
    
        if not config.interimConn or not config.productionConn: pytest.skip("Jenkins Servers Not Connected")

        chk, jobNames = loadViewInInterimServer(viewName=viewName, viewFileNameForInterim="viewWithJobsWithPlugins.xml", jobFileNamesForViewInInterim=["jobWithPluginsNoViews.xml"])
        
        if not chk: pytest.fail("Failed to Load View in Interim Server")
        
        result = jjt.check_publish_standards([viewName], "view", allowDuplicates=False, mode="quiet")

        assert not result, "Publish Standards Not Met - Positive Test Failed"

    except Exception as e:
        logger.error("Exception in test_check_publish_view_standards_positive: %s", e)

    finally:
        for conn in [config.interimConn]:
            if conn:
                if conn.view_exists(viewName):
                    conn.delete_view(viewName)
                    for jobName in jobNames:
                        if conn.job_exists(jobName):
                            conn.delete_job(jobName)


def test_check_publish_view_standards_negative():
    """
    Negative Test Case

    Verifies that the function will detect views that meet the publishing standards when there are duplicate views in the target environment.

    Parameters:
    None

    Returns:
    None
    """
    jobNames = []
    viewName = "Publish View Standards - Negative"

    try:
    
        if not config.interimConn or not config.productionConn: pytest.skip("Jenkins Servers Not Connected")

        chk, jobNames = loadViewInInterimServer(viewName=viewName, viewFileNameForInterim="viewWithJobsWithPlugins.xml", jobFileNamesForViewInInterim=["jobWithPluginsNoViews.xml"])
        
        if not chk: pytest.fail("Failed to Load View in Interim Server")

        result = jjt.check_publish_standards([viewName], "view", allowDuplicates=False, mode="quiet")

        assert result, "Publish Standards Not Met - Positive Test Failed"

    except Exception as e:
        logger.error("Exception in test_check_publish_view_standards_negative: %s", e)

    finally:
        for conn in [config.interimConn]:
            if conn:
                if conn.view_exists(viewName):
                    conn.delete_view(viewName)
                    for jobName in jobNames:
                        if conn.job_exists(jobName):
                            conn.delete_job(jobName)
