from . import basemodule as jbm
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
    try:

        if not production_machine_url or not interim_machine_url:
            raise ValueError("Either production_machine_url or interim_machine_url is None.")
        if not production_username or not interim_username:
            raise ValueError("Either production_username or interim_username is None.")
        if not production_password or not interim_password:
            raise ValueError("Either production_password or interim_password is None.")

        cfg.production_url = production_machine_url
        cfg.interim_url = interim_machine_url
        cfg.mode = mode

        cfg.production_conn, cfg.interim_conn = jbm.establish_connection_to_servers(production_machine_url,
                                                                                    interim_machine_url,
                                                                                    production_username,
                                                                                    interim_username,
                                                                                    production_password,
                                                                                    interim_password)

    except Exception as e:
        print("Exception in connect: ", e)


def transfer(publish_list, ftype="job", mode="console", allowDuplicates=False):
    try:

        console = Console()
        cfg.table = Table(title="Transfer Status")

        cfg.table.add_column("Name", "Status", "Description", justify="right", style="cyan", no_wrap=True)

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

            chk = jbm.transfer_jobs(publish_list)
            console.print(cfg.table)
            return chk

        elif ftype == "view":

            chk = jbm.transfer_views(publish_list)
            console.print(cfg.table)
            return chk

    except Exception as e:
        print("Error in transfer: ", e)
        return False


def check_publish_standards(publish_list, ftype="job", mode="console", allowDuplicates=False):
    try:
        console = Console()
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
            console.print(cfg.table)
            return chk

        elif ftype == "view":
            chk = jbm.view_pre_check(publish_list)
            console.print(cfg.table)
            return chk

    except Exception as e:
        print("Error in check_publish_standards: ", e)
        return False


def check_plugin_dependencies(publish_list, ftype="job", mode="console"):
    try:

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

            for job in publish_list:

                chk_plugins = jbm.check_job_plugins_in_production_without_install(job)
                if chk_plugins:
                    return chk_plugins

        elif ftype == "view":

            interim_views_list = jutils.get_views_list(interim_conn)
            jobs_plugins = {}
            for view in publish_list:
                if view in interim_views_list:
                    interim_jobs_list = jutils.get_view_and_its_jobs(interim_conn)[view]
                    for job in interim_jobs_list:
                        chk_plugins = jbm.check_job_plugins_in_production_without_install(job)
                        if chk_plugins:
                            jobs_plugins[job] = chk_plugins

            return jobs_plugins

    except Exception as e:
        print("Error in check_plugin_dependencies: ", e)
        return []


def check_and_install_plugin_dependencies(publish_list, ftype="job", mode="console"):
    try:

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

            for job in publish_list:
                return jbm.check_job_plugins_in_production(job)

        elif ftype == "view":

            interim_views_list = jutils.get_views_list(interim_conn)
            for view in publish_list:
                if view in interim_views_list:
                    interim_jobs_list = jutils.get_view_and_its_jobs(interim_conn)[view]
                    for job in interim_jobs_list:
                        if not jbm.check_job_plugins_in_production(job):
                            return False

            return True

    except Exception as e:
        print(f'Error in Check_and_Install_Plugin_Dependencies: {e}')
        return False


def production_cleanup(mode='console'):

    try:
        production_conn = cfg.production_conn
        interim_conn = cfg.interim_conn
        mode = cfg.mode = mode.lower()

        if not production_conn or not interim_conn:
            raise ValueError("Connection Not Established!")
        if mode not in ('console', 'quiet'):
            raise TypeError("Invalid Mode Field! Mode = [console, quiet]")

        return jbm.production_view_clean_up()

    except Exception as e:
        print("Error in production_cleanup: ", e)
        return False


def interim_cleanup(mode='console'):

    try:
        production_conn = cfg.production_conn
        interim_conn = cfg.interim_conn
        mode = cfg.mode = mode.lower()

        if not production_conn or not interim_conn:
            raise ValueError("Connection Not Established!")
        if mode not in ('console', 'quiet'):
            raise TypeError("Invalid Mode Field! Mode = [console, quiet]")

        return jbm.interim_view_clean_up()

    except Exception as e:
        print("Error in interim_cleanup: ", e)
        return False
