Supported Functionalities
-------------------------

.. note::

    mode = 'quiet' or 'console'
        - 'quiet' is non-verbose (success, failure messages are NOT printed on console)
        - 'console' is verbose
    By default, mode is 'console'.


----

Connect to Jenkins Servers
___________________

To connect to the production and interim Jenkins servers, use the `connect` function:


**Parameters**
^^^^^^

    - `production_machine_url`: URL of the production Jenkins server.
    - `interim_machine_url`: URL of the interim Jenkins server.
    - `production_username`: Username for the production server.
    - `interim_username`: Username for the interim server.
    - `production_password`: Password for the production server.
    - `interim_password`: Password for the interim server.
    - `mode`: Output mode, either “console” or “quiet”.

.. tip::

    The best security practice would include passing usernames & passwords as .env variables.

    .. code-block:: python

        import os

        production_username = os.environ['production_username']
        production_password = os.environ.get('production_password', None)

**Example usage**
^^^^

.. code-block:: python

    import jenkins_job_transfers as jt

    jt.connect(
        production_machine_url='http://127.0.0.1:8080',
        interim_machine_url='http://127.0.0.1:8081',
        production_username='production_username',
        interim_username='interim_username',
        production_password='production_password',
        interim_password='interim_password',
        mode='quiet'
    )

.. warning::

    Connecting Jenkins servers before initiating other functions is necessary.


----

Transfer Jobs or Views
___________________

To transfer jobs or views from interim to production, use the `transfer` function:

**Parameters**
^^^^^^

    - `publish_list`: List of jobs or views to be transferred.
    - `ftype`: Type of transfer, either “job” or “view”.
    - `mode`: Output mode, either “console” or “quiet”.
    - `allowDuplicates`: Boolean to allow duplicate jobs.

**Example usage**
^^^^

.. code-block:: python

    import jenkins_job_transfers as jt

    # Job Transfers

    jt.transfer(
        ["JobA", "JobB"], 
        ftype="job", 
        mode="console", 
        allowDuplicates=True
    )

    # View Transfer

    jt.transfer(
        ['ViewA', 'ViewB'],
        ftype="view",
        mode="console",
        allowDuplicates=True
    )


----

Check Publish Standards
___________________

To verify if the jobs or views meet the publish standards, use the `check_publish_standards` function:

**Parameters**
^^^^^^

    - `publish_list`: List of jobs or views to check.
    - `ftype`: Type of check, either “job” or “view”.
    - `mode`: Output mode, either “console” or “quiet”.
    - `allowDuplicates`: Boolean to allow duplicate jobs.

**Example usage**
^^^^

.. code-block:: python

    import jenkins_job_transfers as jt

    # Publish Standards Check for Jobs

    jt.check_publish_standards(
        ["job1", "job2"], 
        ftype="job", 
        mode="console"
    )

    # Publish Standards Check for Views
    
    jt.check_publish_standards(
        ["view1", "view2"], 
        ftype="view", 
    )


----

Check Plugin Dependencies
___________________

To check plugin dependencies for jobs or views, use the `check_plugin_dependencies` function:

**Parameters**
^^^^^^

    - `publish_list`: List of jobs or views to check.
    - `ftype`: Type of check, either “job” or “view”.
    - `mode`: Output mode, either “console” or “quiet”.

**Example usage**
^^^^

.. code-block:: python

    import jenkins_job_transfers as jt

    # Check Plugin Dependencies for Jobs

    jt.check_plugin_dependencies(
        ["job1", "job2"], 
        ftype="job", 
        mode="console"
    )

    # Check Plugin Dependencies for Views
    
    jt.check_plugin_dependencies(
        ["view1", "view2"], 
        ftype="view", 
        mode="console"
    )



----

Check and Install Plugin Dependencies
___________________

To check and install missing plugin dependencies, use the `check_and_install_plugin_dependencies` function:

**Parameters**
^^^^^^

    - `publish_list`: List of jobs or views to check and install dependencies for.
    - `ftype`: Type of check, either “job” or “view”.
    - `mode`: Output mode, either “console” or “quiet”.

**Example usage**
^^^^

.. code-block:: python

    import jenkins_job_transfers as jt

    # Check and Install Plugin Dependencies for Jobs

    jt.check_and_install_plugin_dependencies(
        ["job1", "job2"], 
        ftype="job", 
        mode="console"
    )

    # Check and Install Plugin Dependencies for Views

    jt.check_and_install_plugin_dependencies(
        ["view1", "view2"], 
        ftype="view", 
        mode="console"
    )



----

Clean Up Production
___________________

To clean up the production Jenkins server, use the `production_cleanup` function:
All the views without any Jobs in the production are deleted in this operation.

**Parameters**
^^^^^^

    - `mode`: Output mode, either “console” or “quiet”.

**Example usage**
^^^^

.. code-block:: python

    import jenkins_job_transfers as jt

    jt.production_cleanup(mode="console")



----

Clean Up Interim
___________________

To clean up the interim Jenkins server, use the `interim_cleanup` function:
All the views without any jobs in the interim are deleted during this operation.

**Parameters**
^^^^^^

    - `mode`: Output mode, either “console” or “quiet”.

**Example usage**
^^^^

.. code-block:: python

    import jenkins_job_transfers as jt

    jt.interim_cleanup(mode="console")



----

Set Console Size
___________________

To set the width of the console output, use the `set_console_size` function:

**Parameters**
^^^^^^

    - `width`: Desired console width.

**Example usage**
^^^^

.. code-block:: python

    import jenkins_job_transfers as jt

    jt.set_console_size(120)
