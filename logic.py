import logging
import random

import numpy

from constants import (
    GIF_FLAME_NUM, GIT_REPOSITORY_ROOT_PATH,
)
from errors import InvalidField, InvalidLiteral, InvalidWidthField, InvalidHeightField, InvalidCellState
# Rust が Python の世界で動いてるのうれしい
from game_of_life import Field, get_status  # type: ignore
from gol_gif import gen_gif_and_save  # type: ignore


# public
def gen_random_field(lines):

    if not all([__parse(i) for i in lines[0].split()]):
        raise InvalidLiteral

    width, height = (int(s) for s in lines[0].split())
    random_field = ""
    for i in range(width * height):
        random_state = str(random.choice([0, 1, 1]))
        random_field += random_state
        if (i+1) % width == 0:
            random_field += "\n"

    return width, height, random_field.rstrip()

# public
def gen_and_save_gif_to_repository(lines, user_id):
    width, height = (int(s) for s in lines[0].split())

    cells = [int(s) for s in "".join(lines[1:])]

    length = len(cells)

    if len(lines[1:]) != height and width * height != length:
        raise InvalidField

    if len(lines[1:]) != height:
        raise InvalidHeightField

    # InvalidHeightField の検査を pass したうえで
    # この if 文通れなかったら width が invalid　ってことね
    if width * height != length:
        raise InvalidWidthField
    
    if cells.count(0) + cells.count(1) != length:
        raise InvalidCellState
    
    field = Field(width, height, cells)
    status = get_status(field, GIF_FLAME_NUM)
    width, height, status = __enlarge_field_status(width, height, status)
    gen_gif_and_save(width, height, status, f"{GIT_REPOSITORY_ROOT_PATH}/public/users/{user_id}.gif")
    logging.info(f"save gif to {GIT_REPOSITORY_ROOT_PATH}/public/users/{user_id}.gif successfully")

# private
def __enlarge_field_status(width, height, status):
    status = numpy.array(status)
    x5_status = []
    for state in status:
        x5_state = state.repeat(5, axis=0).repeat(5, axis=1).flatten().tolist()
        x5_status.append(x5_state)
    return width*5, height*5, x5_status

# private
def __parse(s) -> bool:
        try:
            int(s)
        except ValueError:
            return False
        else:
            return True
