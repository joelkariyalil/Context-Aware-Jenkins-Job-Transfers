"""
Main Jenkins Transfer Manager with dependency injection.

This module provides the high-level interface for Jenkins transfer operations,
coordinating between all services while maintaining clean separation of concerns.
"""

import logging
from typing import List, Dict, Optional

from ..types import (
    JenkinsConfig, ApplicationConfig, TransferOptions, TransferResult,
    TransferType, OperationMode, Logger
)
from .jenkins_api import JenkinsConnection
from .services import JobTransferService, ViewTransferService, CleanupService, PluginAnalyzer
from ..ui import ConsoleReporter
from ..validation import InputValidator, ConfigValidator
from ..types import (
    ConnectionError, ValidationError, JenkinsTransferError
)


class JenkinsTransferManager:
    """
    Main coordinator for Jenkins transfer operations.
    
    This class provides the high-level interface for all Jenkins transfer
    operations while maintaining clean separation between business logic,
    UI concerns, and configuration management.
    """
    
    def __init__(
        self,
        production_config: JenkinsConfig,
        interim_config: JenkinsConfig,
        app_config: Optional[ApplicationConfig] = None,
        logger: Optional[Logger] = None
    ):
        """
        Initialize Jenkins Transfer Manager.
        
        Args:
            production_config: Production Jenkins configuration
            interim_config: Interim Jenkins configuration  
            app_config: Application configuration (optional)
            logger: Logger instance (optional, will create default if not provided)
        """
        # Store configurations
        self.production_config = production_config
        self.interim_config = interim_config
        self.app_config = app_config or ApplicationConfig()
        
        # Setup logger
        self.logger = logger or self._create_default_logger()
        
        # Validate configurations
        self._validate_configurations()
        
        # Initialize services
        self._initialize_services()
        
        # Initialize UI components
        self.reporter = ConsoleReporter(self.app_config)
        
        self.logger.info("JenkinsTransferManager initialized successfully")
    
    def _create_default_logger(self) -> Logger:
        """Create a default logger if none provided."""
        logger = logging.getLogger('jenkins_transfer')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(getattr(logging, self.app_config.log_level))
        return logger
    
    def _validate_configurations(self) -> None:
        """Validate all configurations."""
        # Validate production config
        prod_validation = ConfigValidator.validate_jenkins_config(self.production_config)
        if not prod_validation.is_valid:
            raise ValidationError("production_config", "configuration", 
                                f"Invalid configuration: {'; '.join(prod_validation.errors)}")
        
        # Validate interim config
        interim_validation = ConfigValidator.validate_jenkins_config(self.interim_config)
        if not interim_validation.is_valid:
            raise ValidationError("interim_config", "configuration",
                                f"Invalid configuration: {'; '.join(interim_validation.errors)}")
        
        # Show any warnings
        if prod_validation.warnings or interim_validation.warnings:
            all_warnings = prod_validation.warnings + interim_validation.warnings
            for warning in all_warnings:
                self.logger.warning(f"Configuration warning: {warning}")
    
    def _initialize_services(self) -> None:
        """Initialize all service dependencies."""
        try:
            # Create Jenkins connections
            self.production = JenkinsConnection(self.production_config, self.logger)
            self.interim = JenkinsConnection(self.interim_config, self.logger)
            
            # Initialize analyzer and services
            self.plugin_analyzer = PluginAnalyzer(self.logger)
            
            self.job_service = JobTransferService(
                self.production, self.interim, self.plugin_analyzer, self.logger
            )
            
            self.view_service = ViewTransferService(
                self.production, self.interim, self.job_service, self.logger
            )
            
            self.production_cleanup = CleanupService(self.production, self.logger)
            self.interim_cleanup = CleanupService(self.interim, self.logger)
            
        except Exception as e:
            error_msg = f"Failed to initialize services: {str(e)}"
            self.logger.error(error_msg)
            raise ConnectionError("initialization", error_msg)
    
    def connect(self) -> bool:
        """
        Test connections to both Jenkins servers.
        
        Returns:
            True if both connections are successful, False otherwise
        """
        try:
            self.logger.info("Testing connections to Jenkins servers")
            
            # Test production connection
            prod_jobs = self.production.get_jobs()
            self.logger.info(f"Production server accessible ({len(prod_jobs)} jobs)")
            
            # Test interim connection  
            interim_jobs = self.interim.get_jobs()
            self.logger.info(f"Interim server accessible ({len(interim_jobs)} jobs)")
            
            # Show connection status
            self.reporter.show_connection_status(
                self.production_config, 
                self.interim_config, 
                success=True
            )
            
            return True
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Connection test failed: {error_msg}")
            
            self.reporter.show_connection_status(
                self.production_config, 
                self.interim_config, 
                success=False,
                error_message=error_msg
            )
            
            return False
    
    def transfer_jobs(
        self, 
        job_names: List[str], 
        options: Optional[TransferOptions] = None
    ) -> TransferResult:
        """
        Transfer jobs from interim to production server.
        
        Args:
            job_names: List of job names to transfer
            options: Transfer options (optional, will use defaults)
            
        Returns:
            TransferResult with operation details
            
        Raises:
            ValidationError: If input validation fails
        """
        # Validate inputs
        validated_jobs = InputValidator.validate_job_list(job_names)
        transfer_options = options or TransferOptions()
        
        # Validate options
        options_validation = ConfigValidator.validate_transfer_options(transfer_options)
        if not options_validation.is_valid:
            raise ValidationError("transfer_options", "options",
                                f"Invalid options: {'; '.join(options_validation.errors)}")
        
        # Show any validation warnings
        if options_validation.warnings:
            self.reporter.show_validation_results(options_validation, "Transfer Options")
        
        self.logger.info(f"Starting job transfer for {len(validated_jobs)} jobs")
        
        # Show progress start
        self.reporter.show_progress_start("Job Transfer", len(validated_jobs))
        
        # Perform transfer
        result = self.job_service.transfer_jobs(validated_jobs, transfer_options)
        
        # Show results
        self.reporter.show_transfer_summary(result)
        
        return result
    
    def transfer_views(
        self, 
        view_names: List[str], 
        options: Optional[TransferOptions] = None
    ) -> TransferResult:
        """
        Transfer views from interim to production server.
        
        Args:
            view_names: List of view names to transfer
            options: Transfer options (optional, will use defaults)
            
        Returns:
            TransferResult with operation details
            
        Raises:
            ValidationError: If input validation fails
        """
        # Validate inputs
        validated_views = InputValidator.validate_view_list(view_names)
        transfer_options = options or TransferOptions()
        
        # Validate options
        options_validation = ConfigValidator.validate_transfer_options(transfer_options)
        if not options_validation.is_valid:
            raise ValidationError("transfer_options", "options",
                                f"Invalid options: {'; '.join(options_validation.errors)}")
        
        self.logger.info(f"Starting view transfer for {len(validated_views)} views")
        
        # Show progress start
        self.reporter.show_progress_start("View Transfer", len(validated_views))
        
        # Perform transfer
        result = self.view_service.transfer_views(validated_views, transfer_options)
        
        # Show results
        self.reporter.show_transfer_summary(result)
        
        return result
    
    def check_job_plugin_dependencies(self, job_names: List[str]) -> Dict[str, List[str]]:
        """
        Check plugin dependencies for jobs without installing them.
        
        Args:
            job_names: List of job names to check
            
        Returns:
            Dictionary mapping job names to their missing plugins
            
        Raises:
            ValidationError: If input validation fails
        """
        # Validate inputs
        validated_jobs = InputValidator.validate_job_list(job_names)
        
        self.logger.info(f"Checking plugin dependencies for {len(validated_jobs)} jobs")
        
        # Check dependencies
        job_plugins = self.job_service.check_job_plugin_dependencies(validated_jobs)
        
        # Show results
        for job_name, missing_plugins in job_plugins.items():
            self.reporter.show_plugin_dependencies(job_name, missing_plugins)
        
        if not job_plugins:
            self.reporter.print_info("All jobs have their plugin dependencies satisfied")
        
        return job_plugins
    
    def install_plugin_dependencies(
        self, 
        job_names: List[str], 
        options: Optional[TransferOptions] = None
    ) -> TransferResult:
        """
        Check and install plugin dependencies for jobs.
        
        Args:
            job_names: List of job names to check and install plugins for
            options: Transfer options (optional)
            
        Returns:
            TransferResult with plugin installation details
        """
        # Validate inputs
        validated_jobs = InputValidator.validate_job_list(job_names)
        transfer_options = options or TransferOptions(install_missing_plugins=True)
        
        self.logger.info(f"Installing plugin dependencies for {len(validated_jobs)} jobs")
        
        # This will check and install plugins as part of the transfer process
        # but we'll set allow_duplicates=True to avoid skipping existing jobs
        temp_options = TransferOptions(
            allow_duplicates=True,
            install_missing_plugins=True,
            mode=transfer_options.mode
        )
        
        # We create a dry-run style result by checking plugins without actual job transfer
        result = TransferResult()
        
        for job_name in validated_jobs:
            try:
                if not self.interim.job_exists(job_name):
                    result.add_job_failure(job_name, "Job not found on interim server")
                    continue
                
                config_xml = self.interim.get_job_config(job_name)
                
                # Extract and install plugins
                required_plugins = self.plugin_analyzer.extract_plugins_from_job_config(config_xml)
                available_plugins = self.production.get_plugin_names()
                missing_plugins = self.plugin_analyzer.get_missing_plugins(required_plugins, available_plugins)
                
                for plugin_name in missing_plugins:
                    try:
                        success = self.production.install_plugin(plugin_name)
                        if success:
                            result.add_plugin_success(plugin_name)
                        else:
                            result.add_plugin_failure(plugin_name, "Installation failed")
                    except Exception as e:
                        result.add_plugin_failure(plugin_name, str(e))
                
                result.add_job_success(job_name)
                
            except Exception as e:
                result.add_job_failure(job_name, str(e))
        
        # Show results
        self.reporter.show_transfer_summary(result)
        
        return result
    
    def cleanup_production(self) -> TransferResult:
        """
        Clean up production server by removing empty views.
        
        Returns:
            TransferResult with cleanup details
        """
        self.logger.info("Starting production server cleanup")
        
        result = self.production_cleanup.cleanup_empty_views()
        
        # Show results
        cleaned_views = result.successful_views
        errors = [f"{view}: {error}" for view, error in result.failed_views.items()]
        
        self.reporter.show_cleanup_results("production", cleaned_views, errors)
        
        return result
    
    def cleanup_interim(self) -> TransferResult:
        """
        Clean up interim server by removing empty views.
        
        Returns:
            TransferResult with cleanup details
        """
        self.logger.info("Starting interim server cleanup")
        
        result = self.interim_cleanup.cleanup_empty_views()
        
        # Show results
        cleaned_views = result.successful_views  
        errors = [f"{view}: {error}" for view, error in result.failed_views.items()]
        
        self.reporter.show_cleanup_results("interim", cleaned_views, errors)
        
        return result
    
    def get_job_list(self, server: str = "interim") -> List[str]:
        """
        Get list of jobs from specified server.
        
        Args:
            server: Server to query ("production" or "interim")
            
        Returns:
            List of job names
        """
        if server.lower() == "production":
            return self.production.get_job_names()
        elif server.lower() == "interim":
            return self.interim.get_job_names()
        else:
            raise ValidationError("server", server, "production or interim")
    
    def get_view_list(self, server: str = "interim") -> List[str]:
        """
        Get list of views from specified server.
        
        Args:
            server: Server to query ("production" or "interim")
            
        Returns:
            List of view names
        """
        if server.lower() == "production":
            return self.production.get_view_names()
        elif server.lower() == "interim":
            return self.interim.get_view_names()
        else:
            raise ValidationError("server", server, "production or interim")
    
    def get_view_jobs(self, view_name: str, server: str = "interim") -> List[str]:
        """
        Get list of jobs in a view.
        
        Args:
            view_name: Name of the view
            server: Server to query ("production" or "interim")
            
        Returns:
            List of job names in the view
        """
        view_name = InputValidator.validate_view_list([view_name])[0]
        
        if server.lower() == "production":
            return self.production.get_view_jobs(view_name)
        elif server.lower() == "interim":
            return self.interim.get_view_jobs(view_name)
        else:
            raise ValidationError("server", server, "production or interim")