"""
Type definitions and data classes for Jenkins Job Transfers

This module contains all the data structures and type hints used throughout
the Jenkins Transfer system.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union, Protocol
from enum import Enum


class TransferType(Enum):
    """Types of items that can be transferred."""
    JOB = "job"
    VIEW = "view"


class OperationMode(Enum):
    """Output modes for operations."""
    CONSOLE = "console"
    QUIET = "quiet"


class ServerType(Enum):
    """Types of Jenkins servers."""
    PRODUCTION = "production"
    INTERIM = "interim"


@dataclass
class JenkinsConfig:
    """Configuration for a Jenkins server connection."""
    url: str
    username: str
    password: str
    timeout: int = 30
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.url:
            raise ValueError("Jenkins URL cannot be empty")
        if not self.url.startswith(('http://', 'https://')):
            raise ValueError("Jenkins URL must start with http:// or https://")
        if not self.username:
            raise ValueError("Username cannot be empty")
        if not self.password:
            raise ValueError("Password cannot be empty")
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")
        
        # Normalize URL by removing trailing slash
        self.url = self.url.rstrip('/')


@dataclass
class TransferOptions:
    """Options for transfer operations."""
    allow_duplicates: bool = False
    mode: OperationMode = OperationMode.CONSOLE
    retry_count: int = 3
    timeout_seconds: int = 30
    install_missing_plugins: bool = True
    
    def __post_init__(self):
        """Validate options after initialization."""
        if self.retry_count < 0:
            raise ValueError("Retry count must be non-negative")
        if self.timeout_seconds <= 0:
            raise ValueError("Timeout must be positive")


@dataclass
class ApplicationConfig:
    """Global application configuration."""
    console_width: int = 149
    default_mode: OperationMode = OperationMode.CONSOLE
    max_retry_attempts: int = 3
    log_level: str = "INFO"
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.console_width <= 0:
            raise ValueError("Console width must be positive")
        if self.max_retry_attempts < 0:
            raise ValueError("Max retry attempts must be non-negative")
        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError("Invalid log level")


@dataclass
class JobInfo:
    """Information about a Jenkins job."""
    name: str
    config_xml: Optional[str] = None
    required_plugins: List[str] = field(default_factory=list)
    exists_on_production: bool = False
    exists_on_interim: bool = False


@dataclass
class ViewInfo:
    """Information about a Jenkins view."""
    name: str
    config_xml: Optional[str] = None
    job_names: List[str] = field(default_factory=list)
    exists_on_production: bool = False
    exists_on_interim: bool = False


@dataclass
class PluginInfo:
    """Information about a Jenkins plugin."""
    name: str
    version: Optional[str] = None
    installed_on_production: bool = False
    installed_on_interim: bool = False


@dataclass
class TransferResult:
    """Result of a transfer operation."""
    successful_jobs: List[str] = field(default_factory=list)
    failed_jobs: Dict[str, str] = field(default_factory=dict)  # job_name -> error_message
    successful_views: List[str] = field(default_factory=list)
    failed_views: Dict[str, str] = field(default_factory=dict)  # view_name -> error_message
    installed_plugins: List[str] = field(default_factory=list)
    failed_plugins: Dict[str, str] = field(default_factory=dict)  # plugin_name -> error_message
    warnings: List[str] = field(default_factory=list)
    
    @property
    def total_items(self) -> int:
        """Total number of items processed."""
        return (len(self.successful_jobs) + len(self.failed_jobs) + 
                len(self.successful_views) + len(self.failed_views))
    
    @property
    def success_rate(self) -> float:
        """Success rate as a percentage."""
        if self.total_items == 0:
            return 100.0
        successful = len(self.successful_jobs) + len(self.successful_views)
        return (successful / self.total_items) * 100.0
    
    @property
    def has_failures(self) -> bool:
        """True if any operations failed."""
        return len(self.failed_jobs) > 0 or len(self.failed_views) > 0
    
    def add_job_success(self, job_name: str) -> None:
        """Add a successful job transfer."""
        self.successful_jobs.append(job_name)
    
    def add_job_failure(self, job_name: str, error: str) -> None:
        """Add a failed job transfer."""
        self.failed_jobs[job_name] = error
    
    def add_view_success(self, view_name: str) -> None:
        """Add a successful view transfer."""
        self.successful_views.append(view_name)
    
    def add_view_failure(self, view_name: str, error: str) -> None:
        """Add a failed view transfer."""
        self.failed_views[view_name] = error
    
    def add_plugin_success(self, plugin_name: str) -> None:
        """Add a successful plugin installation."""
        self.installed_plugins.append(plugin_name)
    
    def add_plugin_failure(self, plugin_name: str, error: str) -> None:
        """Add a failed plugin installation."""
        self.failed_plugins[plugin_name] = error
    
    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)


class Logger(Protocol):
    """Protocol for logger objects."""
    
    def debug(self, msg: str, **kwargs) -> None:
        """Log debug message."""
        ...
    
    def info(self, msg: str, **kwargs) -> None:
        """Log info message."""
        ...
    
    def warning(self, msg: str, **kwargs) -> None:
        """Log warning message."""
        ...
    
    def error(self, msg: str, **kwargs) -> None:
        """Log error message."""
        ...
    
    def critical(self, msg: str, **kwargs) -> None:
        """Log critical message."""
        ...


class JenkinsAPI(Protocol):
    """Protocol for Jenkins API implementations."""
    
    def get_jobs(self) -> List[Dict[str, str]]:
        """Get list of jobs."""
        ...
    
    def get_views(self) -> List[Dict[str, str]]:
        """Get list of views."""
        ...
    
    def get_job_config(self, job_name: str) -> str:
        """Get job configuration XML."""
        ...
    
    def create_job(self, job_name: str, config_xml: str) -> None:
        """Create a new job."""
        ...
    
    def get_plugins_info(self) -> List[Dict[str, str]]:
        """Get list of installed plugins."""
        ...


@dataclass
class ValidationResult:
    """Result of validation operations."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def add_error(self, error: str) -> None:
        """Add validation error."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str) -> None:
        """Add validation warning."""
        self.warnings.append(warning)