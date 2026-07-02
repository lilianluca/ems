"""
This module is used to register all the models in the application.
It is imported in the main application file to ensure that all models
are registered before the application starts.
"""

from src.devices.models import *  # noqa: F403
from src.sites.models import *  # noqa: F403
from src.users.models import *  # noqa: F403
