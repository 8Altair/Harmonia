import logging, colorlog

from pathlib import Path


def configure_logging(log_file_name: str, logger_name: str = None):
    """
        Configure a logger with console and file output.
        
        Args:
            log_file_name: Name of the log file ("pipeline_log.txt")
            logger_name: Optional name for the logger. If None, uses log_file_name without extension.
    
        Returns:
            Configured logger instance
    """
    if logger_name is None:
        logger_name = log_file_name.replace(".txt", "")
    
    logger = colorlog.getLogger(logger_name)   # Create a logger object
    logger.handlers.clear() # Avoid duplicate handlers on reload
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # Configure logging to output messages to the console with color formatting
    handler = colorlog.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)s: %(message)s",  # Customize the log message format
        log_colors=
        {  # Customize the colors for different log levels
            "DEBUG": "blue",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        }
    ))

    project_root_directory = Path(__file__).resolve().parent
    logs_directory = project_root_directory / "Logs"

    logs_directory.mkdir(parents=True, exist_ok=True)  # Ensure Logs directory exists under project root
    file_handler = logging.FileHandler(logs_directory / log_file_name, mode="w", encoding="utf-8",  delay=False)    # Create a file handler to write log messages to a text file
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))

    logger.addHandler(handler)
    logger.addHandler(file_handler)

    return logger


# Create the loggers
preprocessing_logger = configure_logging("preprocessing.txt")
vad_logger = configure_logging("vad.txt")
asr_model_logger = configure_logging("asr_model.txt")
language_detection_logger = configure_logging("language_detection.txt")
language_decision_logger = configure_logging("language_decision.txt")
file_transcription_logger = configure_logging("file_transcription.txt")
live_transcription_logger = configure_logging("live_transcription.txt")
nmt_model_logger = configure_logging("nmt_model.txt")
translator_logger = configure_logging("translator.txt")
tts_model_logger = configure_logging("tts.txt")
speech_synthesis_logger = configure_logging("speech_synthesis.txt")
