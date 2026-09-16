import numpy as np
from matplotlib import pyplot as plt
from typing import Any

# Co-ordinates of points of maximum house quality
MAX_QUALITY_POINTS = [(25,25), (15, 15)]

# Size of grid.
GRID_LENGTH = 50
GRID_WIDTH = 50

# Household constants.
BASE_INCOME = 80000
MAX_INCOME = 5000000

# Market constants.
# Average rent per year.
AVERAGE_HOUSE_PRICE = 1000000
AVERAGE_RENT = 0.2*AVERAGE_HOUSE_PRICE

# Global lists.
housingGrid: list[Dwelling] = []
householdGrid: list[Household] = []

# Class for houses.
class Dwelling:
    def __init__(self, coord : tuple[int, int]):
        self.coord = coord
        self.quality = getDwellingQuality(coord)
        self.occupant : Household | None = None
        self.owner : Household | None = None
        self.rentPrice = AVERAGE_RENT * np.random.uniform(0.5,1.5)
        self.salePrice = AVERAGE_HOUSE_PRICE * np.random.uniform(0.5,1.5)

# Class for households.
class Household:
    def __init__(self):
        # Use pareto distribution to model income.
        # Most people have around base income, a small amount have way more (long tail).
        self.income = BASE_INCOME + np.random.pareto(0.3)
        self.money = 0
        self.occupying = None
        self.owns = []

# Find the distance between two points.
def getDistBetween(p1 : tuple[int, int], p2 : tuple[int, int]) -> np.floating[Any]:
    return np.linalg.norm(np.array(p1) - np.array(p2))

# Find the quality of a dwelling.
def getDwellingQuality(dwellingCoord : tuple[int, int]) -> np.float64:
    # Consider only proximity to closest max quality point.
    minDist = min([getDistBetween(dwellingCoord, p) for p in MAX_QUALITY_POINTS])
    # Split into quality bins.
    bins = np.array([0.0, 2.5, 5.0, 10.0, 15.0, 20.0, 30.0])
    return max(bins) - np.digitize(minDist, bins) + 1

# Find all dwellings for sale.
def getUnoccupiedDwellings() -> list[Dwelling]:
    return list(filter(lambda x: x.occupant == None, housingGrid))

# Find all dwellings lived in by the owner.
def getOwnedDwellings() -> list[Dwelling]:
    return list(filter(lambda x: x.owner and x.occupant and x.occupant == x.owner, housingGrid))

# Find all dwellings lived in by renters.
def getRentedDwellings() -> list[Dwelling]:
    return list(filter(lambda x: x.occupant and x.owner and x.occupant != x.owner, housingGrid))

# Search available houses for the one with the highest quality that can be purchased.
def findHouseToPurchase(household: Household) -> Dwelling | None:
    canPurchase = list(filter(lambda x: x.owner == None and x.salePrice <= household.money, housingGrid))
    return sorted(canPurchase, key=lambda x: (-x.quality, x.salePrice))[0] if len(canPurchase) > 0 else None

# Search available houses for the one with the highest quality that can be rented.
def findHouseToRent(household: Household):
    canRent = list(filter(lambda x: not x.occupant and x.owner and  x.salePrice <= household.money, housingGrid))
    return sorted(canRent, key=lambda x: (-x.quality, x.rentPrice))[0] if len(canRent) > 0 else None

def purchase(household: Household, dwelling: Dwelling):
    household.money = household.money - dwelling.salePrice
    household.owns.append(dwelling)
    dwelling.owner = household
    # If homeless, move into purchased house.
    if not household.occupying:
        dwelling.occupant = household
        household.occupying = dwelling
    # If renting, move into purchased house.
    elif household.occupying not in household.owns:
        household.occupying.occupant = None
        dwelling.occupant = household
        household.occupying = dwelling

    # If new house is nicer, occupy it instead.

    # Otherwise, put new house up for rent.

def tick():
    # Give all households more money according to their income.
    for x in householdGrid:
        x.money += x.income
        # If renting, pay rent.
        if x.occupying and x.occupying.owner != x:
            x.occupying.owner.money += x.occupying.rentPrice
            x.money -= x.occupying.rentPrice

        # Purchase house if household can afford one.
        # Can purchase up to 3 per tick.
        for i in range(3):
            bestPurchaseOption = findHouseToPurchase(x)
            if bestPurchaseOption: purchase(x, bestPurchaseOption)
        # Try to rent if not living anywhere.
        if not x.occupying:
            bestRentOption = findHouseToRent(x)
            # TODO: fn
            if bestRentOption:
                bestRentOption.occupant = x
                x.occupying = bestRentOption




def stepAndPlot(nSteps: int):
    qualityGrid = list(map(lambda x: x.quality, housingGrid))
    qualityGridShaped = (np.array(qualityGrid)).reshape(GRID_LENGTH, GRID_WIDTH)
    fig = plt.figure(figsize=(12, 7), constrained_layout=True)
    a = plt.subplot2grid((3,5), (0,0), rowspan = 3, colspan=3, fig=fig)
    b = plt.subplot2grid((3,5), (0,3), colspan=2, fig=fig)

    incomes = list(map(lambda x: x.income, householdGrid))
    b.hist(incomes, 100, density=True, log=True)

    for i in range(nSteps):
        a.clear()
        # Plot quality background (needs improvement...).
        a.axis([0, GRID_LENGTH, 0, GRID_WIDTH])
        a.imshow(qualityGridShaped)
        unoccupiedCoords = list(map(lambda x: x.coord, getUnoccupiedDwellings()))
        ownedCoords = list(map(lambda x: x.coord, getOwnedDwellings()))
        rentedCoords = list(map(lambda x: x.coord, getRentedDwellings()))
        if unoccupiedCoords:
            xs, ys = zip(*unoccupiedCoords)
            a.plot(xs, ys, 'o', color='red')[0]
        if ownedCoords:
            xs, ys = zip(*ownedCoords)
            a.plot(xs, ys, 'o', color='blue')[0]
        if rentedCoords:
            xs, ys = zip(*rentedCoords)
            a.plot(xs, ys, 'o', color='orange')[0]

        plt.savefig(f"./step{i}")
        tick()

# Initialise grid with a dwelling per cell.
# TODO: change to use np structured arrays.
for i in range(GRID_LENGTH):
    for j in range(GRID_WIDTH):
        housingGrid.append(Dwelling((i,j)))

# Initialise households to occupy dwellings.
# Have 0.95 * no of dwellings so some are left empty.
for i in range(round(0.95*GRID_WIDTH*GRID_LENGTH)):
    householdGrid.append(Household())

stepAndPlot(20)