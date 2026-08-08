"""
Input validation utilities for Jenkins Job Transfers

This module provides validation functions for all user inputs and configurations
to ensure data integrity and provide clear error messages.
"""

import re
from typing import List, Union
from urllib.parse import urlparse

from ..types import JenkinsConfig, TransferOptions, ValidationResult, TransferType, OperationMode
from ..types import ValidationError


class InputValidator:
    """Utility class for validating various types of input."""
    
    # Valid Jenkins job name pattern (allows letters, numbers, dots, hyphens, underscores)
    JOB_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9._-]+$')
    
    # Valid Jenkins view name pattern
    VIEW_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9._\s-]+$')
    
    @classmethod
    def validate_job_list(cls, job_list: Union[List[str], str]) -> List[str]:
        """
        Validate and sanitize a list of job names.
        
        Args:
            job_list: List of job names or single job name
            
        Returns:
            List of validated job names
            
        Raises:
            ValidationError: If validation fails
        """
        # Handle single job name
        if isinstance(job_list, str):
            job_list = [job_list]
        
        if not isinstance(job_list, list):
            raise ValidationError("job_list", str(type(job_list)), "list of strings")
        
        if not job_list:
            raise ValidationError("job_list", "empty list", "non-empty list")
        
        validated_jobs = []
        for i, job_name in enumerate(job_list):
            if not isinstance(job_name, str):
                raise ValidationError(
                    f"job_list[{i}]", 
                    str(type(job_name)), 
                    "string"
                )
            
            sanitized = job_name.strip()
            if not sanitized:
                raise ValidationError(
                    f"job_list[{i}]", 
                    "empty or whitespace", 
                    "non-empty string"
                )
            
            if not cls.JOB_NAME_PATTERN.match(sanitized):
                raise ValidationError(
                    f"job_list[{i}]", 
                    sanitized, 
                    "alphanumeric characters, dots, hyphens, underscores only"
                )
            
            validated_jobs.append(sanitized)
        
        return validated_jobs
    
    @classmethod
    def validate_view_list(cls, view_list: Union[List[str], str]) -> List[str]:
        """
        Validate and sanitize a list of view names.
        
        Args:
            view_list: List of view names or single view name
            
        Returns:
            List of validated view names
            
        Raises:
            ValidationError: If validation fails
        """
        # Handle single view name
        if isinstance(view_list, str):
            view_list = [view_list]
        
        if not isinstance(view_list, list):
            raise ValidationError("view_list", str(type(view_list)), "list of strings")
        
        if not view_list:
            raise ValidationError("view_list", "empty list", "non-empty list")
        
        validated_views = []
        for i, view_name in enumerate(view_list):
            if not isinstance(view_name, str):
                raise ValidationError(
                    f"view_list[{i}]", 
                    str(type(view_name)), 
                    "string"
                )
            
            sanitized = view_name.strip()
            if not sanitized:
                raise ValidationError(
                    f"view_list[{i}]", 
                    "empty or whitespace", 
                    "non-empty string"
                )
            
            if not cls.VIEW_NAME_PATTERN.match(sanitized):
                raise ValidationError(
                    f"view_list[{i}]", 
                    sanitized, 
                    "alphanumeric characters, dots, spaces, hyphens, underscores only"
                )
            
            validated_views.append(sanitized)
        
        return validated_views
    
    @classmethod
    def validate_jenkins_url(cls, url: str) -> str:
        """
        Validate and normalize a Jenkins URL.
        
        Args:
            url: Jenkins server URL
            
        Returns:
            Normalized URL
            
        Raises:
            ValidationError: If URL is invalid
        """
        if not isinstance(url, str):
            raise ValidationError("url", str(type(url)), "string")
        
        url = url.strip()
        if not url:
            raise ValidationError("url", "empty", "valid URL")
        
        if not url.startswith(('http://', 'https://')):
            raise ValidationError("url", url, "URL starting with http:// or https://")
        
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                raise ValidationError("url", url, "valid URL with hostname")
        except Exception as e:
            raise ValidationError("url", url, f"valid URL ({str(e)})")
        
        # Normalize by removing trailing slash
        return url.rstrip('/')
    
    @classmethod
    def validate_credentials(cls, username: str, password: str) -> tuple[str, str]:
        """
        Validate Jenkins credentials.
        
        Args:
            username: Jenkins username
            password: Jenkins password
            
        Returns:
            Tuple of (username, password)
            
        Raises:
            ValidationError: If credentials are invalid
        """
        if not isinstance(username, str) or not username.strip():
            raise ValidationError("username", username, "non-empty string")
        
        if not isinstance(password, str) or not password:
            raise ValidationError("password", "[hidden]", "non-empty string")
        
        return username.strip(), password
    
    @classmethod
    def validate_transfer_type(cls, transfer_type: Union[str, TransferType]) -> TransferType:
        """
        Validate transfer type.
        
        Args:
            transfer_type: Type of transfer (job or view)
            
        Returns:
            Validated TransferType enum
            
        Raises:
            ValidationError: If type is invalid
        """
        if isinstance(transfer_type, TransferType):
            return transfer_type
        
        if not isinstance(transfer_type, str):
            raise ValidationError("transfer_type", str(type(transfer_type)), "string")
        
        transfer_type = transfer_type.lower().strip()
        
        try:
            return TransferType(transfer_type)
        except ValueError:
            valid_types = [t.value for t in TransferType]
            raise ValidationError("transfer_type", transfer_type, f"one of {valid_types}")
    
    @classmethod
    def validate_operation_mode(cls, mode: Union[str, OperationMode]) -> OperationMode:
        """
        Validate operation mode.
        
        Args:
            mode: Operation mode (console or quiet)
            
        Returns:
            Validated OperationMode enum
            
        Raises:
            ValidationError: If mode is invalid
        """
        if isinstance(mode, OperationMode):
            return mode
        
        if not isinstance(mode, str):
            raise ValidationError("mode", str(type(mode)), "string")
        
        mode = mode.lower().strip()
        
        try:
            return OperationMode(mode)
        except ValueError:
            valid_modes = [m.value for m in OperationMode]
            raise ValidationError("mode", mode, f"one of {valid_modes}")


