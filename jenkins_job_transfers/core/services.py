"""
Core business logic services for Jenkins Job Transfers.

This module contains the main business logic separated from UI concerns.
All services are pure business logic with no side effects.
"""

from typing import List, Dict, Set, Optional
from lxml import etree
import logging

from ..types import (
    TransferResult, TransferOptions, JobInfo, ViewInfo, PluginInfo,
    Logger, JenkinsConfig, TransferType
)
from .jenkins_api import JenkinsConnection
from ..types import (
    JobNotFoundError, ViewNotFoundError, PluginMissingError,
    JobTransferError, ViewTransferError, PluginInstallationError
)


class PluginAnalyzer:
    """Analyzes plugin dependencies in Jenkins configurations."""
    
    def __init__(self, logger: Logger):
        """
        Initialize plugin analyzer.
        
        Args:
            logger: Logger instance
        """
        self.logger = logger
    
    def extract_plugins_from_job_config(self, config_xml: str) -> List[str]:
        """
        Extract plugin names from job configuration XML.
        
        Args:
            config_xml: Job configuration XML
            
        Returns:
            List of plugin names required by the job
        """
        try:
            plugin_names = []
            tree = etree.fromstring(config_xml.encode())
            
            # Find all elements with plugin attribute
            plugin_elements = tree.xpath('//*[@plugin]')
            
            for element in plugin_elements:
                plugin_attr = element.attrib.get('plugin', '')
                if plugin_attr:
                    # Extract plugin name (remove version info)
                    plugin_name = plugin_attr.split('@')[0]
                    if plugin_name and plugin_name not in plugin_names:
                        plugin_names.append(plugin_name)
            
            self.logger.debug(f"Extracted {len(plugin_names)} plugin dependencies from job config")
            return plugin_names
            
        except etree.XMLSyntaxError as e:
            self.logger.error(f"Error parsing job config XML: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error extracting plugins: {e}")
            return []
    
    def get_missing_plugins(
        self, 
        required_plugins: List[str], 
        available_plugins: List[str]
    ) -> List[str]:
        """
        Get list of plugins that are required but not available.
        
        Args:
            required_plugins: List of required plugin names
            available_plugins: List of available plugin names
            
        Returns:
            List of missing plugin names
        """
        required_set = set(required_plugins)
        available_set = set(available_plugins)
        missing = list(required_set - available_set)
        
        if missing:
            self.logger.info(f"Found {len(missing)} missing plugins: {missing}")
        else:
            self.logger.debug("No missing plugins found")
        
        return missing


