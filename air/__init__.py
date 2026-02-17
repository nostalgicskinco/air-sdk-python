"""AIR SDK — Record, replay, and govern every AI decision."""

__version__ = "0.1.0"

from air.client import AIRClient
from air.wrapper import air_wrap

__all__ = ["AIRClient", "air_wrap", "__version__"]
