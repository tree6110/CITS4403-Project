from classes import Dwelling, Household

# Find all dwellings for sale.
def getUnoccupiedDwellings(allDwellings: list[Dwelling]) -> list[Dwelling]:
    return list(filter(lambda x: x.occupant == None, allDwellings))


# Find all dwellings lived in by the owner.
def getOwnedDwellings(allDwellings: list[Dwelling]) -> list[Dwelling]:
    return list(filter(lambda x: x.owner and x.occupant and x.occupant == x.owner, allDwellings))


# Find all dwellings lived in by renters.
def getRentedDwellings(allDwellings: list[Dwelling]) -> list[Dwelling]:
    return list(filter(lambda x: x.occupant and x.owner and x.occupant != x.owner, allDwellings))


# Search available houses for the one with the highest quality that can be purchased.
def findHouseToPurchase(allDwellings: list[Dwelling], household: Household) -> Dwelling | None:
    canPurchase = list(filter(lambda x: x.owner == None and x.salePrice <= household.money, allDwellings))
    return sorted(canPurchase, key=lambda x: (-x.quality, x.salePrice))[0] if len(canPurchase) > 0 else None


# Search available houses for the one with the highest quality that can be rented.
def findHouseToRent(allDwellings: list[Dwelling], household: Household):
    canRent = list(filter(lambda x: not x.occupant and x.owner and  x.rentPrice <= household.money, allDwellings))
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
    elif dwelling.quality > household.occupying.quality:
        dwelling.occupant = household
        household.occupying.occupant = None
        household.occupying = dwelling
    # Otherwise, new house goes up for rent.