class ConfigValidator:
    """Validator for configuration objects."""
    
    @classmethod
    def validate_jenkins_config(cls, config: JenkinsConfig) -> ValidationResult:
        """
        Validate Jenkins configuration.
        
        Args:
            config: Jenkins configuration to validate
            
        Returns:
            ValidationResult with any errors or warnings
        """
        result = ValidationResult(is_valid=True)
        
        try:
            # URL validation
            InputValidator.validate_jenkins_url(config.url)
        except ValidationError as e:
            result.add_error(f"Invalid URL: {e.message}")
        
        try:
            # Credentials validation
            InputValidator.validate_credentials(config.username, config.password)
        except ValidationError as e:
            result.add_error(f"Invalid credentials: {e.message}")
        
        # Timeout validation
        if config.timeout <= 0:
            result.add_error("Timeout must be positive")
        elif config.timeout < 10:
            result.add_warning("Timeout is very low, may cause connection issues")
        
        return result
    
    @classmethod
    def validate_transfer_options(cls, options: TransferOptions) -> ValidationResult:
        """
        Validate transfer options.
        
        Args:
            options: Transfer options to validate
            
        Returns:
            ValidationResult with any errors or warnings
        """
        result = ValidationResult(is_valid=True)
        
        if options.retry_count < 0:
            result.add_error("Retry count must be non-negative")
        elif options.retry_count > 10:
            result.add_warning("High retry count may cause long delays")
        
        if options.timeout_seconds <= 0:
            result.add_error("Timeout must be positive")
        elif options.timeout_seconds < 5:
            result.add_warning("Very low timeout may cause failures")
        
        return result


class BatchValidator:
    """Validator for batch operations."""
    
    @classmethod
    def validate_transfer_batch(
        cls, 
        jobs: List[str], 
        views: List[str], 
        transfer_type: TransferType
    ) -> ValidationResult:
        """
        Validate a batch transfer operation.
        
        Args:
            jobs: List of job names
            views: List of view names
            transfer_type: Type of transfer
            
        Returns:
            ValidationResult with any errors or warnings
        """
        result = ValidationResult(is_valid=True)
        
        # Check that we have something to transfer
        if transfer_type == TransferType.JOB and not jobs:
            result.add_error("No jobs specified for job transfer")
        
        if transfer_type == TransferType.VIEW and not views:
            result.add_error("No views specified for view transfer")
        
        # Validate individual items
        if jobs:
            try:
                InputValidator.validate_job_list(jobs)
            except ValidationError as e:
                result.add_error(f"Job validation failed: {e.message}")
        
        if views:
            try:
                InputValidator.validate_view_list(views)
            except ValidationError as e:
                result.add_error(f"View validation failed: {e.message}")
        
        # Check for reasonable batch sizes
        total_items = len(jobs) + len(views)
        if total_items > 100:
            result.add_warning(f"Large batch size ({total_items} items) may take a long time")
        
        return result