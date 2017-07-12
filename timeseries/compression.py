def _check_list(ls):
    if not isinstance(ls, list):
        raise ValueError("Requires a list!")

def _check_tuple(pt):
    if not isinstance(pt, tuple):
        raise ValueError("Requires a list of tuples!")

_SIGFIGS=6
_EPSILON=1./10**_SIGFIGS
def _get_update_rate(next_time, prev_time):
    return next_time - prev_time

def _check_update_rate(next_time, prev_time, update_rate):
    if update_rate <= 0:
        raise ValueError("Update Rate is not valid!")
    # check if calculated rate is within 0.001% of update rate
    if abs(_get_update_rate(next_time, prev_time) - \
            float(update_rate)) >= update_rate*_EPSILON:
        raise ValueError("Update Rate not consistent!")

# Ensure our floats are properly rounded because this can
# cause errors when decompressing
def _add_and_round(prev_time, update_rate):
    next_time = prev_time + update_rate
    if isinstance(next_time, float):
        next_time = round(next_time, _SIGFIGS)
    return next_time

def compress(timeseries):

    _check_list(timeseries)
    
    if not len(timeseries) > 1:
        return timeseries, 0
    
    prev_pt = timeseries[0]
    _check_tuple(prev_pt)
    compressed_timeseries = [prev_pt]
    
    update_rate = None
    for next_pt in timeseries[1:]:
        _check_tuple(next_pt)
        prev_time, prev_data = prev_pt
        next_time, next_data = next_pt

        if not update_rate:
            update_rate = _get_update_rate(next_time, prev_time)
        _check_update_rate(next_time, prev_time, update_rate)
        
        if next_data != prev_data:
            compressed_timeseries.append(next_pt)
        
        prev_pt = next_pt

    # Add the last point if missing, so we understand where to stop
    if prev_pt != compressed_timeseries[-1]:
        compressed_timeseries.append(timeseries[-1])
    return compressed_timeseries, update_rate

def uncompress(timeseries, update_rate):

    _check_list(timeseries)
    
    if not len(timeseries) > 1:
        return timeseries
    
    prev_pt = timeseries[0]
    _check_tuple(prev_pt)
    uncompressed_timeseries = [prev_pt]
    
    prev_time, prev_data = prev_pt

    for next_pt in timeseries[1:]:
        _check_tuple(next_pt)
        next_time, next_data = next_pt
        
        # For all timeseries elements between the current entry time
        # and the next, fille in with datapoints matching the current
        # data with successive time increments using update_rate
        prev_time = _add_and_round(prev_time, update_rate)
        while next_time > prev_time:
            uncompressed_timeseries.append((prev_time, prev_data))
            prev_time = _add_and_round(prev_time, update_rate)

        # After we've filled up the array with previous data samples,
        # add the newest sample in there and do it again
        uncompressed_timeseries.append(next_pt)
        prev_data = next_data
        prev_time = next_time

    return uncompressed_timeseries

if __name__ == '__main__':
    # Trviai cases
    timeseries = []
    assert(uncompress(*compress(timeseries)) == timeseries)
    timeseries = [(0, 0)]
    assert(uncompress(*compress(timeseries)) == timeseries)
    timeseries = [(0, 0), (1, 0)]
    assert(compress(timeseries) == ([(0, 0), (1, 0)], 1))
    assert(uncompress(*compress(timeseries)) == timeseries)
    timeseries = [(0, 1), (1, 1), (2, 1), (3, 1)]
    assert(compress(timeseries) == ([(0, 1), (3, 1)], 1))
    assert(uncompress(*compress(timeseries)) == timeseries)

    # More advanced cases
    from random import randrange as rand_range
    N = 100
    for _ in range(10): # run this many trials
        timeseries = [(t/N, rand_range(0,2)) for t in range(N)]
        assert(uncompress(*compress(timeseries)) == timeseries)

    print('compress()/uncompress() Testing Passed!')
