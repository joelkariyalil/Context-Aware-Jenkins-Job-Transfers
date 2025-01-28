from . import baseModule as jbm
from . import utils as jutils
from . import config as cfg
from rich.console import Console
from rich.table import Table

'''
Functions to Support

1. connect(production_machine_url, dev_machine_url, production_username, dev_username, production_password, dev_password)
2. transfer(production_conn, interim_conn, publish_list, type="job" or "view", allowDuplicateJobs=False)
3. check_publish_standards(production_conn, interim_conn, publish_list, type="job" or "view", allowDuplicateJobs=False) 
4. check_plugin_dependencies(production_conn, interim_conn, publish_list, type="job" or "view")
5. check_and_install_plugin_dependencies(production_conn, interim_conn, publish_list, type="job" or "view")
6. production_cleanup()
7. interim_cleanup()

mode = "console" or "quiet"

'''


def connect(production_machine_url, interim_machine_url, production_username, interim_username, production_password,
            interim_password, mode="console"):
    """
    Establishes a connection to the production and interim Jenkins servers.

    This function sets up the necessary configurations and attempts to connect to the specified Jenkins servers
    using the provided URLs, usernames, and passwords. It also validates the input parameters and confirms
    the connection status.

    Parameters:
    - production_machine_url (str): The URL for the production Jenkins server.
    - interim_machine_url (str): The URL for the interim Jenkins server.
    - production_username (str): The username for the production Jenkins server.
    - interim_username (str): The username for the interim Jenkins server.
    - production_password (str): The password for the production Jenkins server.
    - interim_password (str): The password for the interim Jenkins server.
    - mode (str, optional): The mode of operation, either "console" or "quiet". Defaults to "console".

    Returns:
    - bool: True if the connection is successfully established, False otherwise.

    Raises:
    - ValueError: If any of the URLs, usernames, or passwords are None, or if the connection cannot be established.
    - TypeError: If the mode is not one of the allowed values ("console", "quiet").
    """
    try:

        if not production_machine_url or not interim_machine_url:
            raise ValueError("Either production_machine_url or interim_machine_url is None.")
        if not production_username or not interim_username:
            raise ValueError("Either production_username or interim_username is None.")
        if not production_password or not interim_password:
            raise ValueError("Either production_password or interim_password is None.")
        if mode not in ('console', 'quiet'):
            raise TypeError("Invalid Mode Field! Mode = [console, quiet]")

        cfg.production_url = production_machine_url
        cfg.interim_url = interim_machine_url   
        cfg.mode = mode
        cfg.console = Console()
        cfg.table = Table(show_lines=True, width=cfg.width)
        cfg.table.add_section()
        cfg.table.add_column("Connection Summary", style="cyan", no_wrap=True)
        cfg.table.add_row("Production URL", production_machine_url)
        cfg.table.add_row("Interim URL", interim_machine_url)

        cfg.production_conn, cfg.interim_conn = jbm.establish_connection_to_servers(production_machine_url,
                                                                                    interim_machine_url,
                                                                                    production_username,
                                                                                    interim_username,
                                                                                    production_password,
                                                                                    interim_password)
        # Check if the connection has been established
        if not cfg.production_conn.get_views() or not cfg.interim_conn.get_views():
            raise ValueError("Connection Not Established!")

        cfg.table.add_row("Connection Status", "Connection Established")
        if mode == 'console': cfg.console.print(cfg.table)
        return True

    except Exception as e:
        cfg.table.add_row("Connection Status", "Connection Failed", str(e))
        cfg.console.print(cfg.table)
        return False


def transfer(publish_list, ftype="job", allowDuplicates=False, mode="console"):
    """
    Transfers jobs/views from the production Jenkins server to the interim Jenkins server.

    Parameters:
    - publish_list (list): A list of job/view names to be transferred.
    - ftype (str, optional): The type of the element in the publish_list. Defaults to "job".
    - allowDuplicates (bool, optional): Whether to allow duplicate jobs/views. Defaults to False.
    - mode (str, optional): The mode of operation, either "console" or "quiet". Defaults to "console".

    Returns:
    - bool: True if the transfer is successful, False otherwise.

    Raises:
    - ValueError: If the connection to the Jenkins servers has not been established.
    - TypeError: If the publish_list is not a list, or if the ftype or mode is not a string.
    """
    try:

        cfg.table = Table(show_lines=True, width=cfg.width)
        cfg.table.add_column("Transfer Details", style="cyan", no_wrap=True)

        production_conn = cfg.production_conn
        interim_conn = cfg.interim_conn

        ftype = ftype.lower()
        mode = cfg.mode = mode.lower()
        cfg.allowDuplicates = allowDuplicates
        res = False

        if not production_conn or not interim_conn:
            raise ValueError("Connection Not Established!")
        if not isinstance(publish_list, list):
            raise TypeError("Publish List Must be a List!")
        if not isinstance(ftype, str):
            raise TypeError("Type Must be a String!")
        if ftype not in ('job', 'view'):
            raise TypeError("Invalid Type Field! Type = [job, view]")
        if mode not in ('console', 'quiet'):
            raise TypeError("Invalid Mode Field! Mode = [console, quiet]")

        if ftype == "job":

            res = jbm.transfer_jobs(publish_list)

        elif ftype == "view":

            res = jbm.transfer_views(publish_list)

        if mode == 'console': cfg.console.print(cfg.table)
        return res

    except Exception as e:
        cfg.table.add_row("Transfer Status", "Failed", str(e))
        cfg.console.print(cfg.table)
        return False


