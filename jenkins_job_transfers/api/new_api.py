"""
New improved API for Jenkins Job Transfers with backward compatibility.

This module provides the new clean API while maintaining backward compatibility
with the existing interface.
"""

from typing import List, Dict, Optional, Union
import logging

from ..types import JenkinsConfig, ApplicationConfig, TransferOptions, OperationMode
from ..core import JenkinsTransferManager
from ..types import ValidationError, JenkinsTransferError

# Global manager instance for backward compatibility
_global_manager: Optional[JenkinsTransferManager] = None


def create_manager(
    production_url: str,
    interim_url: str,
    production_username: str,
    interim_username: str,
    production_password: str,
    interim_password: str,
    app_config: Optional[ApplicationConfig] = None,
    logger: Optional[logging.Logger] = None
) -> JenkinsTransferManager:
    """
    Create a new JenkinsTransferManager instance.
    
    This is the recommended way to use the new API. It provides full control
    over configuration and doesn't rely on global state.
    
    Args:
        production_url: Production Jenkins server URL
        interim_url: Interim Jenkins server URL
        production_username: Production server username
        interim_username: Interim server username
        production_password: Production server password
        interim_password: Interim server password
        app_config: Application configuration (optional)
        logger: Logger instance (optional)
        
    Returns:
        Configured JenkinsTransferManager instance
        
    Example:
        >>> manager = create_manager(
        ...     "https://production.jenkins.com",
        ...     "https://interim.jenkins.com", 
        ...     "prod_user", "interim_user",
        ...     "prod_pass", "interim_pass"
        ... )
        >>> result = manager.transfer_jobs(["job1", "job2"])
    """
    production_config = JenkinsConfig(
        url=production_url,
        username=production_username,
        password=production_password
    )
    
    interim_config = JenkinsConfig(
        url=interim_url,
        username=interim_username,
        password=interim_password
    )
    
    return JenkinsTransferManager(
        production_config=production_config,
        interim_config=interim_config,
        app_config=app_config,
        logger=logger
    )


def create_manager_from_configs(
    production_config: JenkinsConfig,
    interim_config: JenkinsConfig,
    app_config: Optional[ApplicationConfig] = None,
    logger: Optional[logging.Logger] = None
) -> JenkinsTransferManager:
    """
    Create a JenkinsTransferManager from configuration objects.
    
    Args:
        production_config: Production Jenkins configuration
        interim_config: Interim Jenkins configuration
        app_config: Application configuration (optional)
        logger: Logger instance (optional)
        
    Returns:
        Configured JenkinsTransferManager instance
    """
    return JenkinsTransferManager(
        production_config=production_config,
        interim_config=interim_config,
        app_config=app_config,
        logger=logger
    )


# Backward compatibility functions that maintain the old API
def connect(
    production_machine_url: str, 
    interim_machine_url: str, 
    production_username: str, 
    interim_username: str, 
    production_password: str,
    interim_password: str, 
    mode: str = "console"
) -> bool:
    """
    Backward compatible connect function.
    
    Establishes connections to Jenkins servers and stores the manager globally.
    This maintains the old API behavior for existing code.
    """
    global _global_manager
    
    try:
        # Convert mode to enum
        operation_mode = OperationMode.CONSOLE if mode == "console" else OperationMode.QUIET
        app_config = ApplicationConfig(default_mode=operation_mode)
        
        # Create manager
        _global_manager = create_manager(
            production_machine_url,
            interim_machine_url,
            production_username,
            interim_username,
            production_password,
            interim_password,
            app_config
        )
        
        # Test connections
        return _global_manager.connect()
        
    except Exception as e:
        if _global_manager and _global_manager.reporter:
            _global_manager.reporter.print_error("Connection failed", str(e))
        return False


def transfer(
    publish_list: List[str], 
    ftype: str = "job", 
    allowDuplicates: bool = False, 
    mode: str = "console"
) -> bool:
    """
    Backward compatible transfer function.
    
    Transfers jobs or views using the globally stored manager.
    """
    global _global_manager
    
    if _global_manager is None:
        raise JenkinsTransferError("No connection established. Call connect() first.")
    
    try:
        # Convert parameters to new format
        operation_mode = OperationMode.CONSOLE if mode == "console" else OperationMode.QUIET
        options = TransferOptions(
            allow_duplicates=allowDuplicates,
            mode=operation_mode
        )
        
        # Perform transfer based on type
        if ftype.lower() == "job":
            result = _global_manager.transfer_jobs(publish_list, options)
        elif ftype.lower() == "view":
            result = _global_manager.transfer_views(publish_list, options)
        else:
            raise ValidationError("ftype", ftype, "job or view")
        
        # Return success based on whether there were failures
        return not result.has_failures
        
    except Exception as e:
        if _global_manager.reporter:
            _global_manager.reporter.print_error("Transfer failed", str(e))
        return False


