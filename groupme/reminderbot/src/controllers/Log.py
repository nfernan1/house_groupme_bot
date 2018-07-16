import sys


class Log:


    def debug(msg):
        print(str(msg))
        sys.stdout.flush()