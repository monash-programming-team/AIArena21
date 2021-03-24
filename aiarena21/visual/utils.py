import math

def interpolate_colour_discrete(colours, max_v, min_v, actual):
    proportion = min(1, max(0, (actual - min_v) / (max_v - min_v)))
    index = min(len(colours)-1, math.floor(proportion * len(colours)))
    return colours[index]