class JobTransferService:
    """Service for transferring Jenkins jobs between servers."""
    
    def __init__(
        self, 
        production: JenkinsConnection, 
        interim: JenkinsConnection,
        plugin_analyzer: PluginAnalyzer,
        logger: Logger
    ):
        """
        Initialize job transfer service.
        
        Args:
            production: Production Jenkins connection
            interim: Interim Jenkins connection
            plugin_analyzer: Plugin analyzer service
            logger: Logger instance
        """
        self.production = production
        self.interim = interim
        self.plugin_analyzer = plugin_analyzer
        self.logger = logger
    
    def transfer_jobs(
        self, 
        job_names: List[str], 
        options: TransferOptions
    ) -> TransferResult:
        """
        Transfer jobs from interim to production server.
        
        Args:
            job_names: List of job names to transfer
            options: Transfer options
            
        Returns:
            TransferResult with details of the operation
        """
        result = TransferResult()
        
        self.logger.info(f"Starting job transfer for {len(job_names)} jobs")
        
        for job_name in job_names:
            try:
                self._transfer_single_job(job_name, options, result)
            except Exception as e:
                error_msg = f"Unexpected error transferring job {job_name}: {str(e)}"
                self.logger.error(error_msg)
                result.add_job_failure(job_name, error_msg)
        
        self.logger.info(
            f"Job transfer completed: {len(result.successful_jobs)} successful, "
            f"{len(result.failed_jobs)} failed"
        )
        
        return result
    
    def _transfer_single_job(
        self, 
        job_name: str, 
        options: TransferOptions, 
        result: TransferResult
    ) -> None:
        """Transfer a single job."""
        self.logger.info(f"Transferring job: {job_name}")
        
        try:
            # Check if job exists on interim server
            if not self.interim.job_exists(job_name):
                raise JobNotFoundError(job_name, "interim")
            
            # Get job configuration
            config_xml = self.interim.get_job_config(job_name)
            
            # Check plugin dependencies if requested
            if options.install_missing_plugins:
                self._ensure_job_plugins(job_name, config_xml, result)
            
            # Check if job already exists on production
            job_exists_on_production = self.production.job_exists(job_name)
            
            if job_exists_on_production and not options.allow_duplicates:
                result.add_warning(f"Job '{job_name}' already exists on production (skipped)")
                return
            
            # Transfer the job
            if job_exists_on_production:
                self.production.update_job(job_name, config_xml)
                self.logger.info(f"Updated existing job: {job_name}")
            else:
                self.production.create_job(job_name, config_xml)
                self.logger.info(f"Created new job: {job_name}")
            
            result.add_job_success(job_name)
            
        except JobNotFoundError as e:
            result.add_job_failure(job_name, str(e))
        except JobTransferError as e:
            result.add_job_failure(job_name, str(e))
    
    def _ensure_job_plugins(
        self, 
        job_name: str, 
        config_xml: str, 
        result: TransferResult
    ) -> None:
        """Ensure all required plugins are installed for a job."""
        try:
            # Extract required plugins from job config
            required_plugins = self.plugin_analyzer.extract_plugins_from_job_config(config_xml)
            
            if not required_plugins:
                return
            
            # Get available plugins on production
            available_plugins = self.production.get_plugin_names()
            
            # Find missing plugins
            missing_plugins = self.plugin_analyzer.get_missing_plugins(
                required_plugins, available_plugins
            )
            
            if not missing_plugins:
                return
            
            # Install missing plugins
            for plugin_name in missing_plugins:
                try:
                    success = self.production.install_plugin(plugin_name)
                    if success:
                        result.add_plugin_success(plugin_name)
                        self.logger.info(f"Initiated installation of plugin: {plugin_name}")
                    else:
                        result.add_plugin_failure(plugin_name, "Installation failed")
                except Exception as e:
                    result.add_plugin_failure(plugin_name, str(e))
            
            if missing_plugins:
                result.add_warning(
                    "Plugin installations initiated - Jenkins restart required to complete"
                )
                
        except Exception as e:
            self.logger.error(f"Error ensuring plugins for job {job_name}: {e}")
            result.add_warning(f"Could not verify plugins for job {job_name}: {str(e)}")
    
    def check_job_plugin_dependencies(self, job_names: List[str]) -> Dict[str, List[str]]:
        """
        Check plugin dependencies for jobs without installing anything.
        
        Args:
            job_names: List of job names to check
            
        Returns:
            Dictionary mapping job names to their missing plugins
        """
        job_plugins = {}
        available_plugins = self.production.get_plugin_names()
        
        for job_name in job_names:
            try:
                if not self.interim.job_exists(job_name):
                    self.logger.warning(f"Job {job_name} not found on interim server")
                    continue
                
                config_xml = self.interim.get_job_config(job_name)
                required_plugins = self.plugin_analyzer.extract_plugins_from_job_config(config_xml)
                missing_plugins = self.plugin_analyzer.get_missing_plugins(
                    required_plugins, available_plugins
                )
                
                if missing_plugins:
                    job_plugins[job_name] = missing_plugins
                    
            except Exception as e:
                self.logger.error(f"Error checking plugins for job {job_name}: {e}")
        
        return job_plugins


