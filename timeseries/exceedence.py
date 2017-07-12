from .shared import *
from .compression import uncompress

def get_exceedences(actual_data, expected_data, sample_time, lsb=0, latency=0, variance=0):
    # Ensure input data is the right types
    check_list(actual_data)
    check_list(expected_data)
    check_tuple(actual_data[0])
    check_tuple(actual_data[-1])
    check_tuple(expected_data[0])
    check_tuple(expected_data[-1])

    # Ensure the time boundaries of the two lists match
    a0_t, _ = actual_data[0]
    e0_t, _ = expected_data[0]
    aN_t, _ = actual_data[-1]
    eN_t, _ = expected_data[-1]
    if a0_t != e0_t or aN_t != eN_t:
        raise ValueError("Begining and Ending Times must be aligned")

    # Verify lists are same lengths, or else we can't do the algorithm
    a_decompressed = False
    e_decompressed = False
    if len(actual_data) != len(expected_data) or \
            [t for t, _ in actual_data] != \
            [t for t, _ in expected_data]:
                # Check for data equivalency and decompress
                # to attempt to get lengths to match
                if len(actual_data) < len(expected_data):
                    actual_data = uncompress(actual_data, sample_time)
                    a_decompressed = True
                if len(expected_data) < len(actual_data):
                    expected_data = uncompress(expected_data, sample_time)
                    e_decompressed = True
                if len(actual_data) < len(expected_data) and not a_decompressed:
                    actual_data = uncompress(actual_data, sample_time)
                    a_decompressed = True
                # If it still doesn't match then it's an error
                if len(actual_data) != len(expected_data) or \
                        [t for t, _ in actual_data] != \
                        [t for t, _ in expected_data]:
                    raise ValueError("Decompressed data doesn't align!")

    # Start our checking algorithm
    exceedences = []
    for a_pt, e_pt in zip(actual_data, expected_data):
        if not a_decompressed:
            check_tuple(a_pt)
        if not e_decompressed:
            check_tuple(e_pt)

        # Ensure each actual point is within the bound given by the shape 
        # drawn via the expected shape skewed in  +/- X and + T directions
        # given our values of latency and variance.
        
        # Ensure these shapes are on proper bounds given our values of lsb
        # and sample time so we don't get false negatives.

        # If we have a confirmed positive exceedence, append it to our list of exceedences
        # This should return an entire section of points that exceed our bounds

    return exceedences

if __name__ == '__main__':
    # Trivial cases
    assert(get_exceedences([(0, 1), (1, 1)], [(0, 1), (1, 1)], 1) == [])

    from random import randrange as rand_range
    from .compression import compress
    N = 100
    for _ in range(10): # run this many trials
        timeseries, sample_time = compress([(t/N, rand_range(0,2)) for t in range(N+1)])
        assert(get_exceedences(timeseries, [(0,1), (1,1)], sample_time, variance=1) == [])

    print("get_exceedences() Testing Passed!")
