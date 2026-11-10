import os


END = "\033[0m"

START = "\033[90m"
def log(message):
    if(os.getenv("DEBUG") == "True"):
        print(f" {START}{message}{END}")

START_ERROR = "\033[91m"
def log_error(message):
    if(os.getenv("DEBUG") == "True"):
        print(f" {START_ERROR}Error: {message}{END}")