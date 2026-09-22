import numpy as np
from typing import Any
from constants import AVERAGE_RENT, AVERAGE_HOUSE_PRICE, AVERAGE_INCOME, MAX_QUALITY_POINTS

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
        # Use lognormal distribution to model income.
        self.income = np.random.lognormal(mean=np.log(AVERAGE_INCOME), sigma=1)
        self.money = 2 * self.income
        self.occupying = None
        self.owns = []

################# Functions for initialisation of objects #####################

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