from .shared import *
def compress(timeseries):

    check_list(timeseries)
    
    if not len(timeseries) > 1:
        return timeseries, 0
    
    prev_pt = timeseries[0]
    check_tuple(prev_pt)
    compressed_timeseries = [prev_pt]
    
    update_rate = None
    for next_pt in timeseries[1:]:
        check_tuple(next_pt)
        prev_time, prev_data = prev_pt
        next_time, next_data = next_pt

        if not update_rate:
            update_rate = get_update_rate(next_time, prev_time)
        check_update_rate(next_time, prev_time, update_rate)
        
        if next_data != prev_data:
            compressed_timeseries.append((next_time, prev_data)) # step
            compressed_timeseries.append(next_pt)
        
        prev_pt = next_pt

    # Add the last point if missing, so we understand where to stop
    if prev_pt != compressed_timeseries[-1]:
        compressed_timeseries.append(timeseries[-1])
    return compressed_timeseries, update_rate

def uncompress(timeseries, update_rate):

    check_list(timeseries)
    
    if not len(timeseries) > 1:
        return timeseries
    
    prev_pt = timeseries[0]
    check_tuple(prev_pt)
    uncompressed_timeseries = [prev_pt]
    
    for next_pt in timeseries[1:]:
        check_tuple(next_pt)
        
        prev_time, prev_data = prev_pt
        next_time, next_data = next_pt
        
        if prev_time == next_time:
            uncompressed_timeseries.pop() # Handle steps

        # For all timeseries elements between the current entry time
        # and the next, fille in with datapoints matching the current
        # data with successive time increments using update_rate
        prev_time = add_and_round(prev_time, update_rate)
        while next_time > prev_time:
            prev_pt = (prev_time, prev_data)
            uncompressed_timeseries.append(prev_pt)
            prev_time = add_and_round(prev_time, update_rate)
        # After we've filled up the array with previous data samples,
        # add the newest sample in there and do it again
        uncompressed_timeseries.append(next_pt)
        prev_pt = next_pt

    return uncompressed_timeseries

if __name__ == '__main__':
    def assert_equal(q1, q2):
        try:
            assert(q1 == q2)
        except AssertionError as error:
            raise AssertionError('Result:\n{}\n  is not equal to:\n{}'.format(q1, q2))

    # Trvial cases
    timeseries = []
    assert_equal(uncompress(*compress(timeseries)), timeseries)
    timeseries = [(0, 0)]
    assert_equal(uncompress(*compress(timeseries)), timeseries)
    timeseries = [(0, 0), (1, 0)]
    assert_equal(compress(timeseries), ([(0, 0), (1, 0)], 1))
    assert_equal(uncompress(*compress(timeseries)), timeseries)
    
    # Flat lines
    timeseries = [(0, 1), (1, 1), (2, 1), (3, 1)]
    assert_equal(compress(timeseries), ([(0, 1), (3, 1)], 1))
    assert_equal(uncompress(*compress(timeseries)), timeseries)
    
    # Steps work appropiately
    timeseries = [(0, 0), (1, 0), (2, 2), (3, 2)]
    assert_equal(compress(timeseries), ([(0, 0), (2, 0), (2, 2), (3, 2)], 1))
    assert_equal(uncompress(*compress(timeseries)), timeseries)

    # More advanced cases
    from random import randrange as rand_range
    N = 100
    for _ in range(10): # run this many trials
        timeseries = [(t/N, rand_range(0,2)) for t in range(N)]
        assert_equal(uncompress(*compress(timeseries)), timeseries)

    print('compress()/uncompress() Testing Passed!')
