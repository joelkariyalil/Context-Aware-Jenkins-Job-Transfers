"""
Jenkins API wrapper with improved error handling and type safety.

This module provides a clean interface to Jenkins operations with proper
exception handling and logging.
"""

import jenkins
from typing import List, Dict, Optional
from lxml import etree

from ..types import JenkinsConfig, JobInfo, ViewInfo, PluginInfo, Logger
from ..types import (
    ConnectionError, AuthenticationError, JobNotFoundError, 
    ViewNotFoundError, JobTransferError, ViewTransferError
)


class JenkinsConnection:
    """
    Wrapper around jenkins.Jenkins with improved error handling and type safety.
    """
    
    def __init__(self, config: JenkinsConfig, logger: Logger):
        """
        Initialize Jenkins connection.
        
        Args:
            config: Jenkins server configuration
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self._jenkins: Optional[jenkins.Jenkins] = None
        self._connect()
    
    def _connect(self) -> None:
        """Establish connection to Jenkins server."""
        try:
            self.logger.info(
                "Connecting to Jenkins server", 
                extra={"url": self.config.url, "username": self.config.username}
            )
            
            self._jenkins = jenkins.Jenkins(
                self.config.url,
                username=self.config.username,
                password=self.config.password,
                timeout=self.config.timeout
            )
            
            # Test connection by getting server info
            self._jenkins.get_whoami()
            
            self.logger.info(
                "Successfully connected to Jenkins server",
                extra={"url": self.config.url}
            )
            
        except jenkins.JenkinsException as e:
            if "unauthorized" in str(e).lower() or "forbidden" in str(e).lower():
                raise AuthenticationError(self.config.url, self.config.username)
            raise ConnectionError(self.config.url, str(e))
        except Exception as e:
            raise ConnectionError(self.config.url, str(e))
    
    @property
    def jenkins(self) -> jenkins.Jenkins:
        """Get the underlying Jenkins client."""
        if self._jenkins is None:
            raise ConnectionError(self.config.url, "Not connected")
        return self._jenkins
    
    def get_jobs(self) -> List[Dict[str, str]]:
        """
        Get list of all jobs.
        
        Returns:
            List of job dictionaries with name and other info
        """
        try:
            self.logger.debug("Retrieving job list")
            jobs = self.jenkins.get_jobs()
            self.logger.info(f"Retrieved {len(jobs)} jobs")
            return jobs
        except jenkins.JenkinsException as e:
            self.logger.error(f"Failed to retrieve jobs: {e}")
            raise JobTransferError("unknown", "retrieve job list", str(e))
    
    def get_job_names(self) -> List[str]:
        """Get list of job names."""
        jobs = self.get_jobs()
        return [job['name'] for job in jobs]
    
    def get_job_config(self, job_name: str) -> str:
        """
        Get job configuration XML.
        
        Args:
            job_name: Name of the job
            
        Returns:
            Job configuration XML as string
            
        Raises:
            JobNotFoundError: If job doesn't exist
        """
        try:
            self.logger.debug(f"Retrieving config for job: {job_name}")
            config_xml = self.jenkins.get_job_config(job_name)
            self.logger.debug(f"Retrieved config for job: {job_name}")
            return config_xml
        except jenkins.NotFoundException:
            raise JobNotFoundError(job_name, self.config.url)
        except jenkins.JenkinsException as e:
            raise JobTransferError(job_name, "get config", str(e))
    
    def create_job(self, job_name: str, config_xml: str) -> None:
        """
        Create a new job.
        
        Args:
            job_name: Name of the job to create
            config_xml: Job configuration XML
            
        Raises:
            JobTransferError: If job creation fails
        """
        try:
            self.logger.info(f"Creating job: {job_name}")
            self.jenkins.create_job(job_name, config_xml)
            self.logger.info(f"Successfully created job: {job_name}")
        except jenkins.JenkinsException as e:
            self.logger.error(f"Failed to create job {job_name}: {e}")
            raise JobTransferError(job_name, "create", str(e))
    
    def update_job(self, job_name: str, config_xml: str) -> None:
        """
        Update an existing job.
        
        Args:
            job_name: Name of the job to update
            config_xml: New job configuration XML
            
        Raises:
            JobTransferError: If job update fails
        """
        try:
            self.logger.info(f"Updating job: {job_name}")
            self.jenkins.reconfig_job(job_name, config_xml)
            self.logger.info(f"Successfully updated job: {job_name}")
        except jenkins.NotFoundException:
            raise JobNotFoundError(job_name, self.config.url)
        except jenkins.JenkinsException as e:
            self.logger.error(f"Failed to update job {job_name}: {e}")
            raise JobTransferError(job_name, "update", str(e))
    
    def delete_job(self, job_name: str) -> None:
        """
        Delete a job.
        
        Args:
            job_name: Name of the job to delete
            
        Raises:
            JobTransferError: If job deletion fails
        """
        try:
            self.logger.info(f"Deleting job: {job_name}")
            self.jenkins.delete_job(job_name)
            self.logger.info(f"Successfully deleted job: {job_name}")
        except jenkins.NotFoundException:
            raise JobNotFoundError(job_name, self.config.url)
        except jenkins.JenkinsException as e:
            self.logger.error(f"Failed to delete job {job_name}: {e}")
            raise JobTransferError(job_name, "delete", str(e))
    
    def job_exists(self, job_name: str) -> bool:
        """
        Check if a job exists.
        
        Args:
            job_name: Name of the job to check
            
        Returns:
            True if job exists, False otherwise
        """
        try:
            self.jenkins.get_job_info(job_name)
            return True
        except jenkins.NotFoundException:
            return False
        except jenkins.JenkinsException:
            # If we can't determine, assume it doesn't exist
            return False
    
    def get_views(self) -> List[Dict[str, str]]:
        """
        Get list of all views.
        
        Returns:
            List of view dictionaries with name and other info
        """
        try:
            self.logger.debug("Retrieving view list")
            views = self.jenkins.get_views()
            self.logger.info(f"Retrieved {len(views)} views")
            return views
        except jenkins.JenkinsException as e:
            self.logger.error(f"Failed to retrieve views: {e}")
            raise ViewTransferError("unknown", "retrieve view list", str(e))
    
    def get_view_names(self) -> List[str]:
        """Get list of view names."""
        views = self.get_views()
        return [view['name'] for view in views]
    
    def get_view_config(self, view_name: str) -> str:
        """
        Get view configuration XML.
        
        Args:
            view_name: Name of the view
            
        Returns:
            View configuration XML as string
            
        Raises:
            ViewNotFoundError: If view doesn't exist
        """
        try:
            self.logger.debug(f"Retrieving config for view: {view_name}")
            config_xml = self.jenkins.get_view_config(view_name)
            self.logger.debug(f"Retrieved config for view: {view_name}")
            return config_xml
        except jenkins.NotFoundException:
            raise ViewNotFoundError(view_name, self.config.url)
        except jenkins.JenkinsException as e:
            raise ViewTransferError(view_name, "get config", str(e))
    
    def create_view(self, view_name: str, config_xml: str) -> None:
        """
        Create a new view.
        
        Args:
            view_name: Name of the view to create
            config_xml: View configuration XML
            
        Raises:
            ViewTransferError: If view creation fails
        """
        try:
            self.logger.info(f"Creating view: {view_name}")
            self.jenkins.create_view(view_name, config_xml)
            self.logger.info(f"Successfully created view: {view_name}")
        except jenkins.JenkinsException as e:
            self.logger.error(f"Failed to create view {view_name}: {e}")
            raise ViewTransferError(view_name, "create", str(e))
    
    def update_view(self, view_name: str, config_xml: str) -> None:
        """
        Update an existing view.
        
        Args:
            view_name: Name of the view to update
            config_xml: New view configuration XML
            
        Raises:
            ViewTransferError: If view update fails
        """
        try:
            self.logger.info(f"Updating view: {view_name}")
            self.jenkins.reconfig_view(view_name, config_xml)
            self.logger.info(f"Successfully updated view: {view_name}")
        except jenkins.NotFoundException:
            raise ViewNotFoundError(view_name, self.config.url)
        except jenkins.JenkinsException as e:
            self.logger.error(f"Failed to update view {view_name}: {e}")
            raise ViewTransferError(view_name, "update", str(e))
    
    def delete_view(self, view_name: str) -> None:
        """
        Delete a view.
        
        Args:
            view_name: Name of the view to delete
            
        Raises:
            ViewTransferError: If view deletion fails
        """
        try:
            self.logger.info(f"Deleting view: {view_name}")
            self.jenkins.delete_view(view_name)
            self.logger.info(f"Successfully deleted view: {view_name}")
        except jenkins.NotFoundException:
            raise ViewNotFoundError(view_name, self.config.url)
        except jenkins.JenkinsException as e:
            self.logger.error(f"Failed to delete view {view_name}: {e}")
            raise ViewTransferError(view_name, "delete", str(e))
    
    def view_exists(self, view_name: str) -> bool:
        """
        Check if a view exists.
        
        Args:
            view_name: Name of the view to check
            
        Returns:
            True if view exists, False otherwise
        """
        try:
            self.jenkins.get_view_info(view_name)
            return True
        except jenkins.NotFoundException:
            return False
        except jenkins.JenkinsException:
            # If we can't determine, assume it doesn't exist
            return False
    
    def get_view_jobs(self, view_name: str) -> List[str]:
        """
        Get list of jobs in a view.
        
        Args:
            view_name: Name of the view
            
        Returns:
            List of job names in the view
            
        Raises:
            ViewNotFoundError: If view doesn't exist
        """
        try:
            config_xml = self.get_view_config(view_name)
            root = etree.fromstring(config_xml.encode('utf-8'))
            job_names = root.xpath('//jobNames/string/text()')
            self.logger.debug(f"View {view_name} contains {len(job_names)} jobs")
            return job_names
        except ViewNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to parse jobs from view {view_name}: {e}")
            raise ViewTransferError(view_name, "get jobs", str(e))
    
    def get_plugins(self) -> List[PluginInfo]:
        """
        Get list of installed plugins.
        
        Returns:
            List of PluginInfo objects
        """
        try:
            self.logger.debug("Retrieving plugin list")
            plugins_info = self.jenkins.get_plugins_info()
            
            plugins = []
            for plugin_data in plugins_info:
                plugin = PluginInfo(
                    name=plugin_data.get('shortName', ''),
                    version=plugin_data.get('version', ''),
                    installed_on_production=False,  # Will be set by caller
                    installed_on_interim=False     # Will be set by caller
                )
                plugins.append(plugin)
            
            self.logger.info(f"Retrieved {len(plugins)} plugins")
            return plugins
            
        except jenkins.JenkinsException as e:
            self.logger.error(f"Failed to retrieve plugins: {e}")
            raise JobTransferError("unknown", "retrieve plugin list", str(e))
    
    def get_plugin_names(self) -> List[str]:
        """Get list of installed plugin names."""
        plugins = self.get_plugins()
        return [plugin.name for plugin in plugins]
    
    def install_plugin(self, plugin_name: str) -> bool:
        """
        Install a plugin.
        
        Args:
            plugin_name: Name of the plugin to install
            
        Returns:
            True if installation was initiated successfully
            
        Note:
            Plugin installation requires a Jenkins restart to complete.
        """
        try:
            self.logger.info(f"Installing plugin: {plugin_name}")
            result = self.jenkins.install_plugin(plugin_name)
            if result:
                self.logger.info(f"Plugin installation initiated: {plugin_name}")
            else:
                self.logger.warning(f"Plugin installation may have failed: {plugin_name}")
            return result
        except jenkins.JenkinsException as e:
            self.logger.error(f"Failed to install plugin {plugin_name}: {e}")
            return False