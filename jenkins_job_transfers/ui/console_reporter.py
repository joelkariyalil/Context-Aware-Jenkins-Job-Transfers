"""
Console reporting and UI functionality for Jenkins Job Transfers.

This module handles all console output, table formatting, and user interaction,
completely separated from business logic.
"""

from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TaskID
from rich.panel import Panel
from rich.text import Text

from ..types import (
    TransferResult, JenkinsConfig, ApplicationConfig, 
    OperationMode, ValidationResult
)


class ConsoleReporter:
    """
    Handles all console output and user interaction for Jenkins transfers.
    """
    
    def __init__(self, config: ApplicationConfig):
        """
        Initialize console reporter.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.console = Console()
        self._current_table: Optional[Table] = None
    
    def _create_table(self, title: str, width: Optional[int] = None) -> Table:
        """
        Create a formatted table for output.
        
        Args:
            title: Table title
            width: Table width (defaults to config width)
            
        Returns:
            Configured Table object
        """
        table_width = width or self.config.console_width
        table = Table(
            title=title,
            show_lines=True, 
            width=table_width,
            title_style="bold blue"
        )
        return table
    
    def show_connection_status(
        self, 
        production_config: JenkinsConfig, 
        interim_config: JenkinsConfig,
        success: bool,
        error_message: Optional[str] = None
    ) -> None:
        """
        Display connection status for both servers.
        
        Args:
            production_config: Production server configuration
            interim_config: Interim server configuration
            success: Whether connection was successful
            error_message: Error message if connection failed
        """
        if self.config.default_mode == OperationMode.QUIET:
            return
        
        table = self._create_table("Jenkins Connection Status")
        table.add_column("Server", style="cyan", no_wrap=True)
        table.add_column("URL", style="white")
        table.add_column("Status", style="green" if success else "red")
        
        status_text = "✓ Connected" if success else "✗ Failed"
        
        table.add_row("Production", production_config.url, status_text)
        table.add_row("Interim", interim_config.url, status_text)
        
        if not success and error_message:
            table.add_row("Error", error_message, "")
        
        self.console.print(table)
    
    def show_transfer_summary(self, result: TransferResult) -> None:
        """
        Display transfer operation summary.
        
        Args:
            result: Transfer operation result
        """
        if self.config.default_mode == OperationMode.QUIET:
            return
        
        # Summary panel
        summary_text = Text()
        summary_text.append(f"Total Items: {result.total_items}\n")
        summary_text.append(f"Success Rate: {result.success_rate:.1f}%\n", style="green")
        
        if result.successful_jobs:
            summary_text.append(f"Jobs Transferred: {len(result.successful_jobs)}\n", style="green")
        if result.successful_views:
            summary_text.append(f"Views Transferred: {len(result.successful_views)}\n", style="green")
        if result.installed_plugins:
            summary_text.append(f"Plugins Installed: {len(result.installed_plugins)}\n", style="blue")
        
        if result.has_failures:
            summary_text.append(f"Failed Jobs: {len(result.failed_jobs)}\n", style="red")
            summary_text.append(f"Failed Views: {len(result.failed_views)}\n", style="red")
        
        panel = Panel(summary_text, title="Transfer Summary", border_style="blue")
        self.console.print(panel)
        
        # Detailed results
        if result.successful_jobs or result.failed_jobs:
            self._show_job_results(result)
        
        if result.successful_views or result.failed_views:
            self._show_view_results(result)
        
        if result.installed_plugins or result.failed_plugins:
            self._show_plugin_results(result)
        
        if result.warnings:
            self._show_warnings(result.warnings)
    
    def _show_job_results(self, result: TransferResult) -> None:
        """Show detailed job transfer results."""
        table = self._create_table("Job Transfer Results")
        table.add_column("Job Name", style="cyan")
        table.add_column("Status", style="white")
        table.add_column("Details", style="white")
        
        for job_name in result.successful_jobs:
            table.add_row(job_name, "✓ Success", "Transferred successfully")
        
        for job_name, error in result.failed_jobs.items():
            table.add_row(job_name, "✗ Failed", error)
        
        self.console.print(table)
    
    def _show_view_results(self, result: TransferResult) -> None:
        """Show detailed view transfer results."""
        table = self._create_table("View Transfer Results")
        table.add_column("View Name", style="cyan")
        table.add_column("Status", style="white")
        table.add_column("Details", style="white")
        
        for view_name in result.successful_views:
            table.add_row(view_name, "✓ Success", "Transferred successfully")
        
        for view_name, error in result.failed_views.items():
            table.add_row(view_name, "✗ Failed", error)
        
        self.console.print(table)
    
    def _show_plugin_results(self, result: TransferResult) -> None:
        """Show detailed plugin installation results."""
        table = self._create_table("Plugin Installation Results")
        table.add_column("Plugin Name", style="cyan")
        table.add_column("Status", style="white")
        table.add_column("Details", style="white")
        
        for plugin_name in result.installed_plugins:
            table.add_row(plugin_name, "✓ Installed", "Installation initiated")
        
        for plugin_name, error in result.failed_plugins.items():
            table.add_row(plugin_name, "✗ Failed", error)
        
        if result.installed_plugins:
            table.add_row(
                "", 
                "⚠ Note", 
                "Jenkins restart required to complete plugin installation"
            )
        
        self.console.print(table)
    
    def _show_warnings(self, warnings: List[str]) -> None:
        """Show warnings to the user."""
        if not warnings:
            return
        
        warning_text = Text()
        for warning in warnings:
            warning_text.append(f"• {warning}\n", style="yellow")
        
        panel = Panel(warning_text, title="Warnings", border_style="yellow")
        self.console.print(panel)
    
    def show_validation_results(self, validation: ValidationResult, context: str) -> None:
        """
        Show validation results.
        
        Args:
            validation: Validation result
            context: Context for the validation (e.g., "Input Validation")
        """
        if self.config.default_mode == OperationMode.QUIET and validation.is_valid:
            return
        
        if validation.is_valid and not validation.warnings:
            # No need to show anything for valid inputs without warnings
            return
        
        table = self._create_table(context)
        table.add_column("Type", style="white")
        table.add_column("Message", style="white")
        
        for error in validation.errors:
            table.add_row("❌ Error", error)
        
        for warning in validation.warnings:
            table.add_row("⚠️  Warning", warning)
        
        self.console.print(table)
    
    def show_progress_start(self, operation: str, total_items: int) -> None:
        """
        Show start of a progress operation.
        
        Args:
            operation: Name of the operation
            total_items: Total number of items to process
        """
        if self.config.default_mode == OperationMode.QUIET:
            return
        
        self.console.print(f"\n🚀 Starting {operation} ({total_items} items)...")
    
    def show_progress_item(self, item_name: str, status: str, details: str = "") -> None:
        """
        Show progress for individual item.
        
        Args:
            item_name: Name of the item being processed
            status: Status (success, failed, processing)
            details: Additional details
        """
        if self.config.default_mode == OperationMode.QUIET:
            return
        
        status_icons = {
            "processing": "⏳",
            "success": "✅",
            "failed": "❌",
            "warning": "⚠️"
        }
        
        icon = status_icons.get(status, "•")
        message = f"{icon} {item_name}"
        if details:
            message += f" - {details}"
        
        self.console.print(message)
    
    def show_progress_complete(self, operation: str, success_count: int, total_count: int) -> None:
        """
        Show completion of a progress operation.
        
        Args:
            operation: Name of the operation
            success_count: Number of successful items
            total_count: Total number of items
        """
        if self.config.default_mode == OperationMode.QUIET:
            return
        
        if success_count == total_count:
            self.console.print(f"✅ {operation} completed successfully ({success_count}/{total_count})")
        else:
            self.console.print(f"⚠️  {operation} completed with issues ({success_count}/{total_count} successful)")
    
    def show_plugin_dependencies(self, job_name: str, required_plugins: List[str]) -> None:
        """
        Show plugin dependencies for a job.
        
        Args:
            job_name: Name of the job
            required_plugins: List of required plugins
        """
        if self.config.default_mode == OperationMode.QUIET:
            return
        
        if not required_plugins:
            self.console.print(f"✅ Job '{job_name}' has no missing plugin dependencies")
            return
        
        table = self._create_table(f"Plugin Dependencies for '{job_name}'")
        table.add_column("Plugin Name", style="cyan")
        table.add_column("Status", style="white")
        
        for plugin in required_plugins:
            table.add_row(plugin, "❌ Missing")
        
        self.console.print(table)
    
    def show_cleanup_results(self, server_name: str, cleaned_views: List[str], errors: List[str]) -> None:
        """
        Show cleanup operation results.
        
        Args:
            server_name: Name of the server (production/interim)
            cleaned_views: List of views that were cleaned up
            errors: List of cleanup errors
        """
        if self.config.default_mode == OperationMode.QUIET:
            return
        
        table = self._create_table(f"{server_name.title()} Server Cleanup")
        table.add_column("Item", style="cyan")
        table.add_column("Status", style="white")
        
        if cleaned_views:
            for view in cleaned_views:
                table.add_row(f"View: {view}", "✅ Cleaned up")
        
        if errors:
            for error in errors:
                table.add_row("Error", f"❌ {error}")
        
        if not cleaned_views and not errors:
            table.add_row("Result", "ℹ️  No cleanup needed")
        
        self.console.print(table)
    
    def print_error(self, message: str, details: Optional[str] = None) -> None:
        """
        Print an error message.
        
        Args:
            message: Error message
            details: Additional error details
        """
        error_text = f"❌ Error: {message}"
        if details:
            error_text += f"\nDetails: {details}"
        
        self.console.print(error_text, style="red")
    
    def print_warning(self, message: str) -> None:
        """
        Print a warning message.
        
        Args:
            message: Warning message
        """
        self.console.print(f"⚠️  Warning: {message}", style="yellow")
    
    def print_info(self, message: str) -> None:
        """
        Print an info message.
        
        Args:
            message: Info message
        """
        self.console.print(f"ℹ️  {message}", style="blue")