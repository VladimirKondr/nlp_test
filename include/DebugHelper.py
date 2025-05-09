from enum import Enum
import time
import os

class DebugMode(Enum):
    OFF = 0
    FILE = 1
    STDOUT = 2
    FILE_AND_STDOUT = 3

GLOBAL_DEBUG_MODE = DebugMode.FILE
GLOBAL_DEBUG_FILENAME = "debug.log"
GLOBAL_DEBUG_FILEMODE = 'a'
try:
    # Use absolute path to ensure consistent file location
    GLOBAL_DEBUG_FILEPATH = os.path.join(os.getcwd(), GLOBAL_DEBUG_FILENAME)
    GLOBAL_DEBUG_FILE = open(GLOBAL_DEBUG_FILEPATH, GLOBAL_DEBUG_FILEMODE) if GLOBAL_DEBUG_MODE in (DebugMode.FILE, DebugMode.FILE_AND_STDOUT) else None
    print(f"Debug log file opened at: {GLOBAL_DEBUG_FILEPATH}")
except Exception as e:
    print(f"Error opening debug file: {e}")
    GLOBAL_DEBUG_FILE = None


class DebugHelper:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DebugHelper, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Only initialize if not already done
        if not hasattr(self, '_initialized'):
            self._initialized = True

    @classmethod
    def get_instance(cls):
        """Get the singleton instance, creating it if necessary."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def log1(self, message: str, name: str):
        """Log a message to file, stdout, or both based on debug mode."""
        if GLOBAL_DEBUG_MODE == DebugMode.OFF:
            return
            
        # Fix the string formatting with escaped quotes
        timestamp = time.strftime("%H:%M")
        formatted_message = f"({timestamp})[{name}] {message}"
        
        if GLOBAL_DEBUG_MODE in (DebugMode.FILE, DebugMode.FILE_AND_STDOUT) and GLOBAL_DEBUG_FILE:
            try:
                GLOBAL_DEBUG_FILE.write(formatted_message + "\n")
                GLOBAL_DEBUG_FILE.flush()
            except Exception as e:
                print(f"Error writing to log file: {e}")
                
        if GLOBAL_DEBUG_MODE in (DebugMode.STDOUT, DebugMode.FILE_AND_STDOUT):
            print(formatted_message)

    @staticmethod
    def log(message: str, name: str = ""):
        """Static wrapper for logging via the singleton instance."""
        DebugHelper.get_instance().log1(message, name)

    def close(self):
        """Close the log file if open."""
        if GLOBAL_DEBUG_FILE:
            GLOBAL_DEBUG_FILE.close()

    @staticmethod
    def close_static():
        """Static wrapper for closing via the singleton instance."""
        DebugHelper.get_instance().close()

def time_func():
    """Decorator to measure and log execution time of sync or async functions, only when debug is enabled."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if GLOBAL_DEBUG_MODE == DebugMode.OFF:
                return func(*args, **kwargs)
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            elapsed_time = end_time - start_time
            DebugHelper.log(f"Function '{func.__qualname__}' took {elapsed_time:.2f} seconds")
            return result
        return wrapper
    return decorator