from . import Jenkins_Base_Module as jbm

'''
Functions to Support

1. connect(production_machine_url, dev_machine_url, production_username, dev_username, production_password, dev_password)
2. transfer(production_conn, interim_conn, publish_list, type="job" or "view", allowDuplicateJobs=False)
3. check_publish_standards(production_conn, interim_conn, publish_list, type="job" or "view", allowDuplicateJobs=False) 
4. check_plugin_dependencies(production_conn, interim_conn, publish_list, type="job" or "view")
5. check_and_install_plugin_dependencies(production_conn, interim_conn, publish_list, type="job" or "view")

mode = "console" or "quiet"

'''


def connect(production_machine_url, interim_machine_url, production_username, interim_username, production_password,
            interim_password):

    global production_conn, interim_conn, production_url, interim_url

    production_url = production_machine_url
    interim_url = interim_machine_url

    production_conn, interim_conn = jbm.establish_connection_to_servers(production_machine_url, interim_machine_url,
                                                                        production_username, interim_username,
                                                                        production_password, interim_password)


def transfer(publish_list, type="job", allowDuplicateJobs=False):
    pass


def check_publish_standards(publish_list, type="job", mode="console", allowDuplicateJobs=False):
    pass


def check_plugin_dependencies(publish_list, type="job", mode="console"):

    global production_conn, interim_conn

    if not production_conn or not interim_conn:
        raise ValueError("Connection Not Established!")
    if not isinstance(publish_list, list):
        raise TypeError("Publish List Must be a List!")
    if not isinstance(type, str):
        raise TypeError("Type Must be a String!")

    plugins_to_install_production = jbm.plugin_differences(production_conn, interim_conn)

    if type == "job":

        for job in publish_list:

            chk_plugins = jbm.check_job_plugins_in_production_without_install(interim_conn, plugins_to_install_production, job, mode)
            if chk_plugins:
                return chk_plugins

    elif type == "view":

        interim_views_list = jbm.get_views_list(interim_conn)
        jobs_plugins = {}
        for view in publish_list:
            if view in interim_views_list:
                interim_jobs_list = jbm.get_view_and_its_jobs(interim_conn)[view]
                for job in interim_jobs_list:
                    chk_plugins = jbm.check_job_plugins_in_production_without_install(interim_conn, plugins_to_install_production, job, mode)
                    if chk_plugins:
                        jobs_plugins[job] = chk_plugins

        return jobs_plugins


def check_and_install_plugin_dependencies(publish_list, type="job", mode="console"):

    try:

        global production_conn, interim_conn, production_url
        type = type.lower()
        mode = mode.lower()

        if not production_conn or not interim_conn:
            raise ValueError("Connection Not Established!")
        if not isinstance(publish_list, list):
            raise TypeError("Publish List Must be a List!")
        if not isinstance(type, str):
            raise TypeError("Type Must be a String!")
        if type not in ('job', 'view'):
            raise TypeError("Invalid Type Field! Type = [job, view]")
        if mode not in ('console', 'quiet'):
            raise TypeError("Invalid Mode Field! Mode = [console, quiet]")

        plugins_to_install_production = jbm.plugin_differences(production_conn, interim_conn)

        if type == "job":

            for job in publish_list:

                return jbm.check_job_plugins_in_production(production_conn, interim_conn, production_url, plugins_to_install_production, job, mode)

        elif type == "view":

            interim_views_list = jbm.get_views_list(interim_conn)
            for view in publish_list:
                if view in interim_views_list:
                    interim_jobs_list = jbm.get_view_and_its_jobs(interim_conn)[view]
                    for job in interim_jobs_list:
                        if not jbm.check_job_plugins_in_production(production_conn, interim_conn, production_url, plugins_to_install_production, job, mode):
                            return False

            return True

    except Exception as e:
        print(f'Error in Check_and_Install_Plugin_Dependencies: {e}')
        return False
