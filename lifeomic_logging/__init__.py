import logging
from lifeomic_logging.logger import scoped_logger, get_request_context

logging.getLogger("aws_xray_sdk").setLevel(logging.CRITICAL)
logging.getLogger("aws_xray_sdk.core.models.entity").setLevel(logging.ERROR)

__all__ = ["scoped_logger", "get_request_context"]
