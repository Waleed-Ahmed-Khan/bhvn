try:
    from .logger import AppLogger
    from .logging import get_logger
except ImportError:
    from logger import AppLogger
    from logging import get_logger