def check_publish_standards(
    publish_list: List[str], 
    ftype: str = "job", 
    allowDuplicates: bool = False, 
    mode: str = "console"
) -> bool:
    """
    Backward compatible function to check if jobs/views meet publishing standards.
    
    This checks if the items exist and validates them before transfer.
    """
    global _global_manager
    
    if _global_manager is None:
        raise JenkinsTransferError("No connection established. Call connect() first.")
    
    try:
        # For backward compatibility, we'll check if items exist and are valid
        if ftype.lower() == "job":
            # Check if jobs exist on interim server
            interim_jobs = _global_manager.get_job_list("interim")
            production_jobs = _global_manager.get_job_list("production")
            
            all_valid = True
            for job_name in publish_list:
                if job_name not in interim_jobs:
                    if mode == "console":
                        _global_manager.reporter.print_error(f"Job '{job_name}' not found on interim server")
                    all_valid = False
                elif job_name in production_jobs and not allowDuplicates:
                    if mode == "console":
                        _global_manager.reporter.print_warning(f"Job '{job_name}' already exists on production")
                    # This is a warning, not an error for standards check
            
            return all_valid
            
        elif ftype.lower() == "view":
            # Check if views exist on interim server
            interim_views = _global_manager.get_view_list("interim")
            production_views = _global_manager.get_view_list("production")
            
            all_valid = True
            for view_name in publish_list:
                if view_name not in interim_views:
                    if mode == "console":
                        _global_manager.reporter.print_error(f"View '{view_name}' not found on interim server")
                    all_valid = False
                elif view_name in production_views and not allowDuplicates:
                    if mode == "console":
                        _global_manager.reporter.print_warning(f"View '{view_name}' already exists on production")
                    # This is a warning, not an error for standards check
            
            return all_valid
            
        else:
            raise ValidationError("ftype", ftype, "job or view")
            
    except Exception as e:
        if _global_manager.reporter and mode == "console":
            _global_manager.reporter.print_error("Standards check failed", str(e))
        return False


def check_plugin_dependencies(
    publish_list: List[str], 
    ftype: str = "job", 
    mode: str = "console"
) -> Dict[str, List[str]]:
    """
    Backward compatible function to check plugin dependencies without installing.
    """
    global _global_manager
    
    if _global_manager is None:
        raise JenkinsTransferError("No connection established. Call connect() first.")
    
    try:
        if ftype.lower() == "job":
            return _global_manager.check_job_plugin_dependencies(publish_list)
        elif ftype.lower() == "view":
            # For views, we need to get all jobs in the views and check their dependencies
            all_job_plugins = {}
            for view_name in publish_list:
                try:
                    job_names = _global_manager.get_view_jobs(view_name, "interim")
                    job_plugins = _global_manager.check_job_plugin_dependencies(job_names)
                    all_job_plugins.update(job_plugins)
                except Exception as e:
                    if mode == "console":
                        _global_manager.reporter.print_error(f"Failed to check view '{view_name}'", str(e))
            
            return all_job_plugins
        else:
            raise ValidationError("ftype", ftype, "job or view")
            
    except Exception as e:
        if _global_manager.reporter and mode == "console":
            _global_manager.reporter.print_error("Plugin dependency check failed", str(e))
        return {}


def check_and_install_plugin_dependencies(
    publish_list: List[str], 
    ftype: str = "job", 
    mode: str = "console"
) -> bool:
    """
    Backward compatible function to check and install plugin dependencies.
    """
    global _global_manager
    
    if _global_manager is None:
        raise JenkinsTransferError("No connection established. Call connect() first.")
    
    try:
        operation_mode = OperationMode.CONSOLE if mode == "console" else OperationMode.QUIET
        options = TransferOptions(mode=operation_mode, install_missing_plugins=True)
        
        if ftype.lower() == "job":
            result = _global_manager.install_plugin_dependencies(publish_list, options)
            return not result.has_failures
        elif ftype.lower() == "view":
            # For views, get all jobs and install their dependencies
            all_jobs = []
            for view_name in publish_list:
                try:
                    job_names = _global_manager.get_view_jobs(view_name, "interim")
                    all_jobs.extend(job_names)
                except Exception as e:
                    if mode == "console":
                        _global_manager.reporter.print_error(f"Failed to process view '{view_name}'", str(e))
                    return False
            
            # Remove duplicates
            unique_jobs = list(set(all_jobs))
            result = _global_manager.install_plugin_dependencies(unique_jobs, options)
            return not result.has_failures
        else:
            raise ValidationError("ftype", ftype, "job or view")
            
    except Exception as e:
        if _global_manager.reporter and mode == "console":
            _global_manager.reporter.print_error("Plugin installation failed", str(e))
        return False


def production_cleanup(mode: str = 'console') -> bool:
    """
    Backward compatible function to clean up production server.
    """
    global _global_manager
    
    if _global_manager is None:
        raise JenkinsTransferError("No connection established. Call connect() first.")
    
    try:
        result = _global_manager.cleanup_production()
        return not result.has_failures
    except Exception as e:
        if _global_manager.reporter and mode == "console":
            _global_manager.reporter.print_error("Production cleanup failed", str(e))
        return False


def interim_cleanup(mode: str = 'console') -> bool:
    """
    Backward compatible function to clean up interim server.
    """
    global _global_manager
    
    if _global_manager is None:
        raise JenkinsTransferError("No connection established. Call connect() first.")
    
    try:
        result = _global_manager.cleanup_interim()
        return not result.has_failures
    except Exception as e:
        if _global_manager.reporter and mode == "console":
            _global_manager.reporter.print_error("Interim cleanup failed", str(e))
        return False


def set_console_size(width: int) -> None:
    """
    Backward compatible function to set console width.
    """
    global _global_manager
    
    try:
        if _global_manager is not None:
            _global_manager.app_config.console_width = width
            # Update the reporter with new width
            from ..ui import ConsoleReporter
            _global_manager.reporter = ConsoleReporter(_global_manager.app_config)
    except Exception as e:
        print(f"Error setting console size: {e}")


# Export the global manager for advanced users who need direct access
def get_manager() -> Optional[JenkinsTransferManager]:
    """
    Get the current global manager instance.
    
    Returns:
        Current JenkinsTransferManager instance or None if not connected
    """
    return _global_manager


def reset_manager() -> None:
    """
    Reset the global manager instance.
    
    Useful for testing or when you need to establish a new connection.
    """
    global _global_manager
    _global_manager = None