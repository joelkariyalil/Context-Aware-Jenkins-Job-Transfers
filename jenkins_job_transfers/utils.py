import jenkins
from lxml import etree
from . import config as cfg


def get_config_xml(conn, job_name):
    """
    Retrieve the configuration XML for a specific job from the Jenkins server.

    conn: Jenkins server connection object
    job_name: Name of the job to retrieve the configuration XML for

    Returns:
    The configuration XML of the specified job, or None if an exception occurs
    """
    try:
        config_xml = conn.get_job_config(job_name)
    except jenkins.JenkinsException:
        config_xml = None
    return config_xml


def create_job(job_name, config_xml):
    """
    Creates a job on Jenkins-Production using the provided connection, job name, and configuration XML.

    Parameters:
    - job_name: the name of the job to be created
    - config_xml: the XML configuration for the job

    Returns:
    None
    """
    try:
        production_conn = cfg.production_conn
        production_conn.create_job(job_name, config_xml)
        cfg.table.add_row(*["", job_name, 'Job', 'Success', 'Created'])

    except jenkins.JenkinsException as e:
        print(f"FAILED to Create Job. Error: {e}")
        cfg.table.add_row(*["", job_name, 'Job', 'Failed', str(e)])


def update_job(job_name, config_xml):
    """
    A function to update a job on Jenkins-Production with the provided configuration XML.

    Parameters:
    - job_name: the name of the job to be updated
    - config_xml: the new configuration XML for the job

    Returns:
    None
    """
    try:
        production_conn = cfg.production_conn
        production_conn.reconfig_job(job_name, config_xml)
        cfg.table.add_row(*["", job_name, 'Job', 'Success', 'Updated'])
    except jenkins.JenkinsException as e:
        cfg.table.add_row(*["", job_name, 'Job', 'Failed', str(e)])


def delete_job(job_name):
    """
    A function to delete a job on Jenkins-Production.

    Parameters:
    - job_name: the name of the job to be deleted

    Returns:
    None
    """
    try:
        production_conn = cfg.production_conn
        production_conn.delete_job(job_name)
        cfg.table.add_row(*["", job_name, 'Job', 'Success', 'Deleted'])
    except jenkins.JenkinsException as e:
        cfg.table.add_row(*["", job_name, 'Job', 'Failed', str(e)])


def create_view(view_name, config_xml):
    """
        A function to create a specified view in Jenkins production environment.

        Args:
            view_name: Name of the view to be updated.
            config_xml: Configuration XML for the updated view.

        Returns:
            None
    """
    try:
        production_conn = cfg.production_conn
        production_conn.create_view(view_name, config_xml)
        cfg.table.add_row(*["", view_name, 'View', 'Success', 'Created'])
    except jenkins.JenkinsException as e:
        cfg.table.add_row(*["", view_name, 'View', 'Failed', str(e)])


def update_view(view_name, config_xml):
    """
    A function to update a specified view in Jenkins production environment.

    Args:
        view_name: Name of the view to be updated.
        config_xml: Configuration XML for the updated view.

    Returns:
        None
    """
    try:
        production_conn = cfg.production_conn
        production_conn.reconfig_view(view_name, config_xml)
        cfg.table.add_row(*["", view_name, 'View', 'Success', 'Updated'])
    except jenkins.JenkinsException as e:
        cfg.table.add_row(*["", view_name, 'View', 'Failed', str(e)])


def delete_view(view_name):
    """
    A function to delete a specified view in Jenkins production environment.

    Args:
        view_name: Name of the view to be deleted.

    Returns:
        None
    """
    try:
        production_conn = cfg.production_conn
        production_conn.delete_view(view_name)
        cfg.table.add_row(*["", view_name, 'View', 'Success', 'Deleted'])
    except jenkins.JenkinsException as e:
        cfg.table.add_row(*["", view_name, 'View', 'Failed', str(e)])


def get_plugin_list(conn):
    """
    Get a list of plugins using the provided connection object.

    Args:
        conn: The connection object used to retrieve plugin information.

    Returns:
        list: A list of short names of the plugins.
    """
    try:
        plist = []
        for plugin in conn.get_plugins_info():
            plist.append(plugin.get('shortName'))
        return plist
    except Exception as e:
        print("Error in get_plugin_list: ", e)


def get_job_list(conn):
    """
    A function to retrieve a list of job names from the given connection object.

    Parameters:
    conn (connection object): The connection object used to retrieve job information.

    Returns:
    list: A list of job names extracted from the connection object.
    """
    try:
        job_list = []
        for job in conn.get_jobs():
            job_list.append(job['name'])
        return job_list
    except Exception as e:
        print("Error in get_job_list: ", e)


def get_views_list(conn):
    """
    Retrieves a list of views from the given connection.

    Args:
        conn: The connection object used to retrieve the views.

    Returns:
        list: A list of names of the views retrieved from the connection.
    """
    try:
        view_list = []
        for view in conn.get_views():
            view_list.append(view['name'])
        return view_list
    except Exception as e:
        print("Error in get_views_list: ", e)


def get_view_and_its_jobs(conn):
    """
    Generate a dictionary of views and their associated jobs.

    :param conn: The connection object to interact with the system.
    :return: A dictionary containing view names as keys and a list of job names as values.
    """
    try:
        view_list = {}
        for view in conn.get_views():
            if view['name'] != 'all':
                config_xml_views = get_view_config_xml(conn, view['name'])
                root = etree.fromstring(config_xml_views.encode('utf-8'))  # Parse the XML string with lxml
                view_list[view["name"]] = root.xpath('//jobNames/string/text()')
        return view_list
    except Exception as e:
        print("Error in get_view_and_its_jobs: ", e)


def get_view_config_xml(conn, view_name):
    """
    Retrieve the configuration XML for a specific view.

    Args:
        conn: The connection to the Jenkins server.
        view_name: The name of the view for which the configuration XML is to be retrieved.

    Returns:
        The configuration XML for the specified view, or None if an exception occurs.
    """
    try:
        config_xml = conn.get_view_config(view_name)
    except jenkins.JenkinsException:
        config_xml = None
    return config_xml