
import numpy as np
import matplotlib.pyplot as plt
from typing import Any

# Co-ordinates of points of maximum house quality
MAX_QUALITY_POINTS = [(25,25), (15, 15)]

# Size of grid.
GRID_LENGTH = 30
GRID_WIDTH = 30

# Household constants.
AVERAGE_INCOME = 50000

# Market constants.
# Average rent per year.
AVERAGE_RENT = 20000
# Average price to buy a house.
AVERAGE_PRICE = 200000

# Global lists.
housingGrid: list[Dwelling] = []
householdGrid: list[Household] = []

# Class for houses.
class Dwelling:
    def __init__(self, coord : tuple[int, int]):
        self.coord = coord
        self.quality = getDwellingQuality(coord)
        self.occupancy = None # None / "rented" / "owned"
        self.rentPrice = AVERAGE_RENT * np.random.uniform(0.8,1.2)
        self.salePrice = AVERAGE_PRICE * np.random.uniform(0.8,1.2)

# Class for households.
class Household:
    def __init__(self):
        self.income = AVERAGE_INCOME * np.random.uniform(0.5,1.5)
        self.money = 0
        self.occupying = None

# Find the distance between two points.
def getDistBetween(p1 : tuple[int, int], p2 : tuple[int, int]) -> np.floating[Any]:
    return np.linalg.norm(np.array(p1) - np.array(p2))

# Find the quality of a dwelling.
def getDwellingQuality(dwellingCoord : tuple[int, int]) -> np.float64:
    # Consider only proximity to closest max quality point.
    minDist = min([getDistBetween(dwellingCoord, p) for p in MAX_QUALITY_POINTS])
    # Split into 5 quality bins.
    bins = np.array([0.0, 2.0, 4.0, 8.0, 16.0])
    return max(bins) - np.digitize(minDist, bins)

# Find all unoccupied dwellings.
def getUnoccupiedDwellings() -> list[Dwelling]:
    return list(filter(lambda x: x.occupancy == None, housingGrid))

# Find all owned dwellings.
def getOwnedDwellings() -> list[Dwelling]:
    return list(filter(lambda x: x.occupancy == "owned", housingGrid))

# Search the all available houses for the one with the highest quality that can be purchased.
# TODO: allow households to get loans so they don't have to purchase outright
def findHousesToPurchase(household: Household) -> Dwelling | None:
    canPurchase = list(filter(lambda x: x.occupancy == None and x.salePrice <= household.money, housingGrid))
    return sorted(canPurchase, key=lambda x: (-x.quality, x.salePrice))[0] if len(canPurchase) > 0 else None

def purchase(household: Household, dwelling: Dwelling):
    household.money = household.money - dwelling.salePrice
    dwelling.occupancy = "owned"
    household.occupying = dwelling

def tick():
    # Give all households more money according to their income.
    for x in householdGrid:
        x.money += x.income
        # Purchase house if household can afford one
        bestPurchaseOption = findHousesToPurchase(x)
        if bestPurchaseOption: purchase(x, bestPurchaseOption)

def stepAndPlot(nSteps: int):
    qualityGrid = list(map(lambda x: x.quality, housingGrid))
    qualityGridShaped = (np.array(qualityGrid)).reshape(GRID_LENGTH, GRID_WIDTH)
    for i in range(nSteps):
        # Plot quality background (needs improvement...).
        plt.axis([0, GRID_LENGTH, 0, GRID_WIDTH])
        plt.imshow(qualityGridShaped)
        # Plot unoccupied dwellings.
        unoccupiedCoords = list(map(lambda x: x.coord, getUnoccupiedDwellings()))
        if unoccupiedCoords:
            xs, ys = zip(*unoccupiedCoords)
            plt.plot(xs, ys, '.', color='red')[0]
        ownedCoords = list(map(lambda x: x.coord, getOwnedDwellings()))
        if ownedCoords:
            ys, xs = zip(*ownedCoords)
            plt.plot(xs, ys, '.', color='blue')[0]
        # Plot 
        plt.savefig(f"./step{i}")
        tick()

# Initialise grid with a dwelling per cell.
# TODO: change to use np structured arrays.
for i in range(GRID_LENGTH):
    for j in range(GRID_WIDTH):
        housingGrid.append(Dwelling((i,j)))

# Initialise households to occupy dwellings.
# Have 0.8 * no of dwellings so some are left empty.
for i in range(round(0.8*GRID_WIDTH*GRID_LENGTH)):
    householdGrid.append(Household())

stepAndPlot(10)