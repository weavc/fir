import json

from termcolor import colored

class Logger:
    verbose: bool = False
    pretty: bool = False
    silent: bool = False
    debug: bool = False

    def __init__(self, verbose: bool = False, pretty: bool = False, silent: bool = False, debug: bool = False):
        self.verbose = verbose
        self.pretty = pretty
        self.silent = silent
        self.debug = debug

    def log(self, message: str | dict):
        if type(message) is dict:
            self.log_dict(message)
            return
        if self.silent:
            return
        print(message)

    def log_debug(self, message: str):
        if not self.debug:
            return
        self.log(f'{colored("[Dedug]:", "blue", attrs=["bold"])} {message}')

    def log_dict(self, obj: dict):
        if self.pretty:
            json_formatted_str = json.dumps(obj, indent=2, skipkeys=False)
            self.log(json_formatted_str)
            return
        self.log(str(obj))

    def log_error(self, message: str, exit: bool = True):
        self.log(f'{colored("[Error]:", "red", attrs=["bold"])} {message}')
        if exit:
            raise SystemExit(1)
        
    def log_success(self, message: str):
        self.log(f'{colored("[Success]:", "green", attrs=["bold"])} {message}')
    
    def log_warning(self, message: str):
        if not self.verbose and not self.debug:
            return
        self.log(f'{colored("[Warning]:", "yellow", attrs=["bold"])} {message}')
    
    def log_info(self, message: str):
        if not self.verbose and not self.debug:
            return
        self.log(f'{colored("[Info]:", "cyan", attrs=["bold"])} {message}')

    