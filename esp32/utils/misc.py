from utils.timeit import timed_function

@timed_function
def file_lines_count(filename):
    with open(filename) as f:
        for i, l in enumerate(f):
            pass
    return i + 1
