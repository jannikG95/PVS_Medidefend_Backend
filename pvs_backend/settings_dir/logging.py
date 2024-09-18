import glob
import logging
import os
import time
from logging.handlers import TimedRotatingFileHandler


class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[92m',  # Grün
        'WARNING': '\033[93m',  # Gelb
        'ERROR': '\033[91m',  # Rot
        'CRITICAL': '\033[91m'  # Rot
    }
    RESET = '\033[0m'

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, '')
        message = super().format(record)
        return f"{log_color}{message}{self.RESET if log_color else ''}"


class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename, when='midnight', interval=1, backupCount=10, encoding=None, delay=False, utc=False,
                 atTime=None):
        super().__init__(filename, when, interval, backupCount, encoding, delay, utc, atTime)
        self._rotate_at_startup()

    def _rotate_at_startup(self):
        try:
            if self.stream:
                self.stream.close()
                self.stream = None

            if os.path.exists(self.baseFilename):
                currentTime = int(time.time())
                timestamp = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(currentTime))
                newFilename = f"{os.path.splitext(self.baseFilename)[0]}_{timestamp}.log"
                self.rotate(self.baseFilename, newFilename)
                self.cleanup()
        except PermissionError as e:
            print(f"Could not rotate log file at startup due to: {e}")
        finally:
            self.stream = self._open()

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None

        currentTime = int(time.time())
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(currentTime))
        newFilename = f"{os.path.splitext(self.baseFilename)[0]}_{timestamp}.log"

        if os.path.exists(newFilename):
            os.remove(newFilename)

        self.rotate(self.baseFilename, newFilename)

        # Re-open the base file as the current log file
        self.stream = self._open()

        # Compute the new rollover time
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt += self.interval

        self.rolloverAt = newRolloverAt

        # Remove old log files
        self.cleanup()

    def cleanup(self):
        log_dir, base_filename = os.path.split(self.baseFilename)
        log_files = sorted(
            glob.glob(os.path.join(log_dir, f"{os.path.splitext(base_filename)[0]}_*.log")),
            key=os.path.getmtime
        )

        while len(log_files) > self.backupCount:
            os.remove(log_files.pop(0))

    def _open(self):
        return open(self.baseFilename, 'a', encoding=self.encoding)


# Logging settings

log_dir = './logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        },
        'colored': {
            '()': ColoredFormatter,
            'format': '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'colored',
        },
        'file': {
            'level': 'INFO',
            'class': 'pvs_backend.settings_dir.logging.CustomTimedRotatingFileHandler',
            'filename': os.path.join('./logs', 'autoresponder.log'),
            'when': 'midnight',
            'backupCount': 10,
            'formatter': 'standard',
            'delay': True,
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
