"""Logging utilities placeholder."""
"""Usage: 
    from app.utils.logger import setup_logger
    get_logger()
"""
# src/core/logger.py
import logging
import sys

# ANSI colors
RESET = "\033[0m"
BOLD = "\033[1m"

COLORS = {
    "DEBUG": "\033[36m",     # Cyan
    "INFO": "\033[32m",      # Green
    "WARNING": "\033[33m",   # Yellow
    "ERROR": "\033[31m",     # Red
    "CRITICAL": "\033[41m",  # Red background
}

FILENAME_COLOR = "\033[35m"   # Magenta
MAX_NAME_LEN = 40             # width limit for logger name


def trim_name(name: str) -> str:
    """Trim logger name to MAX_NAME_LEN from the left, preserving the right side."""
    if len(name) <= MAX_NAME_LEN:
        return name
    return "..." + name[-(MAX_NAME_LEN - 3):]   # 3 chars for "..."


class ColorFormatter(logging.Formatter):
    def format(self, record):
        # Format timestamp (bold)
        record.asctime = f"{BOLD}{self.formatTime(record)}{RESET}"

        # Colorize level
        level_color = COLORS.get(record.levelname, "")
        record.levelname = f"{level_color}{record.levelname}{RESET}"

        # Trim + colorize module/logger name
        trimmed = trim_name(record.name)
        record.name = f"{FILENAME_COLOR}{trimmed}{RESET}"

        return super().format(record)


def get_logger(name: str = None):
    """Get a logger instance for the calling module.
    
    Args:
        name: Optional logger name. If not provided, uses the caller's module name.
    
    Returns:
        Logger instance
    """
    # If no name provided, get the caller's module name
    if name is None:
        import inspect
        frame = inspect.currentframe()
        caller_frame = frame.f_back
        name = caller_frame.f_globals.get('__name__', 'unknown')
    
    logging.captureWarnings(True)

    fmt = "%(asctime)s | %(levelname)-9s | %(name)-50s | %(message)s"
    color_formatter = ColorFormatter(fmt)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(color_formatter)

    # Only configure root logger once
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.INFO,
            handlers=[stream_handler],
        )

    logger = logging.getLogger(name)
    return logger