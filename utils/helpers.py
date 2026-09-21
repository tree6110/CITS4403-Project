import numpy as np
from src.model import Dwelling, Household, MAX_QUALITY_POINTS
from typing import Any

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
def getUnoccupiedDwellings(housingGrid: list[Dwelling]) -> list[Dwelling]:
    return list(filter(lambda x: x.occupant == None, housingGrid))

# Find all dwellings lived in by the owner.
def getOwnedDwellings(housingGrid: list[Dwelling]) -> list[Dwelling]:
    return list(filter(lambda x: x.owner and x.occupant and x.occupant == x.owner, housingGrid))

# Find all dwellings lived in by renters.
def getRentedDwellings(housingGrid: list[Dwelling]) -> list[Dwelling]:
    return list(filter(lambda x: x.occupant and x.owner and x.occupant != x.owner, housingGrid))

# Search available houses for the one with the highest quality that can be purchased.
def findHouseToPurchase(housingGrid: list[Dwelling], household: Household) -> Dwelling | None:
    canPurchase = list(filter(lambda x: x.owner == None and x.salePrice <= household.money, housingGrid))
    return sorted(canPurchase, key=lambda x: (-x.quality, x.salePrice))[0] if len(canPurchase) > 0 else None

# Search available houses for the one with the highest quality that can be rented.
def findHouseToRent(housingGrid: list[Dwelling], household: Household):
    canRent = list(filter(lambda x: not x.occupant and x.owner and  x.rentPrice <= household.money, housingGrid))
    return sorted(canRent, key=lambda x: (-x.quality, x.rentPrice))[0] if len(canRent) > 0 else None