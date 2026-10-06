from PIL import Image

from constants import GRID_WIDTH, GRID_HEIGHT
# Constants that it seems weird to move into constants file.
WATER_COLOUR = (181, 208, 208)

def getNonDwellingCoords() -> list[tuple[int, int]]:
    map = Image.open('data/map.png')
    # map.convert('RGB')
    exclude = []
    w, h = map.size

    print(w, h)
    # Force square because I am silly
    minSideLen = min(w,h)
    interval = minSideLen // GRID_WIDTH
    print(interval)
    for i in range(GRID_WIDTH):
        for j in range(GRID_WIDTH):
            # print("looking at pixel", i*interval, j*interval)
            coord = (i*interval, j*interval)
            if map.getpixel(coord) == WATER_COLOUR:
                exclude.append((i,GRID_WIDTH - j))
    print(len(exclude))
    # print(exclude)
    return exclude


