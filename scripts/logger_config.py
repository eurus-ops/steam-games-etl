import logging, config

# Logger shared by every module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Line format used by both outputs
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
)

# Console output
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# File output, UTF-8 so non-ASCII game names do not break the write
file_handler = logging.FileHandler(config.LOG_FILE_PATH, encoding="utf-8")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# Attach both outputs
logger.addHandler(console_handler)
logger.addHandler(file_handler)
