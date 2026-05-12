"""
filename: logger.py
module: Logging Utility
author: Talha Ahmad
date: 2026-05-12
"""

import logging
import os

# Set up logging to both file and console
log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'quiz_errors.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

def get_logger(name):
    """Returns a logger instance with the specified name"""
    return logging.getLogger(name)
