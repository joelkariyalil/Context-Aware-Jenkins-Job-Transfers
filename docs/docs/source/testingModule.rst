Testing Module Developments
-----------------------------

This is an attempt to ensure that the module developers would be able to run a basic module-verification-test to ensure the correct working of the module's core functionalities.

py-test module has been included as a dependency for the Context Aware Jenkins Job Transfers Module.

Here is the code required to run the pytest.

.. code-block:: bash

    # Code to ensure the current directory in the jenkins_job_transfers
    $pwd
    **/jenkins_job_transfers

    # Run pytest with the required arguments
    pytest --production_username prod --production_password prod --interim_username dev --interim_password dev --production_url http://localhost:8080 --interim_url http://localhost:8081 --verbose

Note:
The variables passed in the pytest can be passed as environment variables to avoid security faults.

Sample Output:
-----------------------------

Below is a --verbose example of running pytest for the Context-Aware Jenkins Job Transfers module:

    .. code-block:: text

        =================================================================================== test session starts ===================================================================================
        platform win32 -- Python 3.12.5, pytest-8.3.4, pluggy-1.5.0 -- F:\Projects\Context-Aware-Jenkins-Job-Transfers\.venv\Scripts\python.exe
        cachedir: .pytest_cache | rootdir: F:\Projects\Context-Aware-Jenkins-Job-Transfers | configfile: pyproject.toml | plugins: order-1.3.0 | collected 19 items

        tests\test_servers.py::test_servers_alive PASSED [  5%]
        tests\test_check_and_install_plugin_dependencies.py::test_check_and_install_plugin_dependencies_quiet_negative PASSED [ 10%]
        tests\test_check_and_install_plugin_dependencies.py::test_check_and_install_plugin_dependencies_quiet_positive PASSED [ 15%]
        tests\test_check_and_install_plugin_dependencies.py::test_check_and_install_plugin_dependencies_console_negative PASSED [ 21%]
        tests\test_check_and_install_plugin_dependencies.py::test_check_and_install_plugin_dependencies_console_positive PASSED [ 26%]
        tests\test_check_plugin_dependencies.py::test_check_plugin_dependencies_quiet_negative PASSED [ 31%]
        tests\test_check_plugin_dependencies.py::test_check_plugin_dependencies_quiet_positive PASSED [ 36%]
        tests\test_check_plugin_dependencies.py::test_check_plugin_dependencies_console_negative PASSED [ 42%]
        tests\test_check_plugin_dependencies.py::test_check_plugin_dependencies_console_positive PASSED [ 47%]
        tests\test_connect.py::test_connect_quiet PASSED [ 52%]
        tests\test_connect.py::test_connect_console PASSED [ 57%]
        tests\test_connect.py::test_invalid_credentials_quiet PASSED [ 63%]
        tests\test_connect.py::test_invalid_credentials_console PASSED [ 68%]
        tests\test_interim_cleanup.py::test_interim_cleanup PASSED [ 73%]
        tests\test_production_cleanup.py::test_production_cleanup PASSED [ 78%]
        tests\test_transfer.py::test_transfer_job_with_plugins_no_views_quiet PASSED [ 84%]
        tests\test_transfer.py::test_transfer_job_without_plugins_no_views PASSED [ 89%]
        tests\test_transfer.py::test_transfer_job_with_plugins_with_views PASSED [ 94%]
        tests\test_transfer.py::test_transfer_views PASSED [100%]

        ==================================================================================== warnings summary =====================================================================================
        jenkins_job_transfers/tests/test_check_and_install_plugin_dependencies.py: 8 warnings
        jenkins_job_transfers/tests/test_check_plugin_dependencies.py: 8 warnings
        jenkins_job_transfers/tests/test_transfer.py: 2 warnings
        F:\Projects\Context-Aware-Jenkins-Job-Transfers\.venv\Lib\site-packages\jenkins\__init__.py:940: DeprecationWarning: get_plugins_info() is deprecated, use get_plugins()
        warnings.warn("get_plugins_info() is deprecated, use get_plugins()",)

        -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
        ============================================================================ 19 passed, 18 warnings in 28.61s =============================================================================
    

This confirms that the core functionalities of the module are working as expected.
