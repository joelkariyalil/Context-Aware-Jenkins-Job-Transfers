"""
Type definitions and data structures for Jenkins Job Transfers.
"""

from .types import (
    JenkinsConfig, ApplicationConfig, TransferOptions, TransferResult,
    TransferType, OperationMode, JobInfo, ViewInfo, PluginInfo,
    Logger, JenkinsAPI, ValidationResult
)

from .exceptions import (
    JenkinsTransferError, ConnectionError, AuthenticationError,
    JobNotFoundError, ViewNotFoundError, PluginMissingError,
    PluginInstallationError, JobTransferError, ViewTransferError,
    ValidationError, ConfigurationError
)

__all__ = [
    # Data classes and configurations
    'JenkinsConfig',
    'ApplicationConfig', 
    'TransferOptions',
    'TransferResult',
    'JobInfo',
    'ViewInfo',
    'PluginInfo',
    'ValidationResult',
    
    # Enums
    'TransferType',
    'OperationMode',
    
    # Protocols
    'Logger',
    'JenkinsAPI',
    
    # Exceptions
    'JenkinsTransferError',
    'ConnectionError',
    'AuthenticationError',
    'JobNotFoundError',
    'ViewNotFoundError',
    'PluginMissingError',
    'PluginInstallationError',
    'JobTransferError',
    'ViewTransferError',
    'ValidationError',
    'ConfigurationError',
]

