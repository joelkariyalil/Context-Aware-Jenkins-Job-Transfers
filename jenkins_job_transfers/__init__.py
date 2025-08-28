"""
Jenkins Job Transfers - Context Aware Jenkins Job Transfer Library

This library provides a pythonic way of transferring jobs between Jenkins servers
with their associated views and plugins, resulting in Context Aware Jenkins Job Transfers.

New API (Recommended):
    from jenkins_job_transfers import create_manager
    
    manager = create_manager(
        production_url="https://prod.jenkins.com",
        interim_url="https://interim.jenkins.com",
        production_username="prod_user",
        interim_username="interim_user", 
        production_password="prod_pass",
        interim_password="interim_pass"
    )
    
    result = manager.transfer_jobs(["job1", "job2"])

Legacy API (Backward Compatible):
    import jenkins_job_transfers as jjt
    
    jjt.connect(prod_url, interim_url, prod_user, interim_user, prod_pass, interim_pass)
    jjt.transfer(["job1", "job2"], ftype="job")
"""

# Import new API components
from .types import (
    JenkinsConfig, ApplicationConfig, TransferOptions, TransferResult,
    TransferType, OperationMode, JobInfo, ViewInfo, PluginInfo
)
from .core import JenkinsTransferManager
from .api import (
    create_manager, create_manager_from_configs,
    get_manager, reset_manager
)
from .types import (
    JenkinsTransferError, ConnectionError, AuthenticationError,
    JobNotFoundError, ViewNotFoundError, PluginMissingError,
    JobTransferError, ViewTransferError, ValidationError
)

# Import backward compatible functions
from .api import (
    connect, transfer, check_publish_standards,
    check_plugin_dependencies, check_and_install_plugin_dependencies,
    production_cleanup, interim_cleanup, set_console_size
)

# Version info
__version__ = "2.0.0"
__author__ = "Joel Thomas Chacko"
__email__ = "joeltc071@gmail.com"

# Expose main classes and functions for easy import
__all__ = [
    # New API (recommended)
    'JenkinsTransferManager',
    'create_manager', 
    'create_manager_from_configs',
    'get_manager',
    'reset_manager',
    
    # Configuration classes
    'JenkinsConfig',
    'ApplicationConfig', 
    'TransferOptions',
    
    # Result classes
    'TransferResult',
    'JobInfo',
    'ViewInfo', 
    'PluginInfo',
    
    # Enums
    'TransferType',
    'OperationMode',
    
    # Exceptions
    'JenkinsTransferError',
    'ConnectionError',
    'AuthenticationError', 
    'JobNotFoundError',
    'ViewNotFoundError',
    'PluginMissingError',
    'JobTransferError',
    'ViewTransferError',
    'ValidationError',
    
    # Backward compatible functions
    'connect',
    'transfer',
    'check_publish_standards',
    'check_plugin_dependencies', 
    'check_and_install_plugin_dependencies',
    'production_cleanup',
    'interim_cleanup',
    'set_console_size',
]

# All function implementations are now in new_api.py and imported above
# This maintains backward compatibility while using the new architecture