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
    try:

        cfg.table = Table(show_lines=True, width=cfg.width)
        cfg.table.add_column("Check Publish Standards (w/o Install)", style="cyan", no_wrap=True)

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
            res = True
            for job in publish_list:
                cfg.table.add_row("Job", job)
                if not jbm.check_job_plugins_in_production_without_install(job):
                    res = False
                cfg.table.add_row()

            if mode == 'console': cfg.console.print(cfg.table)
            return res

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
        return []


def check_and_install_plugin_dependencies(publish_list, ftype="job", mode="console"):
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
    try:
        cfg.width = width
    except Exception as e:
        print(e)