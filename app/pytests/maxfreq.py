import functools
import time

# timestamp long int by function name
last_run_by_func = dict()

# maxfreq 5 means func executes at most 5 times per
# second (at least 1/5 seconds between)
# If func is called less than 1/freq seconds since last call, it doesn't execute and None is returned
def max_freq(maxfreq):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_run_time = 0
            if func.__name__ in last_run_by_func:
                last_run_time = last_run_by_func[func.__name__]
            current_time = time.time()
            if current_time - last_run_time > 1 / maxfreq:
                last_run_by_func[func.__name__] = current_time
                return = func(*args,**kwargs)
            else:
                return None
        return wrapper
    return decorator


# demonstrate maxfreq:

@max_freq(maxfreq=2)
def afunc():
    print(f"afunc at {time.time()}")

@max_freq(maxfreq=1.5)
def bfunc():
    print(f"bfunc at {time.time()}")

for i in range(0, 99):
    afunc()
    bfunc()
    time.sleep(.1)
