from PIL import Image

from constants import GRID_WIDTH, GRID_HEIGHT
# Constants that it seems weird to move into constants file.
WATER_COLOUR = (181, 208, 208)

def getNonDwellingCoords() -> list[tuple[int, int]]:
    map = Image.open('data/map.png')
    map.convert('RGB')
    exclude = []
    w, h = map.size

    # Force square because I am silly
    minSideLen = min(w,h)
    interval = minSideLen // GRID_WIDTH
    for i in range(GRID_WIDTH):
        for j in range(GRID_WIDTH):
            # print("looking at pixel", i*interval, j*interval)
            coord = (i*interval, j*interval)
            coordsToCheck = []
            for x in range(interval):
                for y in range(interval):
                    coordsToCheck.append((coord[0] + x, coord[1] + y))
            isWater = 0
            for coord in coordsToCheck:
                if map.getpixel(coord) == WATER_COLOUR:
                    isWater += 1
            print(isWater)
            if isWater >= len(coordsToCheck)/5:
                exclude.append((i,GRID_WIDTH - j))

            # if map.getpixel(coord) == WATER_COLOUR:
            #     exclude.append((i,GRID_WIDTH - j))
    # print("exclude len is", len(exclude))
    # print(exclude)
    return exclude


            # startingPicCoord = (i*interval, j*interval)
            # waterPixels = 0
            # for i in range(interval):
            #     for j in range(interval):
            #         coord = (startingPicCoord[0] + i, startingPicCoord[1] + j)
            #         if map.getpixel(coord) == WATER_COLOUR:
            #             waterPixels += 1
            # if waterPixels >= (interval**2)/2: exclude.append((i,GRID_WIDTH - j))


