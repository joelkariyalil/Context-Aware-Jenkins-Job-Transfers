import jenkins
import jenkins_job_transfers as jjt
import logging
import pytest
from . import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""

    Testing Stratergy here

    Jobs (For both Console and Quiet Mode)
        1. Invalid Jobs
        2. Job with Plugins
        3. Job without Plugins

    Views (For both Console and Quiet Mode)
        1. Invalid Views
        2. Views with Jobs
        3. (Extra) Views containing Jobs with Plugins
        
"""