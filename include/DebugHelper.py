from enum import Enum
import time
import os

class DebugMode(Enum):
    OFF = 0
    FILE = 1
    STDOUT = 2
    FILE_AND_STDOUT = 3

GLOBAL_DEBUG_MODE = DebugMode.FILE_AND_STDOUT
GLOBAL_DEBUG_FILENAME = "debug.log"
GLOBAL_DEBUG_FILEMODE = 'w'
try:
    GLOBAL_DEBUG_FILEPATH = os.path.join(os.getcwd(), GLOBAL_DEBUG_FILENAME)
    GLOBAL_DEBUG_FILE = open(GLOBAL_DEBUG_FILEPATH, GLOBAL_DEBUG_FILEMODE) if GLOBAL_DEBUG_MODE in (DebugMode.FILE, DebugMode.FILE_AND_STDOUT) else None
    print(f"Debug log file opened at: {GLOBAL_DEBUG_FILEPATH}")
except Exception as e:
    print(f"Error opening debug file: {e}")
    GLOBAL_DEBUG_FILE = None


class DebugHelper:
    """
    A utility class for logging debug information and measuring execution time.
    Implements a singleton pattern to ensure a single instance.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DebugHelper, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.debug_file = None
            self._setup_debug_file()

    def _setup_debug_file(self):
        """Sets up the debug file if required by the global debug mode."""
        if GLOBAL_DEBUG_MODE in (DebugMode.FILE, DebugMode.FILE_AND_STDOUT):
            try:
                self.debug_file = open(GLOBAL_DEBUG_FILEPATH, GLOBAL_DEBUG_FILEMODE)
            except Exception as e:
                print(f"Error opening debug file: {e}")
                self.debug_file = None

    def log(self, message: str, name: str = ""):
        """Logs a message based on the current debug mode."""
        if GLOBAL_DEBUG_MODE == DebugMode.OFF:
            return

        timestamp = time.strftime("%H:%M")
        formatted_message = f"({timestamp})[{name}] {message}"

        if self.debug_file:
            try:
                self.debug_file.write(formatted_message + "\n")
                self.debug_file.flush()
            except Exception as e:
                print(f"Error writing to log file: {e}")

        if GLOBAL_DEBUG_MODE in (DebugMode.STDOUT, DebugMode.FILE_AND_STDOUT):
            print(formatted_message)

    def close(self):
        """Closes the debug file if it is open."""
        if self.debug_file:
            self.debug_file.close()

    @staticmethod
    def time_func():
        """Decorator to measure and log execution time of functions."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                if GLOBAL_DEBUG_MODE == DebugMode.OFF:
                    return func(*args, **kwargs)

                start_time = time.time()
                result = func(*args, **kwargs)
                elapsed_time = time.time() - start_time
                DebugHelper().log(f"Function '{func.__qualname__}' took {elapsed_time:.2f} seconds")
                return result

            return wrapper

        return decorator

DebugHelper()