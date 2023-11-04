candle = [ # green doji
    0,
    1,
    3,
    0,
    2
]

candle2 = [ # red doji
    0,
    3,
    5,
    0,
    2
]

candle3 = [ # green candle, no lower wick
    0,
    1,
    5,
    1,
    3
]

candle4 = [ # red candle, no upper wick
    0,
    3,
    3,
    0,
    1
]

def get_candle_body(candle):
    return candle[4] - candle[1]
def get_candle_size(candle):
    return abs(get_candle_body(candle))
def get_candle_direction(candle):
    if get_candle_body(candle) > 0:
        return 1
    elif get_candle_body(candle) < 0:
        return -1
    else:
        return 0

def get_lower_wick(candle):
    if get_candle_direction(candle) > 0:
        return candle[1] - candle[3]
    elif get_candle_direction(candle) < 0:
        return candle[4] - candle[3]

def get_upper_wick(candle):
    if get_candle_direction(candle) > 0:
        return candle[2] - candle[4]
    elif get_candle_direction(candle) < 0:
        return candle[2] - candle[1]

def get_length_of_opposite_wick(candle):
    if get_candle_body(candle) > 0:
        return get_lower_wick(candle)
    elif get_candle_body(candle) < 0:
        return get_upper_wick(candle)
    else:
        return 0
def is_opposite_wick_short_enough(candle):
    return get_length_of_opposite_wick(candle) < 0.05

def is_doji(candle):
    avg_wick = (get_lower_wick(candle) - get_upper_wick(candle)) / 2
    are_wicks_long_enough = get_lower_wick(candle) > get_candle_size(candle) * 0.9 and get_upper_wick(candle) > get_candle_size(candle) * 0.9
    is_body_small = get_candle_size(candle) < avg_wick * 1.1

    return are_wicks_long_enough and is_body_small 

def is_green_no_lower_wick(candle):
    return candle[1] < candle[4] and abs(candle[1] - candle[3]) < 0.05

def is_red_no_upper_wick(candle):
    return candle[1] > candle[4] and abs(candle[2] - candle[1]) < 0.05

def is_doji(candle):
    w1, w2 = 0, 0
    if candle[1] > candle[4]:
        w1 = candle[2] - candle[1]
        w2 = candle[4] - candle[3]
    elif candle[1] < candle[4]:
        w1 = candle[4] - candle[3]
        w2 = candle[2] - candle[1]
    print(w1, w2)
    # checks whether body is smaller than the average wick size and whether the difference between the wicks is smaller than the size of the body
    return abs(candle[1] - candle[4]) < (w1 + w2) / 2 and abs(w1 - w2) < abs(candle[1] - candle[4])

print(is_doji(candle2))