from datetime import timedelta
from timeit import default_timer as timer
import datetime
import functools


def print_timing(message, sep='-'):
    assert message is not None, "Message is not passed to print_timing decorator"

    def deco_wrapper(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = timer()
            print(sep * 20)
            print(f'{message} started {datetime.datetime.now().strftime("%H:%M:%S")}')
            result = func(*args, **kwargs)
            end = timer()
            print(f"{message} finished in {timedelta(seconds=end - start)}")
            print(sep * 20)
            return result

        return wrapper

    return deco_wrapper
