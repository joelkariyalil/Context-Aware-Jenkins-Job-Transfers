"""
Exception hierarchy for Jenkins Job Transfers

This module defines all custom exceptions used throughout the Jenkins Transfer system.
Each exception provides specific context about what went wrong and how to handle it.
"""

from typing import List, Optional


class JenkinsTransferError(Exception):
    """Base exception for all Jenkins Transfer operations."""
    
    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


class ConnectionError(JenkinsTransferError):
    """Raised when connection to Jenkins server fails."""
    
    def __init__(self, server_url: str, reason: Optional[str] = None):
        self.server_url = server_url
        message = f"Failed to connect to Jenkins server at {server_url}"
        super().__init__(message, reason)


class AuthenticationError(JenkinsTransferError):
    """Raised when Jenkins authentication fails."""
    
    def __init__(self, server_url: str, username: str):
        self.server_url = server_url
        self.username = username
        message = f"Authentication failed for user '{username}' on {server_url}"
        super().__init__(message)


class JobNotFoundError(JenkinsTransferError):
    """Raised when a requested job doesn't exist."""
    
    def __init__(self, job_name: str, server: str):
        self.job_name = job_name
        self.server = server
        message = f"Job '{job_name}' not found on {server} server"
        super().__init__(message)


class ViewNotFoundError(JenkinsTransferError):
    """Raised when a requested view doesn't exist."""
    
    def __init__(self, view_name: str, server: str):
        self.view_name = view_name
        self.server = server
        message = f"View '{view_name}' not found on {server} server"
        super().__init__(message)


class PluginMissingError(JenkinsTransferError):
    """Raised when required plugins are not available."""
    
    def __init__(self, missing_plugins: List[str], server: str):
        self.missing_plugins = missing_plugins
        self.server = server
        plugins_str = ", ".join(missing_plugins)
        message = f"Missing plugins on {server} server: {plugins_str}"
        super().__init__(message)


class PluginInstallationError(JenkinsTransferError):
    """Raised when plugin installation fails."""
    
    def __init__(self, plugin_name: str, server: str, reason: Optional[str] = None):
        self.plugin_name = plugin_name
        self.server = server
        message = f"Failed to install plugin '{plugin_name}' on {server} server"
        super().__init__(message, reason)


class JobTransferError(JenkinsTransferError):
    """Raised when job transfer operation fails."""
    
    def __init__(self, job_name: str, operation: str, reason: Optional[str] = None):
        self.job_name = job_name
        self.operation = operation
        message = f"Failed to {operation} job '{job_name}'"
        super().__init__(message, reason)


class ViewTransferError(JenkinsTransferError):
    """Raised when view transfer operation fails."""
    
    def __init__(self, view_name: str, operation: str, reason: Optional[str] = None):
        self.view_name = view_name
        self.operation = operation
        message = f"Failed to {operation} view '{view_name}'"
        super().__init__(message, reason)


class ValidationError(JenkinsTransferError):
    """Raised when input validation fails."""
    
    def __init__(self, field_name: str, value: str, expected: str):
        self.field_name = field_name
        self.value = value
        self.expected = expected
        message = f"Invalid {field_name}: '{value}'. Expected: {expected}"
        super().__init__(message)


class ConfigurationError(JenkinsTransferError):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, config_field: str, reason: str):
        self.config_field = config_field
        message = f"Configuration error in '{config_field}': {reason}"
        super().__init__(message)