class ViewTransferService:
    """Service for transferring Jenkins views between servers."""
    
    def __init__(
        self, 
        production: JenkinsConnection, 
        interim: JenkinsConnection,
        job_service: JobTransferService,
        logger: Logger
    ):
        """
        Initialize view transfer service.
        
        Args:
            production: Production Jenkins connection
            interim: Interim Jenkins connection
            job_service: Job transfer service for transferring view jobs
            logger: Logger instance
        """
        self.production = production
        self.interim = interim
        self.job_service = job_service
        self.logger = logger
    
    def transfer_views(
        self, 
        view_names: List[str], 
        options: TransferOptions
    ) -> TransferResult:
        """
        Transfer views from interim to production server.
        
        Args:
            view_names: List of view names to transfer
            options: Transfer options
            
        Returns:
            TransferResult with details of the operation
        """
        result = TransferResult()
        
        self.logger.info(f"Starting view transfer for {len(view_names)} views")
        
        for view_name in view_names:
            try:
                self._transfer_single_view(view_name, options, result)
            except Exception as e:
                error_msg = f"Unexpected error transferring view {view_name}: {str(e)}"
                self.logger.error(error_msg)
                result.add_view_failure(view_name, error_msg)
        
        self.logger.info(
            f"View transfer completed: {len(result.successful_views)} successful, "
            f"{len(result.failed_views)} failed"
        )
        
        return result
    
    def _transfer_single_view(
        self, 
        view_name: str, 
        options: TransferOptions, 
        result: TransferResult
    ) -> None:
        """Transfer a single view and its associated jobs."""
        self.logger.info(f"Transferring view: {view_name}")
        
        try:
            # Check if view exists on interim server
            if not self.interim.view_exists(view_name):
                raise ViewNotFoundError(view_name, "interim")
            
            # Get view configuration and jobs
            config_xml = self.interim.get_view_config(view_name)
            job_names = self.interim.get_view_jobs(view_name)
            
            # First transfer all jobs in the view
            if job_names:
                self.logger.info(f"Transferring {len(job_names)} jobs for view {view_name}")
                job_result = self.job_service.transfer_jobs(job_names, options)
                
                # Merge job transfer results
                result.successful_jobs.extend(job_result.successful_jobs)
                result.failed_jobs.update(job_result.failed_jobs)
                result.installed_plugins.extend(job_result.installed_plugins)
                result.failed_plugins.update(job_result.failed_plugins)
                result.warnings.extend(job_result.warnings)
            
            # Check if view already exists on production
            view_exists_on_production = self.production.view_exists(view_name)
            
            if view_exists_on_production and not options.allow_duplicates:
                result.add_warning(f"View '{view_name}' already exists on production (skipped)")
                return
            
            # Transfer the view
            if view_exists_on_production:
                self.production.update_view(view_name, config_xml)
                self.logger.info(f"Updated existing view: {view_name}")
            else:
                self.production.create_view(view_name, config_xml)
                self.logger.info(f"Created new view: {view_name}")
            
            result.add_view_success(view_name)
            
        except ViewNotFoundError as e:
            result.add_view_failure(view_name, str(e))
        except ViewTransferError as e:
            result.add_view_failure(view_name, str(e))


class CleanupService:
    """Service for cleaning up Jenkins servers."""
    
    def __init__(self, connection: JenkinsConnection, logger: Logger):
        """
        Initialize cleanup service.
        
        Args:
            connection: Jenkins connection
            logger: Logger instance
        """
        self.connection = connection
        self.logger = logger
    
    def cleanup_empty_views(self) -> TransferResult:
        """
        Clean up views that have no associated jobs.
        
        Returns:
            TransferResult with cleanup details
        """
        result = TransferResult()
        
        try:
            self.logger.info("Starting cleanup of empty views")
            
            view_names = self.connection.get_view_names()
            
            for view_name in view_names:
                # Skip the default 'all' view
                if view_name.lower() == 'all':
                    continue
                
                try:
                    job_names = self.connection.get_view_jobs(view_name)
                    
                    if not job_names:
                        self.logger.info(f"Deleting empty view: {view_name}")
                        self.connection.delete_view(view_name)
                        result.add_view_success(view_name)
                    
                except Exception as e:
                    error_msg = f"Failed to cleanup view {view_name}: {str(e)}"
                    self.logger.error(error_msg)
                    result.add_view_failure(view_name, error_msg)
            
            self.logger.info(f"Cleanup completed: {len(result.successful_views)} views cleaned up")
            
        except Exception as e:
            error_msg = f"Cleanup operation failed: {str(e)}"
            self.logger.error(error_msg)
            result.add_warning(error_msg)
        
        return result