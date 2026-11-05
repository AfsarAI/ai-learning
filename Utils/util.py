import os

START = "\033[90m"
END = "\033[0m"

def log(message):
    if(os.getenv("DEBUG") == "True"):
        print(f" {START}{message}{END}")