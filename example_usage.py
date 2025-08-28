"""
Example usage of the refactored Jenkins Job Transfers library.

This demonstrates both the new API and backward compatibility.
"""

# Example 1: New API (Recommended)
def example_new_api():
    """Demonstrate the new, improved API."""
    from jenkins_job_transfers import create_manager, TransferOptions, OperationMode
    
    # Create a manager with clean dependency injection
    manager = create_manager(
        production_url="https://production.jenkins.com",
        interim_url="https://interim.jenkins.com",
        production_username="prod_user",
        interim_username="interim_user",
        production_password="prod_password",
        interim_password="interim_password"
    )
    
    # Test connections
    if not manager.connect():
        print("Failed to connect to Jenkins servers")
        return
    
    # Transfer jobs with type safety and clear options
    options = TransferOptions(
        allow_duplicates=False,
        mode=OperationMode.CONSOLE,
        install_missing_plugins=True
    )
    
    result = manager.transfer_jobs(["job1", "job2", "job3"], options)
    
    print(f"Transfer completed with {result.success_rate:.1f}% success rate")
    print(f"Successful jobs: {result.successful_jobs}")
    print(f"Failed jobs: {result.failed_jobs}")
    
    # Transfer views
    view_result = manager.transfer_views(["view1", "view2"], options)
    
    # Check plugin dependencies without installing
    missing_plugins = manager.check_job_plugin_dependencies(["job4", "job5"])
    print(f"Missing plugins: {missing_plugins}")
    
    # Cleanup servers
    cleanup_result = manager.cleanup_production()
    print(f"Cleaned up {len(cleanup_result.successful_views)} empty views")


# Example 2: Backward Compatible API
def example_legacy_api():
    """Demonstrate backward compatibility with existing code."""
    import jenkins_job_transfers as jjt
    
    # Old API still works exactly the same
    success = jjt.connect(
        "https://production.jenkins.com",
        "https://interim.jenkins.com", 
        "prod_user",
        "interim_user",
        "prod_password",
        "interim_password",
        mode="console"
    )
    
    if not success:
        print("Connection failed")
        return
    
    # Transfer jobs - same interface as before
    transfer_success = jjt.transfer(
        ["job1", "job2"], 
        ftype="job", 
        allowDuplicates=False
    )
    
    # Check standards - same as before
    standards_ok = jjt.check_publish_standards(
        ["job3", "job4"],
        ftype="job"
    )
    
    # Check and install plugins - same as before
    plugins_ok = jjt.check_and_install_plugin_dependencies(
        ["job5", "job6"],
        ftype="job"
    )
    
    # Cleanup - same as before
    jjt.production_cleanup()
    jjt.interim_cleanup()


# Example 3: Advanced usage with configuration objects
def example_advanced_api():
    """Demonstrate advanced usage with configuration objects."""
    from jenkins_job_transfers import (
        create_manager_from_configs, JenkinsConfig, ApplicationConfig,
        TransferOptions, OperationMode
    )
    
    # Create detailed configurations
    prod_config = JenkinsConfig(
        url="https://production.jenkins.com",
        username="prod_user", 
        password="prod_password",
        timeout=60
    )
    
    interim_config = JenkinsConfig(
        url="https://interim.jenkins.com",
        username="interim_user",
        password="interim_password", 
        timeout=30
    )
    
    app_config = ApplicationConfig(
        console_width=120,
        default_mode=OperationMode.CONSOLE,
        log_level="DEBUG"
    )
    
    # Create manager with full configuration control
    manager = create_manager_from_configs(
        production_config=prod_config,
        interim_config=interim_config,
        app_config=app_config
    )
    
    # Use with detailed options
    options = TransferOptions(
        allow_duplicates=True,
        retry_count=5,
        timeout_seconds=120,
        install_missing_plugins=True
    )
    
    # Get job lists from servers
    interim_jobs = manager.get_job_list("interim")
    production_jobs = manager.get_job_list("production")
    
    print(f"Interim server has {len(interim_jobs)} jobs")
    print(f"Production server has {len(production_jobs)} jobs")
    
    # Transfer with comprehensive result handling
    result = manager.transfer_jobs(interim_jobs[:5], options)
    
    if result.has_failures:
        print("Some transfers failed:")
        for job, error in result.failed_jobs.items():
            print(f"  {job}: {error}")
    
    if result.warnings:
        print("Warnings:")
        for warning in result.warnings:
            print(f"  {warning}")


# Example 4: Error handling with specific exceptions
def example_error_handling():
    """Demonstrate proper error handling with specific exceptions."""
    from jenkins_job_transfers import (
        create_manager, ValidationError, ConnectionError, 
        JobNotFoundError, PluginMissingError
    )
    
    try:
        manager = create_manager(
            production_url="https://production.jenkins.com",
            interim_url="https://interim.jenkins.com",
            production_username="prod_user",
            interim_username="interim_user",
            production_password="prod_password", 
            interim_password="interim_password"
        )
        
        # This will test the connection
        manager.connect()
        
        # Transfer jobs with specific error handling
        result = manager.transfer_jobs(["nonexistent-job"])
        
    except ValidationError as e:
        print(f"Invalid input: {e}")
    except ConnectionError as e:
        print(f"Connection failed: {e}")
    except JobNotFoundError as e:
        print(f"Job not found: {e.job_name} on {e.server}")
    except PluginMissingError as e:
        print(f"Missing plugins: {e.missing_plugins}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    print("=== Jenkins Job Transfers - Refactored API Examples ===\n")
    
    print("1. New API Example:")
    try:
        example_new_api()
    except Exception as e:
        print(f"Example failed (expected - no real Jenkins servers): {e}")
    
    print("\n2. Legacy API Example:")
    try:
        example_legacy_api()
    except Exception as e:
        print(f"Example failed (expected - no real Jenkins servers): {e}")
    
    print("\n3. Advanced API Example:")
    try:
        example_advanced_api()
    except Exception as e:
        print(f"Example failed (expected - no real Jenkins servers): {e}")
    
    print("\n4. Error Handling Example:")
    try:
        example_error_handling()
    except Exception as e:
        print(f"Example failed (expected - no real Jenkins servers): {e}")
    
    print("\n=== Examples completed ===")