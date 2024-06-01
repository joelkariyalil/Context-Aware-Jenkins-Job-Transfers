from . import Jenkins_Base_Module as jbm

'''

Functions to Support

1. connect(production_machine_url, dev_machine_url, production_username, dev_username, production_password, dev_password)
2. transfer_jobs([jobA, jobB, jobC], allowDuplicateJobs = True)
3. transfer_views([viewA, viewB, viewC], allDuplicateJobs = True)
4. check_publish_view_standards([], type="view")
5. check_publish_job_standards([], type="job")
6. check_job_plugin_dependencies([jobA, jobB, jobC])

'''


def connect(production_machine_url, dev_machine_url, production_username, dev_username, production_password,
            dev_password):
    production_conn, server_conn = jbm.establish_connection_to_servers(production_machine_url, dev_machine_url,
                                                                       production_username, dev_username,
                                                                       production_password, production_password,
                                                                       dev_password)
    return production_conn, server_conn


def transfer_jobs(jobs, allowDuplicateJobs=True):
    pass


def transfer_views(views, allDuplicateJobs=True):
    pass


def check_publish_view_standards(views, type="view"):
    pass


def check_publish_job_standards(jobs, type="job"):
    pass



