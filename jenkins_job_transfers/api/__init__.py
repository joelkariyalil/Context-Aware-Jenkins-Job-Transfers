"""
API layer for Jenkins Job Transfers.
"""

from .new_api import (
    create_manager, create_manager_from_configs,
    connect, transfer, check_publish_standards,
    check_plugin_dependencies, check_and_install_plugin_dependencies,
    production_cleanup, interim_cleanup, set_console_size,
    get_manager, reset_manager
)

__all__ = [
    # New API (recommended)
    'create_manager',
    'create_manager_from_configs',
    'get_manager',
    'reset_manager',
    
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

