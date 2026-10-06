import numpy as np
from matplotlib import pyplot as plt
from classes import Dwelling, Household, Bank, Mortgage
from constants import GRID_DIM
from helpers import getUnoccupiedDwellings, getRentedDwellings, getOwnedDwellings, findHouseToPurchase, findHouseToRent, purchase
from copy import deepcopy
from imageHandling import getNonDwellingCoords

#tbh idk where to put this
bigBank = Bank() 

# TODO: write in a more object-oriented way with a class for each step that stores dwelling and household lists.
def tick(dwellings: list[Dwelling], households: list[Household]) -> tuple[list[Dwelling], list[Household]]:
    
    # Update the interest rates
    bigBank.updateInterestRate()

    # Force some households to exit the market before buying/renting commences.
    for x in households.copy():
    # Chance to exit market.
        if np.random.rand() < 0.1:
            # Move out of occupied home.
            if x.occupying: x.occupying.occupant = None

            #Clear any mortgages associated with exiting houses
            bigBank.activeMortgages = [m for m in bigBank.activeMortgages if m.borrower != x]

            # Return all owned houses to the market and kick all occupants.
            for house in x.owns:
                house.owner = None
                if house.occupant: house.occupant.occupying = None
                house.occupant = None
            # Remove self from household list and instantiate new household to replace.
            households.remove(x)
            households.append(Household())

    # Give all households more money according to their income & process any mortgage payments.
    for x in households:
        x.money += x.income

        for mort in x.mortgages:
            payment = mort.annualPayment()
            x.money -= payment

        # If renting, pay rent.
        if x.occupying and x.occupying.owner != x:
            x.occupying.owner.money += x.occupying.rentPrice
            x.money -= x.occupying.rentPrice

        # Purchase house if household can afford one.
        # Can purchase up to 3 per tick, stop trying to purchace once unsuccessful.
        for i in range(3):
            bestPurchaseOption = findHouseToPurchase(dwellings, x)
            if bestPurchaseOption:
                purchase(x, bestPurchaseOption)
            else:
                break

        # Try to rent if not living anywhere.
        if not x.occupying:
            bestRentOption = findHouseToRent(dwellings, x)
            # TODO: fn
            if bestRentOption:
                bestRentOption.occupant = x
                x.occupying = bestRentOption

    # Return tuple containing modified lists.
    return dwellings, households


def runSimulation(nSteps: int) -> list[tuple[list[Dwelling], list[Household]]]:
    # Calculate coordinates that are water and will not have a dwelling placed on them.
    NO_HOUSE_COORDS = getNonDwellingCoords('data/map.png')
    numHouses = GRID_DIM*GRID_DIM - len(NO_HOUSE_COORDS)
    steps = []
    # Initialise empty dwellings and households.
    currDwellings: list[Dwelling] = []
    currHouseholds: list[Household] = []
    for i in range(GRID_DIM):
        for j in range(GRID_DIM):
            if (i,j) not in NO_HOUSE_COORDS: 
                currDwellings.append(Dwelling((i,j)))

    for i in range(round(0.95*numHouses)):
        currHouseholds.append(Household())

    for i in range(nSteps):
        steps.append((deepcopy(currDwellings), deepcopy(currHouseholds)))
        tick(currDwellings, currHouseholds)
    return steps

def reconstructQualityGrid(dwellings: list[Dwelling]):
    # Adds back in spaces that do not have a dwelling corresponding to them and gets quality for all spaces.
    mapTiles = np.zeros((GRID_DIM, GRID_DIM))
    for dwelling in dwellings:
        i, j = dwelling.coord
        # I have no idea why I need to reverse this here but it seems to work and I want to move on...
        mapTiles[j, i] = dwelling.quality
            
    return mapTiles

def graphSimulation(steps: list[tuple[list[Dwelling], list[Household]]]) -> None:
    
    historicalUnoccupied = []
    historicalRented = []
    historicalOwnerOccupied = []

    qualityGrid = reconstructQualityGrid(steps[0][0])
    fig = plt.figure(figsize=(20, 7), constrained_layout=True)
    a = plt.subplot2grid((3,7), (0,0), rowspan = 3, colspan=3, fig=fig)
    b = plt.subplot2grid((3,7), (0,3), colspan=2, fig=fig)
    c = plt.subplot2grid((3,7), (1,3), colspan=2, fig=fig)
    d = plt.subplot2grid((3,7), (2,3), colspan=2, fig=fig)
    e = plt.subplot2grid((3,7), (0,5), colspan=2, fig=fig)

    for i, (dwellings, households) in enumerate(steps):
        b.clear()
        incomes = list(map(lambda x: x.income, households))
        b.set_title("Income")
        b.hist(incomes, 100, density=True, log=True)

        unoccupiedCoords = list(map(lambda x: x.coord, getUnoccupiedDwellings(dwellings)))
        ownedCoords = list(map(lambda x: x.coord, getOwnedDwellings(dwellings)))
        rentedCoords = list(map(lambda x: x.coord, getRentedDwellings(dwellings)))

        # Save historical data.
        historicalUnoccupied.append(len(unoccupiedCoords))
        historicalRented.append(len(rentedCoords))
        historicalOwnerOccupied.append(len(ownedCoords))
    
        a.clear()
        a.axis([0, GRID_DIM, 0, GRID_DIM])
        a.imshow(qualityGrid)
        xs, ys = zip(*unoccupiedCoords) if unoccupiedCoords else ([], [])
        a.plot(xs, ys, "o", color="red", label=f"Unoccupied ({len(unoccupiedCoords)})")
        xs, ys = zip(*ownedCoords) if ownedCoords else ([], [])
        a.plot(xs, ys, "o", color="blue", label=f"Owner Occupied ({len(ownedCoords)})")
        xs, ys = zip(*rentedCoords) if rentedCoords else ([], [])
        a.plot(xs, ys, "o", color="orange", label=f"Rented ({len(rentedCoords)})")
        a.legend(loc='upper left', bbox_to_anchor=(1.02, 0.5), frameon=False)

        # Plot histogram of houses owned.
        c.clear()
        housesOwned = [len(x.owns) for x in households]
        c.set_title("Houses Owned")
        c.hist(housesOwned, density=True, log=True)

        # Plot histogram of household money.
        e.clear()
        householdMoney = [x.money for x in households]
        e.set_title("Money")
        e.hist(householdMoney, density=True, log=True)

        # Plot historical data.
        d.clear()
        d.set_title("Distribution over time")
        d.plot(historicalUnoccupied, color="red")
        d.plot(historicalRented, color="orange")
        d.plot(historicalOwnerOccupied, color="blue")

        plt.savefig(f"./step{i}")

def main() -> None:
    steps = runSimulation(5)
    graphSimulation(steps)

if __name__ == "__main__":
    main()
