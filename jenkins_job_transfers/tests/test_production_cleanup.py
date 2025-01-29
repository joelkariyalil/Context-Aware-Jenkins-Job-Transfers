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
    """
    Load a view in the interim server given the view name and filenames for the XML files that contain the job configurations.

    Args:
        viewName (str): The name of the view to be transferred.
        viewFileNameForProduction (str): The filename of the XML file containing the view configuration for the interim server.
        jobFileNamesForViewInProduction (list): A list of filenames of the XML files containing the job configurations for the jobs in the view.

    Returns:
        tuple: A tuple containing a boolean indicating whether the view was loaded and a list of job names that were loaded with the view.
    """
    job_names = []
    production_conn = config.production_conn

    try:
        # Construct path to view XML file
        view_path_interim = files("jenkins_job_transfers.tests.assets.xmlFilesForViews").joinpath(
            viewFileNameForProduction
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

        # Create view if it doesn't exist
        try:
            if not production_conn.view_exists(viewName):
                production_conn.create_view(viewName, xml_content.decode('utf-8'))
        except Exception as e:
            logger.error("Failed to create view '%s': %s", viewName, e)
            return False, job_names

        # Create jobs
        jobs_base_path = files("jenkins_job_transfers.tests.assets.xmlFilesForJobs")
        for job_count, job_name in enumerate(job_names):
            try:
                if not production_conn.job_exists(job_name):
                    job_path = jobs_base_path.joinpath(
                        jobFileNamesForViewInProduction[job_count]
                    )
                    
                    try:
                        with open(job_path, "rb") as job_xml_file:
                            job_xml_content = job_xml_file.read()
                            production_conn.create_job(job_name, job_xml_content)
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
        logger.error("Unexpected error in load_view_in_production_server: %s", e)
        return False, job_names

def test_production_cleanup():
    """
    Test case for production cleanup process.

    This test performs the following steps:
    1. Loads a view in the production server using specified XML configuration files.
    2. Deletes the jobs associated with the loaded view.
    3. Executes the production cleanup function to remove views with no associated jobs.
    4. Asserts that the view is successfully deleted from the production server.

    If Jenkins servers are not connected, the test is skipped.
    """
    viewName = "Production Cleanup View"    
    jobNames = []

    try:
        if not config.productionConn: pytest.skip("Jenkins Servers Not Connected")

        # Load View in Interim Server
        chk, jobNames = loadViewInProductionServer(viewName=viewName, viewFileNameForProduction="viewWithJobsWithPlugins.xml", jobFileNamesForViewInProduction=["jobWithPluginsNoViews.xml", "jobWithNoPluginsNoViews.xml"])

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
