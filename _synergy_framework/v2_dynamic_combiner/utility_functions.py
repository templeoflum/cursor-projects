# Utility Functions
def normalize_value(value, min_range=-1, max_range=1):
    return max(min(value, max_range), min_range)

def calculate_fluctuation(degree):
    return math.sin(2 * math.pi * degree)
