from .shared import *
def compress(timeseries):
    # Trivial checks
    check_list(timeseries)
    if not len(timeseries) > 1:
        return timeseries, 0

    # Start with the first point in the series
    last_pt = timeseries[0]
    check_tuple(last_pt)
    compressed_timeseries = [last_pt]
    
    # For each point in the series
    update_rate = None
    last_added_pt = last_pt
    last_slope = None
    for this_pt in timeseries[1:]:
        check_tuple(this_pt)
        last_time, last_data = last_pt
        this_time, this_data = this_pt
        
        if not update_rate:
            update_rate = get_update_rate(this_time, last_time)
        check_update_rate(this_time, last_time, update_rate)
        
        this_slope = calc_slope(last_time, last_data, this_time, this_data)
        
        # If the last point was not added and we're not seeing a 
        # trend continuation, add that point to the series
        if last_pt != last_added_pt and this_slope != last_slope:
            compressed_timeseries.append(last_pt)
            last_added_pt = last_pt

        # Add this point if the slope is different
        # (or the first iteration has a data change)
        if (this_data != last_data and last_slope is None) or \
                (this_slope != last_slope and last_slope is not None):
            compressed_timeseries.append(this_pt)
            last_added_pt = this_pt

        # Update past values
        last_slope = this_slope
        last_pt = this_pt

    # Add the last point if missing, so we have the point to stop decompression
    if compressed_timeseries[-1] != last_pt:
        compressed_timeseries.append(last_pt)

    # Return the compressed dataset, as well as the update rate for decompression
    return compressed_timeseries, update_rate

def uncompress(timeseries, update_rate):

    check_list(timeseries)
    
    if not len(timeseries) > 1:
        return timeseries
    
    last_pt = timeseries[0]
    check_tuple(last_pt)
    uncompressed_timeseries = [last_pt]
    
    for this_pt in timeseries[1:]:
        check_tuple(this_pt)
        
        last_time, last_data = last_pt
        this_time, this_data = this_pt

        slope = calc_slope(last_time, last_data, this_time, this_data)
        
        # For all timeseries elements between the current entry time
        # and the next, filled in with datapoints matching the current
        # data with successive time increments using update_rate
        last_time = add_and_round(last_time, update_rate)
        while this_time > last_time:
            last_data = last_data + slope*update_rate
            last_pt = (last_time, last_data)
            uncompressed_timeseries.append(last_pt)
            last_time = add_and_round(last_time, update_rate)
        # After we've filled up the array with last data samples,
        # add the newest sample in there and do it again
        uncompressed_timeseries.append(this_pt)
        last_pt = this_pt

    return uncompressed_timeseries

