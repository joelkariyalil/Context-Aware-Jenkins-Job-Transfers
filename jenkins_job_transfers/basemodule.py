"""

Summary - Code that Transfers Job b/w Jenkins Servers without requiring a server restart.
Created by - Joel Thomas Chacko; joelkariyalil@gmail.com
Created On - 12-03-2024

"""

import jenkins
from lxml import etree
import json
from . import utils as jutils
from . import config as cfg


def establish_connection_to_servers(production_url, interim_url, production_username, interim_username,
                                    production_password, interim_password):
    """
    Establishes connection to servers using the provided production and interim URLs, username, and password.

    Parameters:
    - production_url (str): The URL for the production server.
    - interim_url (str): The URL for the interim server.
    - username (str): The username for authentication.
    - password (str): The password for authentication.

    Returns:
    - production_server (jenkins.Jenkins): Connection to the production server.
    - interim_server (jenkins.Jenkins): Connection to the interim server.
    """
    try:
        mode = cfg.mode
        production_server = jenkins.Jenkins(production_url, username=production_username, password=production_password)
        interim_server = jenkins.Jenkins(interim_url, username=interim_username, password=interim_password)
        if mode == 'console': print('Connection Established')
        return production_server, interim_server
    except Exception as e:
        if mode == 'console': print('Exception in Establishing Connection: ', e)


def install_plugin_in_production(to_install_plugins_list):
    """
    Installs a list of plugins in the production environment.

    Args:
        to_install_plugins_list (list): A list of plugins to be installed.

    Returns:
        bool: True if all plugins are successfully installed, False otherwise.
    """
    try:
        production_conn = cfg.production_conn
        mode = cfg.mode
        flag_installed = []
        for plugin in to_install_plugins_list:
            try:
                if mode == 'console': print(f'INSTALLING: {plugin}')
                flag_installed.append(production_conn.install_plugin(plugin))
            except Exception as e:
                if mode == 'console': print(f"FAILED to Install Plugin. Error: {e}")
        if False in flag_installed:
            return False
        else:
            return True
    except Exception as e:
        print("Error in install_plugin_in_production: ", e)


def plugin_differences():
    """
    Calculate the differences in plugins between two database connections.
    :return: A list of plugins that are in the interim database but not in the production database.
    """
    try:
        production_conn = cfg.production_conn
        interim_conn = cfg.interim_conn

        if not production_conn or not interim_conn:
            raise ValueError("Either production_conn or interim_conn is None.")

        return list(set(jutils.get_plugin_list(interim_conn)).difference(jutils.get_plugin_list(production_conn)))
    except Exception as e:
        print("Error in plugin_differences: ", e)


def check_job_plugins_in_production(job):
    """
    A function to check and install job-specific plugins in a production environment.

    Args:
        job: The job for which plugins are being checked and installed.

    Returns:
        bool: True if all plugins were successfully installed, False otherwise.
    """
    try:
        interim_conn = cfg.interim_conn
        plugins_to_install_production = plugin_differences()
        mode = cfg.mode
        production_url = cfg.production_url

        config_xml = jutils.get_config_xml(interim_conn, job)
        if mode == 'console': print(f'\nPLUGIN CHECK FOR {job}\n')
        if mode == 'console': print(f"Production URL: {production_url}")
        job_specific_plugins = get_job_specific_plugins(
            config_xml)  # returns a list of jobs required for a particular job in interim
        plugins_to_install = list(set(plugins_to_install_production) & set(job_specific_plugins))
        if mode == 'console': print(f'Plugins to be INSTALLED for {job}: {plugins_to_install}')
        chk_flag = install_plugin_in_production(plugins_to_install)
        if chk_flag:
            if mode == 'console': print(f'All Plugins INSTALLED in Production Server {production_url}\n\n')
            return True
        else:
            if mode == 'console': print(f'Install INITIATED, Please RESTART Production Server {production_url}\n\n')
            return False
    except Exception as e:
        print("Error in check_job_plugins_in_production: ", e)
        return False


