def slide_distance(start: int, end: int, is_cw: bool = True) -> int:
    """Returns the distance between the start and end buttons. Returns the clockwise distance by default
    unless is_cw is set to False, in which case the counter-clockwise distance is returned.

    Args:
        start: The button where the slide begins. Buttons start at 0.
        end: The button where the slide ends. Buttons start at 0.
        is_cw: Determines if the returned distance is in terms of clockwise or counter-clockwise rotation.
            Defaults to True.
    """
    if is_cw:
        if start >= end:
            end += 8

        return (end - start) % 8

    if start <= end:
        start += 8

    return (start - end) % 8


def slide_is_cw(start_position: int, end_position: int) -> bool:
    """Returns True when the shortest distance between the start and end position is achieved with
    a clockwise rotation. Returns False otherwise.

    Args:
        start_position: The button where the slide begins. Buttons start at 0.
        end_position: The button where the slide ends. Buttons start at 0.

    Raises:
        ValueError: When the distance is 4 places. This is because either rotation produces the same
            distance.
    """
    # Handles slide cases where the direction is not specified
    # Returns True for clockwise and False for counterclockwise
    diff = abs(end_position - start_position)
    other_diff = abs(8 - diff)
    if diff == 4:
        raise ValueError("Can't choose direction for a 180 degree angle.")

    if (end_position > start_position and diff > other_diff) or (
        end_position < start_position and diff < other_diff
    ):
        return False
    else:
        return True