def check_publish_standards(publish_list, ftype="job", allowDuplicates=False, mode="console"):
    """
    Checks if a list of jobs/views meet the publishing standards by comparing them with views and jobs from different connections.

    Parameters:
    publish_list (list): A list of jobs/views to be checked against the views and jobs.
    ftype (str): The type of the publish list. Must be one of 'job' or 'view'.
    allowDuplicates (bool): If duplicate jobs/views are allowed in the target environment.
    mode (str): The mode of the check. Must be one of 'console' or 'quiet'.

    Returns:
    bool: True if all jobs/views meet the standards, False otherwise.
    """
    try:

        cfg.table = Table(show_lines=True, width=cfg.width)
        cfg.table.add_column("Check Publish Standards", style="cyan", no_wrap=True)

        production_conn = cfg.production_conn
        interim_conn = cfg.interim_conn

        ftype = ftype.lower()
        mode = cfg.mode = mode.lower()
        cfg.allowDuplicates = allowDuplicates

        if not production_conn or not interim_conn:
            raise ValueError("Connection Not Established!")
        if not isinstance(publish_list, list):
            raise TypeError("Publish List Must be a List!")
        if not isinstance(ftype, str):
            raise TypeError("Type Must be a String!")
        if ftype not in ('job', 'view'):
            raise TypeError("Invalid Type Field! Type = [job, view]")
        if mode not in ('console', 'quiet'):
            raise TypeError("Invalid Mode Field! Mode = [console, quiet]")

        if ftype == "job":
            chk = jbm.job_pre_check(publish_list)
            if mode == 'console': cfg.console.print(cfg.table)
            return chk

        elif ftype == "view":
            chk = jbm.view_pre_check(publish_list)
            if mode == 'console': cfg.console.print(cfg.table)
            return chk

    except Exception as e:
        cfg.table.add_row("Check Publish Standards", "Failed", str(e))
        cfg.console.print(cfg.table)
        return False


def check_plugin_dependencies(publish_list, ftype="job", mode="console"):
    """
    A function that checks if the jobs/views in the given list meets the plugin standards of the production server
    without installing any plugins. The function will return a dictionary containing the jobs/views that do not meet
    the plugin standards. The dictionary will have the job/view name as the key and the list of required plugins
    as the value.

    Parameters:
        - publish_list (list): A list of jobs/views to be checked.
        - ftype (str): The type of the publish_list. It can either be "job" or "view".
        - mode (str): The mode of the function. It can either be "console" or "quiet". In "console" mode, the
                      function will print out the results in a table format. In "quiet" mode, the function will
                      return a dictionary containing the jobs/views that do not meet the plugin standards.

    Returns:
        - dict: A dictionary containing the jobs/views that do not meet the plugin standards. The dictionary will
                have the job/view name as the key and the list of required plugins as the value.
    """
    try:

        cfg.table = Table(show_lines=True, width=cfg.width)
        cfg.table.add_column("Check Plugin Dependencies (w/o Install)", style="cyan", no_wrap=True)

        production_conn = cfg.production_conn
        interim_conn = cfg.interim_conn

        ftype = ftype.lower()
        mode = cfg.mode = mode.lower()

        if not production_conn or not interim_conn:
            raise ValueError("Connection Not Established!")
        if not isinstance(publish_list, list):
            raise TypeError("Publish List Must be a List!")
        if not isinstance(ftype, str):
            raise TypeError("Type Must be a String!")
        if ftype not in ('job', 'view'):
            raise TypeError("Invalid Type Field! Type = [job, view]")
        if mode not in ('console', 'quiet'):
            raise TypeError("Invalid Mode Field! Mode = [console, quiet]")

        if ftype == "job":
            job_plugins = {}
            for job in publish_list:
                cfg.table.add_row("Job", job)
                job_plugins[job] = jbm.check_job_plugins_in_production_without_install(job)
                cfg.table.add_row()

            if mode == 'console': cfg.console.print(cfg.table)
            return job_plugins

        elif ftype == "view":

            interim_views_list = jutils.get_views_list(interim_conn)
            jobs_plugins = {}
            for view in publish_list:
                if view in interim_views_list:
                    cfg.table.add_row("View", view)
                    interim_jobs_list = jutils.get_view_and_its_jobs(interim_conn)[view]
                    for job in interim_jobs_list:
                        chk_plugins = jbm.check_job_plugins_in_production_without_install(job)
                        if chk_plugins:
                            jobs_plugins[job] = chk_plugins
                    cfg.table.add_row()
            if mode == 'console': cfg.console.print(cfg.table)
            return jobs_plugins

    except Exception as e:
        cfg.table.add_row("Check Plugin Dependencies", "Failed", str(e))
        cfg.console.print(cfg.table)
        return {}