def check_job_plugins_in_production_without_install(job):
    """
    A function to check and install job-specific plugins in a production environment.

    Args:
        job: The job for which plugins are being checked and installed.

    Returns:
        bool: True if all plugins were successfully installed, False otherwise.
    """
    try:
        plugins_to_install_production = plugin_differences()
        interim_conn = cfg.interim_conn
        mode = cfg.mode
        config_xml = jutils.get_config_xml(interim_conn, job)
        if mode == 'console': print(f'\nPLUGIN CHECK FOR {job}\n')
        job_specific_plugins = get_job_specific_plugins(
            config_xml)  # returns a list of jobs required for a particular job in interim
        plugins_to_install = list(set(plugins_to_install_production) & set(job_specific_plugins))
        if mode == 'console': print(f'Plugins to be INSTALLED for {job}: {plugins_to_install}')
        return plugins_to_install
    except Exception as e:
        print("Error in check_job_plugins_in_production: ", e)
        return []


def get_job_specific_plugins(config_xml):
    """
    Get job specific plugins from the given config XML.

    Parameters:
    - config_xml (str): The XML configuration to extract plugin information from.

    Returns:
    - list: A list of names of job-specific plugins extracted from the XML.
    """

    try:
        plugin_names = []
        try:
            tree = etree.fromstring(config_xml.encode())
        except etree.XMLSyntaxError as e:
            print(f"Error parsing XML: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []

        plugin_elements = tree.xpath('//*[@plugin]')
        for plugin_attr in plugin_elements:
            plugin_name = plugin_attr.attrib['plugin'].split('@')[0]  # Get Name w/o Version
            plugin_names.append(plugin_name)

        return plugin_names
    except Exception as e:
        print("Error in get_job_specific_plugins: ", e)


def check_views(job_to_update, view_to_update='throughall'):
    """
    A function to check and update views in production based on jobs and views in interim connection.

    Parameters:
    - production_conn: Connection to the production environment.
    - interim_conn: Connection to the interim environment.
    - job_to_update: Job to be updated.
    - view_to_update: The view to be updated (default is 'throughall').

    Returns:
    None
    """
    try:
        production_conn = cfg.production_conn
        interim_conn = cfg.interim_conn

        # Get Views
        interim_specific_views_and_jobs = jutils.get_view_and_its_jobs(interim_conn)
        # print('Interim Jobs and Views', interim_specific_views_and_jobs)
        production_specific_views_and_jobs = jutils.get_view_and_its_jobs(production_conn)
        # print('Production Jobs and Views', production_specific_views_and_jobs)

        for view, jobs in interim_specific_views_and_jobs.items():

            # the below if condition is to narrow down the update/create operations

            if job_to_update in jobs and view_to_update == 'throughall' or job_to_update in \
                    production_specific_views_and_jobs.get(view, '') and view_to_update == 'throughall':
                if view in production_specific_views_and_jobs.keys():  # update view if present!
                    if job_to_update in jobs or production_specific_views_and_jobs[view]:
                        # now check if the view exists, else create one!
                        config_xml = jutils.get_view_config_xml(interim_conn, view)
                        if config_xml:
                            jutils.update_view(view, config_xml)
                else:
                    if job_to_update in jobs:  # create view if not present!
                        config_xml = jutils.get_view_config_xml(interim_conn, view)
                        if config_xml:
                            jutils.create_view(view, config_xml)

            elif job_to_update in jobs and view_to_update == view or job_to_update in production_specific_views_and_jobs.get(
                    view, '') and view_to_update == view:
                if view in production_specific_views_and_jobs.keys():
                    if job_to_update in jobs or production_specific_views_and_jobs[view]:
                        # now check if the view exists, else create one!
                        config_xml = jutils.get_view_config_xml(interim_conn, view)
                        if config_xml:
                            jutils.update_view(view, config_xml)
                else:
                    if job_to_update in jobs:
                        config_xml = jutils.get_view_config_xml(interim_conn, view)
                        if config_xml:
                            jutils.create_view(view, config_xml)

    except Exception as e:
        print("Error in check_views: ", e)


def production_view_clean_up():
    """
    Function to clean up production views by deleting those with no associated jobs.
    """
    try:

        production_conn = cfg.production_conn
        production_url = cfg.production_url
        mode = cfg.mode
        production_specific_views_and_jobs = jutils.get_view_and_its_jobs(production_conn)
        for view, jobs in production_specific_views_and_jobs.items():
            if len(jobs) == 0:
                production_conn.delete_view(view)
                if mode == 'console': print(f'View {view} Deleted')
        if mode == 'console': print(f'\n\n\nProduction Server {production_url} Cleaned!\n\n\n')
        return True

    except Exception as e:
        print("Exception in production_view_clean_up! Error: ", e)
        return False


def interim_view_clean_up():
    """
    Function to clean up interim views by deleting those with no associated jobs.
    """
    try:

        interim_conn = cfg.interim_conn
        interim_url = cfg.interim_url
        mode = cfg.mode
        interim_specific_views_and_jobs = jutils.get_view_and_its_jobs(interim_conn)
        for view, jobs in interim_specific_views_and_jobs.items():
            if len(jobs) == 0:
                interim_conn.delete_view(view)
                if mode == 'console': print(f'View {view} Deleted')
        if mode == 'console': print(f'\n\n\nInterim Server {interim_url} Cleaned!\n\n\n')
        return True

    except Exception as e:
        print("Exception in interim_view_clean_up! Error: ", e)
        return False


def chk_publish_job_standards(job_to_update):
    """
    Check if a job meets certain standards by comparing it with views and jobs from different connections.

    Parameters:
    job_to_update (str): The job to be checked against the views and jobs.

    Returns:
    bool: True if the job meets the standards, False otherwise.
    """
    try:

        production_conn = cfg.production_conn
        interim_conn = cfg.interim_conn
        allowDuplicates = cfg.allowDuplicates
        mode = cfg.mode

        view_list = []
        interim_specific_views_and_jobs = jutils.get_view_and_its_jobs(interim_conn)
        production_specific_views_and_jobs = jutils.get_view_and_its_jobs(production_conn)

        for view, jobs in interim_specific_views_and_jobs.items():
            if job_to_update in jobs or job_to_update in production_specific_views_and_jobs.get(view, ''):
                view_list.append(view)

        if len(view_list) == 1:
            return True

        elif len(view_list) == 0:
            if mode == 'console': print(f"\n\nNOT PRESENT IN ANY VIEW: Job\t\t->\t{job_to_update}\n\n")
            return False

        else:
            if allowDuplicates:
                return True
            if mode == 'console': print(f"\n\nDUPLICATES of {job_to_update} Exists on Views\t\t->\t{view_list}\n\n")
            return False

    except Exception as e:
        print("Error in chk_publish_job_standards: ", e)
        return False


def view_pre_check(views_name_list):
    """
    A function that performs pre-checks on a list of views by checking their associated jobs against publish job standards.

    Parameters:
    - views_name_list: a list of view names to be checked

    Returns:
    - True if all jobs associated with the views pass the standards, False otherwise
    """
    try:
        interim_conn = cfg.interim_conn
        interim_specific_views_and_jobs = jutils.get_view_and_its_jobs(interim_conn)
        for view in views_name_list:
            for job in interim_specific_views_and_jobs[view]:
                if not chk_publish_job_standards(job):
                    return False
        return True
    except Exception as e:
        print("Error in view_pre_check: ", e)
        return False


def job_pre_check(jobs_name_list):
    """
    A function that performs pre-checks on a list of job names to ensure they meet publishing standards.

    Parameters:
    jobs_name_list (list): A list of job names to be checked.

    Returns:
    bool: True if all jobs meet publishing standards, False otherwise.
    """
    global mode
    try:
        mode = cfg.mode
        for job in jobs_name_list:
            if mode == 'console': print('\n' + job, end='\n' + '_' * 101 + '\n\n')
        for job in jobs_name_list:
            if not chk_publish_job_standards(job):
                return False
            else:
                if mode == 'console': print(f"\n\n{job} meets requirements for publishing!\n\n")

        return True

    except Exception as e:
        if mode == 'console': print("Error in job_pre_check: ", e)


def pre_check(list_name, action):
    """
    A function to perform pre-checks based on the action provided and the list of items and create check.json

    Parameters:
    - action (str): The type of action to be performed.
    - list_name (list): The list of items to be checked.

    Returns:
    - None
    """
    try:
        data = {"result": False, "job_list": None}
        interim_conn = cfg.interim_conn
        production_url = cfg.production_url
        interim_url = cfg.interim_url
        if action == 'job':

            temp = []
            job_name_list = list_name
            # Performing Pre-Check here, ensuring that there are no duplicate jobs present and plugins exist!
            if job_pre_check(job_name_list):
                for job in job_name_list:
                    config_xml = jutils.get_config_xml(interim_conn, job)
                    if config_xml:
                        job_specific_plugins_exist = check_job_plugins_in_production(job)
                        if job_specific_plugins_exist:
                            temp.append(True)
                        else:
                            temp.append(False)
                            print(f'Job Specific Plugin NOT INSTALLED in Production Server: {production_url}')
                    else:
                        temp.append(False)
                        print(f"{job}'s config.xml NOT RETRIEVED in Interim Server: {interim_url}")
                    print('_' * 101 + '\n\n')

                if False in temp:
                    result = False
                else:
                    result = True

            else:
                result = False

            data = {"result": result, "job_list": ", ".join(job_name_list)}

        elif action == "view":

            view_name_list = list_name
            temp = []
            job_list = []
            if view_pre_check(view_name_list):
                for view in view_name_list:
                    for job in jutils.get_view_and_its_jobs(interim_conn)[view]:
                        job_list.append(job)
                        config_xml = jutils.get_config_xml(interim_conn, job)
                        if config_xml:
                            job_specific_plugins_exist = check_job_plugins_in_production(job)
                            if job_specific_plugins_exist:
                                temp.append(True)
                            else:
                                temp.append(False)
                                print(f'Job Specific Plugin {job} NOT INSTALLED in Production Server: {production_url}')
                        else:
                            temp.append(False)
                            print(f"{job}'s config.xml NOT RETRIEVED in Interim Server: {interim_url}")
                        print('_' * 101 + '\n\n')

                if False in temp:
                    result = False
                else:
                    result = True

            else:
                result = False

            data = {"result": result, "job_list": ", ".join(job_list)}

        with open("check.json", "w") as f:
            json.dump(data, f, indent=4)

    except Exception as e:
        print(f"Error pre_check: {e}")


def transfer_jobs(job_name_list):
    try:
        production_conn = cfg.production_conn
        interim_conn = cfg.interim_conn
        production_url = cfg.production_url
        interim_url = cfg.interim_url
        mode = cfg.mode
        allow_duplicates = cfg.allowDuplicates

        # Performing Pre-Check here, ensuring that there are no duplicate jobs present!
        if not allow_duplicates:

            if not job_pre_check(job_name_list):
                if mode == 'console': print('Error: Duplicate Job(s) present')
                return -1

        interim_jobs_list = jutils.get_job_list(interim_conn)
        production_jobs_list = jutils.get_job_list(production_conn)

        if mode == 'console': print('\n\nJOB MOVEMENT DETAILS\n')
        # Update Specific Jobs
        if len(job_name_list) != 0:
            for job in job_name_list:
                if mode == 'console': print('\n' + job, end='\n' + '_' * 101 + '\n\n')
                if job in interim_jobs_list:
                    config_xml = jutils.get_config_xml(interim_conn, job)
                    if config_xml:

                        job_specific_plugins_exist = check_job_plugins_in_production(job)

                        if job_specific_plugins_exist:

                            if mode == 'console': print('PUBLISHING DETAILS\n')
                            if job in production_jobs_list:
                                jutils.update_job(job, config_xml)
                            else:
                                jutils.create_job(job, config_xml)
                            check_views(job)

                        else:
                            if mode == 'console': print(
                                f"Job Specific Plugin NOT INSTALLED in Production Server: {production_url}")
                    else:
                        if mode == 'console': print(
                            f"{job}'s config.xml NOT RETRIEVED in Interim Server: {interim_url}")
                else:
                    if mode == 'console': print(f"{job} DOES NOT Exist in Interim Server: {interim_url}")
                    if job in production_jobs_list:
                        jutils.delete_job(job)

                if mode == 'console': print('_' * 101 + '\n\n')

        else:
            if mode == 'console': print('Enter Job Details to Move/Update')
            return False

        production_view_clean_up()
        return True

    except Exception as e:
        print("Error in transfer_jobs: ", e)
        return False


def transfer_views(views_name_list):
    try:

        production_conn = cfg.production_conn
        interim_conn = cfg.interim_conn
        interim_url = cfg.interim_url
        mode = cfg.mode
        allow_duplicates = cfg.allowDuplicates
        production_url = cfg.production_url

        job = ''
        flag_update = False

        production_jobs_list = jutils.get_job_list(production_conn)
        interim_views_list = jutils.get_views_list(interim_conn)

        # Performing Pre-Check here, ensuring that there are no duplicate jobs present!
        if not allow_duplicates:
            if not view_pre_check(views_name_list):
                if mode == 'console': print('Error: Duplicate View(s) present')
                return False

        if mode == 'console': print('\n\nVIEW MOVEMENT DETAILS\n')
        # Update Specific Views, and all jobs within
        if len(views_name_list) != 0:
            for view in views_name_list:
                if mode == 'console': print('\n' + view, end='\n' + '_' * 101 + '\n\n')
                if view in interim_views_list:
                    interim_jobs_list = jutils.get_view_and_its_jobs(interim_conn)[view]
                    for job in interim_jobs_list:
                        if mode == 'console': print('\n' + job, end='\n' + '_' * 101 + '\n\n')
                        # check the required plugins are installed in the Production, if not, skip
                        config_xml = jutils.get_config_xml(interim_conn, job)
                        if config_xml:

                            job_specific_plugins_exist = check_job_plugins_in_production(job)
                            if job_specific_plugins_exist:

                                if mode == 'console': print('PUBLISHING DETAILS\n')
                                if job in production_jobs_list:
                                    flag_update = True
                                    jutils.update_job(job, config_xml)
                                else:
                                    flag_update = True
                                    jutils.create_job(job, config_xml)

                            else:
                                if mode == 'console': print(
                                    f'Job Specific Plugin NOT INSTALLED in Production Server: {production_url}')
                        else:
                            if mode == 'console': print(
                                f"{job}'s config.xml NOT RETRIEVED in Interim Server: {interim_url}")
                        if mode == 'console': print('_' * 101 + '\n\n')

                else:
                    if mode == 'console': print(f"{view} DOES NOT Exist in Interim Server: {interim_url}")
                    if view in production_jobs_list:
                        jutils.delete_view(view)

                # Updating the View once the jobs have been updated/created
                if flag_update:
                    check_views(job, view)
                flag_update = False

        else:
            if mode == 'console': print('Enter View Details to Move/Update')

        production_view_clean_up()
        return True

    except Exception as e:
        print("Error in transfer_views: ", e)
        return False
