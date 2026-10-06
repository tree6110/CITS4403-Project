import numpy as np
from matplotlib import pyplot as plt
from classes import Dwelling, Household, Bank, Mortgage
from constants import GRID_WIDTH, GRID_LENGTH, PROFIT_MARGIN
from helpers import getUnoccupiedDwellings, getRentedDwellings, getOwnedDwellings, findHouseToPurchase, findHouseToRent, purchase, sell, updateHousePrices, determineSale
from copy import deepcopy



# TODO: write in a more object-oriented way with a class for each step that stores dwelling and household lists.
def tick(dwellings: list[Dwelling], households: list[Household], bank: Bank) -> tuple[list[Dwelling], list[Household], Bank]:
    
    # Update the interest rates
    bank.updateInterestRate()
    # Update the housing prices
    updateHousePrices(dwellings, bank.interestRate)

    # Force some households to exit the market before buying/renting commences.
    for x in households.copy():
    # Chance to exit market.
        if np.random.rand() < 0.1:
            # Move out of occupied home.
            if x.occupying: x.occupying.occupant = None

            #Clear any mortgages associated with exiting houses
            bank.activeMortgages = [m for m in bank.activeMortgages if m.borrower != x]

            # Return all owned houses to the market and kick all occupants.
            for house in x.owns:
                house.owner = None
                if house.occupant: house.occupant.occupying = None
                house.occupant = None
            # Remove self from household list and instantiate new household to replace.
            households.remove(x)
            households.append(Household())

    # Process income, mortgage payments, and rent, then allow households to sell dwellings.
    for x in households:
        x.money += x.income
        for mort in x.mortgages:
            payment = mort.annualPayment()
            x.money -= payment

        # If renting, pay rent.
        if x.occupying and x.occupying.owner != x:
            x.occupying.owner.money += x.occupying.rentPrice
            x.money -= x.occupying.rentPrice

        # Determine if households want to sell houses. Selling of rented houses may make renters homeless.
        # if len(determineSale(x)) > 0: print(len(determineSale(x)))
        for dwelling in determineSale(x): sell(dwelling, bank)
    
    # Allow households to purchase dwellings if they can afford one.
    for x in households:
        # Can purchase up to 3 per tick, stop trying to purchase once unsuccessful.
        for i in range(3):
            bestPurchaseOption = findHouseToPurchase(dwellings, x)
            if bestPurchaseOption:
                purchase(x, bestPurchaseOption, bank)
            else:
                break
    
    # Allow households to rent an unoccupied house owned by someone else if they are not living anywhere else.
    for x in households:
        if not x.occupying:
            bestRentOption = findHouseToRent(dwellings, x)
            if bestRentOption:
                bestRentOption.occupant = x
                x.occupying = bestRentOption

    # Return tuple containing modified lists.
    return dwellings, households, bank


def runSimulation(nSteps: int) -> list[tuple[list[Dwelling], list[Household], Bank]]:
    steps = []
    # Initialise empty dwellings and households.
    currDwellings: list[Dwelling] = []
    currHouseholds: list[Household] = []
    # Initialise bank.
    bigBank = Bank() 
    for i in range(GRID_LENGTH):
        for j in range(GRID_WIDTH):
            currDwellings.append(Dwelling((i,j)))
    for i in range(round(0.95*GRID_WIDTH*GRID_LENGTH)):
        currHouseholds.append(Household())

    for i in range(nSteps):
        steps.append((deepcopy(currDwellings), deepcopy(currHouseholds), deepcopy(bigBank)))
        tick(currDwellings, currHouseholds, bigBank)
    return steps


def graphSimulation(steps: list[tuple[list[Dwelling], list[Household], Bank]]) -> None:
    
    historicalUnoccupied = []
    historicalRented = []
    historicalOwnerOccupied = []
    historicalAvgHousePrice = []

    qualityGrid = list(map(lambda x: x.quality, steps[0][0]))
    qualityGridShaped = (np.array(qualityGrid)).reshape(GRID_LENGTH, GRID_WIDTH)
    fig = plt.figure(figsize=(20, 7), constrained_layout=True)
    a = plt.subplot2grid((3,7), (0,0), rowspan = 3, colspan=3, fig=fig)
    b = plt.subplot2grid((3,7), (0,3), colspan=2, fig=fig)
    c = plt.subplot2grid((3,7), (1,3), colspan=2, fig=fig)
    d = plt.subplot2grid((3,7), (2,3), colspan=2, fig=fig)
    e = plt.subplot2grid((3,7), (0,5), colspan=2, fig=fig)
    f = plt.subplot2grid((3,7), (1,5), colspan=2, fig=fig)

    for i, (dwellings, households, _bank) in enumerate(steps):
        b.clear()
        incomes = list(map(lambda x: x.income, households))
        b.set_title("Income")
        b.hist(incomes, 100, density=True, log=True)

        unoccupiedDwellings = getUnoccupiedDwellings(dwellings)

        unoccupiedCoords = list(map(lambda x: x.coord, unoccupiedDwellings))
        ownedCoords = list(map(lambda x: x.coord, getOwnedDwellings(dwellings)))
        rentedCoords = list(map(lambda x: x.coord, getRentedDwellings(dwellings)))

        # Save historical data.
        historicalUnoccupied.append(len(unoccupiedCoords))
        historicalRented.append(len(rentedCoords))
        historicalOwnerOccupied.append(len(ownedCoords))
        unoccupiedForSale = [x for x in unoccupiedDwellings if x.owner is None]
        historicalAvgHousePrice.append(sum(x.salePrice for x in unoccupiedForSale)/len(unoccupiedForSale))
    
        a.clear()
        a.axis([0, GRID_LENGTH, 0, GRID_WIDTH])
        a.imshow(qualityGridShaped)
        xs, ys = zip(*unoccupiedCoords) if unoccupiedCoords else ([], [])
        a.plot(xs, ys, "o", color="red", label=f"Unoccupied ({len(unoccupiedCoords)})")[0]
        xs, ys = zip(*ownedCoords) if ownedCoords else ([], [])
        a.plot(xs, ys, "o", color="blue", label=f"Owner Occupied ({len(ownedCoords)})")[0]
        xs, ys = zip(*rentedCoords) if rentedCoords else ([], [])
        a.plot(xs, ys, "o", color="orange", label=f"Rented ({len(rentedCoords)})")[0]
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

        f.clear()
        f.set_title("Average house price over time")
        f.plot(historicalAvgHousePrice, color="red")

        plt.savefig(f"./step{i}")

def main() -> None:
    steps = runSimulation(50)
    graphSimulation(steps)

main()