"""Manages the configuration of logging operations across the ETL pipeline."""

import logging


def setup_logging(output: str, filename="t3.log", level=20):
    """Setup the basicConfig."""
    log_format = "{asctime} - {levelname} - {message}"
    log_datefmt = "%Y-%m-%d %H:%M"
    if output == "file":
        logging.basicConfig(
            filename=filename,
            encoding="utf-8",
            filemode="a",
            level=level,
            format=log_format,
            style="{",
            datefmt=log_datefmt
        )
        logging.info("Logging to file: %s", filename)
    else:
        logging.basicConfig(
            level=level,
            format=log_format,
            style="{",
            datefmt=log_datefmt
        )
        logging.info("Logging to console.")


if __name__ == '__main__':

    setup_logging("console")
