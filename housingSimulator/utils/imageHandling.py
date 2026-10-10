from PIL import Image
from housingSimulator.src.constants import GRID_DIM
# Constants that it seems weird to move into constants file.
WATER_COLOUR = (181, 208, 208)

def getNonDwellingCoords(imagePath: str) -> list[tuple[int, int]]:
    # Given a specific map image and the colour of water, return cells on our corresponding grid that will be water.
    map = Image.open(imagePath)
    exclude = []
    w, h = map.size

    minSideLen = min(w,h)
    interval = minSideLen // GRID_DIM
    for i in range(GRID_DIM):
        for j in range(GRID_DIM):
            coord = (i*interval, j*interval)
            coordsToCheck = []
            isWater = 0
            for x in range(interval):
                for y in range(interval):
                    coordsToCheck.append((coord[0] + x, coord[1] + y))
            for coord in coordsToCheck:
                if map.getpixel(coord) == WATER_COLOUR:
                    isWater += 1
            # If 1/5 of the area corresponding to the map pixel is water, make the pixel water.
            if isWater >= len(coordsToCheck)/5:
                exclude.append((i,GRID_DIM - j))

    return exclude

