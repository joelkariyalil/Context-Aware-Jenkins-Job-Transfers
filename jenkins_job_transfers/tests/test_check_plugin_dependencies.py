import jenkins_job_transfers as jjt
import jenkins
from importlib.resources import files

def loadJobInServer(jenkinsCreds, server):
    try:
        # Extract credentials for the specified server
        URL = jenkinsCreds[server]["url"]
        Username = jenkinsCreds[server]["username"]
        Password = jenkinsCreds[server]["password"]

        # Connect to Jenkins server
        global conn
        conn = jenkins.Jenkins(URL, username=Username, password=Password)

        # Resolve paths to XML files using importlib.resources
        job1_path = files("jenkins_job_transfers.tests.assets.xmlFilesForJobs").joinpath("jobWithNoPluginsNoViews.xml")
        job2_path = files("jenkins_job_transfers.tests.assets.xmlFilesForJobs").joinpath("jobWithPluginsNoViews.xml")

        # Create jobs using the XML files
        with job1_path.open("r") as file1:
            conn.create_job("Job in Test With No Plugins No Views", file1.read())

        with job2_path.open("r") as file2:
            conn.create_job("Job in Test With Plugins No Views", file2.read())

        return True  # Indicate success

    except Exception as e:
        print(f"Error in loadJobInServer: {e}")
        return False  # Indicate failure

def connectServers(jenkinsCreds):
    try:
        # Extract credentials for both production and interim servers
        productionURL = jenkinsCreds["production"]["url"]
        interimURL = jenkinsCreds["interim"]["url"]
        productionUsername = jenkinsCreds["production"]["username"]
        interimUsername = jenkinsCreds["interim"]["username"]
        productionPassword = jenkinsCreds["production"]["password"]
        interimPassword = jenkinsCreds["interim"]["password"]

        # Use jenkins_job_transfers to connect the servers
        jjt.connect(productionURL, interimURL, productionUsername, interimUsername, productionPassword, interimPassword)

        return True  # Indicate success

    except Exception as e:
        print(f"Error in connectServers: {e}")
        return False  # Indicate failure

def test_check_plugin_dependencies_quiet(jenkinsCreds):
    # Step 1: Load jobs into the interim server
    chk = loadJobInServer(jenkinsCreds, "interim")
    assert chk, "Failed to Create Job in Interim Server"

    # Step 2: Connect production and interim servers
    result = connectServers(jenkinsCreds)
    assert result, "Failed to connect to Jenkins servers"

    # Step 3: Check plugin dependencies for a specific job
    result = jjt.check_plugin_dependencies("Job in Test With No Plugins No Views", ftype="job", mode="quiet")
    conn.delete_job("Job in Test With No Plugins No Views")
    conn.delete_job("Job in Test With Plugins No Views")
    assert result, "Failed to check plugin dependencies for Job in Test With No Plugins No Views"

    
