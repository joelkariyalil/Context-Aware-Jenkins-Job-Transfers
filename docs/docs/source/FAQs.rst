FAQs
====

Q1: How do I install the module?
------------------------------------
To install the `context-aware-jenkins-job-transfers` module, use pip:

.. code-block:: bash

    (.venv) $ pip install context-aware-jenkins-job-transfers

For more detailed installation steps, refer to the Installation section.

Q2: What Jenkins versions are supported?
--------------------------------------------
The module supports Jenkins versions 2.249.1 and above. Earlier versions may not have full compatibility due to plugin changes.

Q3: How do I connect to my Jenkins server?
---------------------------------------------
You can use the `connect` function to connect to your Jenkins server.

.. code-block:: python

    import jenkins_job_transfers as jt

    jt.connect(
        production_machine_url='http://prod-server-url:port',
        interim_machine_url='http://int-server-url:port',
        production_username='production_username',
        interim_username='interim_username',
        production_password='production_password',
        interim_password='interim_password'
    )

For more details on the connection parameters, see the **Connect to Jenkins Servers** section of this documentation.

Q4: How can I contribute to this project?
--------------------------------------------
Contributions are welcome! Please follow the steps below:

1. Fork the repository on GitHub.
2. Clone your fork to your local machine using:

   .. code-block:: bash

       $ git clone https://github.com/your_username/context-aware-jenkins-job-transfers.git

3. Create a new branch for your feature or bug fix.
4. Make your changes, and commit them with a descriptive message.
5. Push your changes to your fork.
6. Create a Pull Request (PR) on the original repository and assign it to the author or other readers for review.

For detailed contribution guidelines, refer to the **Contributions** section.

Q5: Can I transfer both jobs and views at the same time?
-----------------------------------------------------------
Yes, you can transfer both jobs and views, but they need to be done separately by specifying the `ftype` parameter in the `transfer` function.

Q6: How do I handle plugin dependencies?
-------------------------------------------
You can use the `check_and_install_plugin_dependencies` function to automatically check and install missing dependencies.

.. tip::

    It is recommended to run the plugin checks before transferring jobs to avoid failures.

Q7: What does the 'quiet' mode do?
--------------------------------------
The `quiet` mode suppresses all non-error messages, making the output less verbose. Use `mode="quiet"` if you want to minimize console output.