def check_and_install_plugin_dependencies(publish_list, ftype="job", mode="console"):
    """
    A function that checks and installs plugins required by jobs in a view or specified jobs
    in a Jenkins server. The function will print out the results in a table format. In "quiet" mode, the function will
    return a boolean indicating whether all plugins were successfully installed.

    Parameters:
        - publish_list: A list of jobs or views to be checked for plugin dependencies.
        - ftype: A string indicating whether the publish_list contains jobs or views. Default is "job".
        - mode: A string indicating whether to print the results in the console or return them as a boolean. Default is "console".
    Returns:
        - bool: A boolean indicating whether all plugins were successfully installed.
    """
    try:

        cfg.table = Table(show_lines=True, width=cfg.width)
        cfg.table.add_column("Check and Install Plugin Dependencies", style="cyan", no_wrap=True)

        production_conn = cfg.production_conn
        interim_conn = cfg.interim_conn
        res = True

        ftype = ftype.lower()
        mode = cfg.mode = mode.lower()

        if not production_conn or not interim_conn:
            raise ValueError("Connection Not Established!")
        if not isinstance(publish_list, list):
            raise TypeError("Publish List Must be a List!")
        if not isinstance(ftype, str):
            raise TypeError("Type Must be a String!")
        if ftype not in ('job', 'view'):
            raise TypeError("Invalid Type Field! Type = [job, view]")
        if mode not in ('console', 'quiet'):
            raise TypeError("Invalid Mode Field! Mode = [console, quiet]")

        if ftype == "job":

            for job in publish_list:
                if not jbm.check_job_plugins_in_production(job):
                    res = False

            if mode == 'console': cfg.console.print(cfg.table)
            return res

        elif ftype == "view":

            interim_views_list = jutils.get_views_list(interim_conn)
            for view in publish_list:
                if view in interim_views_list:
                    interim_jobs_list = jutils.get_view_and_its_jobs(interim_conn)[view]
                    for job in interim_jobs_list:
                        if not jbm.check_job_plugins_in_production(job):
                            res = False

            if mode == 'console': cfg.console.print(cfg.table)
            return res

    except Exception as e:
        cfg.table.add_row("Check and Install Plugin Dependencies", "Failed", str(e))
        cfg.console.print(cfg.table)
        return False


def production_cleanup(mode='console'):
    """
    Function to clean up production views by deleting those with no associated jobs.
    Parameters:
        - mode: A string indicating whether to print the results in the console or return them as a boolean. Default is "console".
    Returns:
        - bool: A boolean indicating whether all views were successfully cleaned up.
    """
    try:
        production_conn = cfg.production_conn
        interim_conn = cfg.interim_conn
        mode = cfg.mode = mode.lower()

        cfg.table = Table(show_lines=True, width=cfg.width)
        cfg.table.add_column("Production CleanUp", style="cyan", no_wrap=True)

        if not production_conn or not interim_conn:
            raise ValueError("Connection Not Established!")
        if mode not in ('console', 'quiet'):
            raise TypeError("Invalid Mode Field! Mode = [console, quiet]")

        res = jbm.production_view_clean_up()
        if mode == 'console': cfg.console.print(cfg.table)

        return res

    except Exception as e:
        cfg.table.add_row("", "Exception (production_cleanup)", str(e))
        cfg.console.print(cfg.table)
        return False


def interim_cleanup(mode='console'):
    """
    Function to clean up interim views by deleting those with no associated jobs.
    
    Parameters:
        - mode: A string indicating whether to print the results in the console or return them as a boolean. Default is "console".
        
    Returns:
        - bool: A boolean indicating whether all views were successfully cleaned up.
    """
    try:
        production_conn = cfg.production_conn
        interim_conn = cfg.interim_conn
        mode = cfg.mode = mode.lower()

        cfg.table = Table(show_lines=True, width=cfg.width)
        cfg.table.add_column("Production CleanUp", style="cyan", no_wrap=True)

        if not production_conn or not interim_conn:
            raise ValueError("Connection Not Established!")
        if mode not in ('console', 'quiet'):
            raise TypeError("Invalid Mode Field! Mode = [console, quiet]")

        res = jbm.interim_view_clean_up()
        if mode == 'console': cfg.console.print(cfg.table)

        return res

    except Exception as e:
        cfg.table.add_row("", "Exception (interim_cleanup)", str(e))
        cfg.console.print(cfg.table)
        return False


def set_console_size(width):
    """
    Sets the console width for the output of the functions.

    Parameters:
        - width (int): The width of the console in characters.

    Returns:
        - None

    Raises:
        - ValueError: If the width is not a valid positive integer.
    """
    try:
        cfg.width = width
    except Exception as e:
        print(e)