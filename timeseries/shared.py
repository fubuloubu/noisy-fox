def check_list(ls):
    if not isinstance(ls, list):
        raise ValueError("Requires a list!")

def check_tuple(pt):
    if not isinstance(pt, tuple):
        raise ValueError("Requires a list of tuples!")

SIGFIGS=6
EPSILON=1./10**SIGFIGS

def get_update_rate(next_time, prev_time):
    return next_time - prev_time

def check_update_rate(next_time, prev_time, update_rate):
    if update_rate <= 0:
        raise ValueError("Update Rate is not valid!")
    # check if calculated rate is within 0.001% of update rate
    if abs(get_update_rate(next_time, prev_time) - \
            float(update_rate)) >= update_rate*EPSILON:
        raise ValueError("Update Rate not consistent!")

# Ensure our floats are properly rounded because this can
# cause errors when decompressing
def add_and_round(prev_time, update_rate):
    next_time = prev_time + update_rate
    if isinstance(next_time, float):
        next_time = round(next_time, SIGFIGS)
    return next_time

def calc_slope(prev_time, prev_data, next_time, next_data):
    return (next_data - prev_data) / float((next_time - prev_time))