if __name__ == '__main__':
    def assert_equal(l1, l2):
        round_list = lambda l: [(round(i[0], SIGFIGS), round(i[1], SIGFIGS)) for i in l]
        try:
            assert(round_list(l1) == round_list(l2))
        except AssertionError as error:
            # Collect all the diffs between the list, both directions
            # (in case one point exists in one list, but not the other)
            diff_times = [t for t, _ in list(set(l1) - set(l2))]
            diff_times.extend([t for t, _ in list(set(l2) - set(l1)) if t not in diff_times])
            diff_times.sort()
            # Use this list to get the diffs
            diffs = []
            for time in diff_times:
                # Try to find time in l1
                found_i = None
                for i, pt1 in enumerate(l1):
                    if pt1[0] == time:
                        found_i = i
                        break
                # Try to find time in l2
                found_j = None
                for j, pt2 in enumerate(l2):
                    if pt2[0] == time:
                        found_j = j
                        break
                diff_line = []
                if found_i and found_j:
                    # Both have it
                    # If not at extreme of list and times/values match for prior, add this line
                    if found_i > 0 and found_j > 0 and \
                            l1[found_i-1][0] == l2[found_j-1][0] and \
                            l1[found_i-1][1] == l2[found_j-1][1]:
                        diff_line.append('  bf: ({:4.3f}, {:4.3f})'.format(*l1[found_i-1]))
                    diff_line.append('< l1: ({:4.3f}, {:4.3f})'.format(*l1[found_i]))
                    diff_line.append('> l2: ({:4.3f}, {:4.3f})'.format(*l2[found_j]))
                    # If not at extreme of list and times/values match for later, add this line
                    if found_i < len(l1) and found_j < len(l2) and \
                            l1[found_i+1][0] == l2[found_j+1][0] and \
                            l1[found_i+1][1] == l2[found_j+1][1]:
                        diff_line.append('  af: ({:4.3f}, {:4.3f})'.format(*l1[found_i+1]))
                elif found_i:
                    diff_line.append('+ l1: ({:4.3f},  {:4.3f})'.format(*l1[found_i]))
                elif found_j:
                    diff_line.append('+ l2: ({:4.3f},  {:4.3f})'.format(*l2[found_j]))
                diffs.append('\n'.join(diff_line))
            print('Assertion Failure:\n{}\n'.format('\n'.join(diffs)))
            raise error

    def assert_positive_compression(l1, l2):
        try:
            assert(len(l1) <= len(l2))
            return 100*(1 - len(l1)/float(len(l2)))
        except AssertionError as error:
            raise AssertionError('List:\n{0}\n  length ({1}) is not less than length ({3}) of:\n{2}'.\
                    format(l1, len(l1), l2, len(l2)))

    # Trvial cases
    timeseries = []
    assert_equal(uncompress(*compress(timeseries)), timeseries)
    timeseries = [(0.0, 0.0)]
    assert_equal(uncompress(*compress(timeseries)), timeseries)
    timeseries = [(0.0, 0.0), (1.0, 0.0)]
    compressed_timeseries = timeseries
    assert(compress(timeseries)[1] == 1.0)
    assert_equal(compress(timeseries)[0], compressed_timeseries)
    assert_equal(uncompress(*compress(timeseries)), timeseries)
    
    # Flat lines work appropiately
    print("Running flat line test")
    timeseries = [(0.0, 1.0), (1.0, 1.0), (2.0, 1.0), (3.0, 1.0)]
    compressed_timeseries = [(0.0, 1.0), (3.0, 1.0)]
    assert(compress(timeseries)[1] == 1.0)
    assert_equal(compress(timeseries)[0], compressed_timeseries)
    assert_equal(uncompress(*compress(timeseries)), timeseries)
    
    # Steps work appropiately
    print("Running step detect test")
    timeseries = [(0.0, 0.0), (1.0, 0.0), (2.0, 0.0), (3.0, 2.0), (4.0, 2.0)]
    compressed_timeseries = [(0.0, 0.0), (2.0, 0.0), (3.0, 2.0), (4.0, 2.0)]
    assert(compress(timeseries)[1] == 1.0)
    assert_equal(compress(timeseries)[0], compressed_timeseries)
    assert_equal(uncompress(*compress(timeseries)), timeseries)

    # Ramps work appropiately
    print("Running ramp detect test (without wait)")
    timeseries = [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0), (3.0, 3.0), (4.0, 3.0)]
    compressed_timeseries = [(0.0, 0.0), (1.0, 1.0), (3.0, 3.0), (4.0, 3.0)]
    assert(compress(timeseries)[1] == 1.0)
    assert_equal(compress(timeseries)[0], compressed_timeseries)
    assert_equal(uncompress(*compress(timeseries)), timeseries)
    print("Running ramp detect test (with wait)")
    timeseries = [(0.0, 0.0), (1.0, 0.0), (2.0, 1.0), (3.0, 2.0), (4.0, 3.0)]
    compressed_timeseries = [(0.0, 0.0), (1.0, 0.0), (2.0, 1.0), (4.0, 3.0)]
    assert(compress(timeseries)[1] == 1.0)
    assert_equal(compress(timeseries)[0], compressed_timeseries)
    assert_equal(uncompress(*compress(timeseries)), timeseries)

    # Randomized trials to gauge efficiency
    from random import randrange as rand_range, uniform as rand_float
    N = 1000
    print("Running randomized trials (boolean)")
    avg_comp = None
    for i in range(10): # run this many trials
        timeseries = [(t/N, float(rand_range(0.0,2.0))) for t in range(N)]
        assert_equal(uncompress(*compress(timeseries)), timeseries)
        comp = assert_positive_compression(compress(timeseries)[0], timeseries)
        avg_comp = comp if not avg_comp else (comp + i*avg_comp)/(i+1)
    print('  Average compression: {:3.2f}%'.format(avg_comp))
    
    print("Running randomized trials (integer [0, 9])")
    avg_comp = None
    for i in range(10): # run this many trials
        timeseries = [(t/N, float(rand_range(0.0,10.0))) for t in range(N)]
        assert_equal(uncompress(*compress(timeseries)), timeseries)
        comp = assert_positive_compression(compress(timeseries)[0], timeseries)
        avg_comp = comp if not avg_comp else (comp + i*avg_comp)/(i+1)
    print('  Average compression: {:3.2f}%'.format(avg_comp))
    
    print("Running randomized trials (normal dist [-10.0, 10.0])")
    avg_comp = None
    for i in range(10): # run this many trials
        timeseries = [(t/N, rand_float(-10.0,10.0)) for t in range(N)]
        assert_equal(uncompress(*compress(timeseries)), timeseries)
        comp = assert_positive_compression(compress(timeseries)[0], timeseries)
        avg_comp = comp if not avg_comp else (comp + i*avg_comp)/(i+1)
    print('  Average compression: {:3.2f}%'.format(avg_comp))
    
    print('compress()/uncompress() Testing Passed!')
