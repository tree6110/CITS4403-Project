import numpy as np
from matplotlib import pyplot as plt
from housingSimulator.src.classes import Dwelling, Household, Bank, Mortgage
from housingSimulator.src.constants import GRID_DIM, LOAN_PERIOD, COST_OF_LIVING
from housingSimulator.utils.helpers import (
    getUnoccupiedDwellings,
    getRentedDwellings,
    getOwnedDwellings,
    findHouseToPurchase,
    findHouseToRent,
    purchase,
    updateHousePrices,
    determineSale,
    releaseFromOldOwner,
    putOnMarket,
    adjustMarketPrices,
)
from copy import deepcopy
from housingSimulator.utils.imageHandling import getNonDwellingCoords


# Main function used to compute agent actions over one step of time.
def tick(
    dwellings: list[Dwelling],
    households: list[Household],
    bank: Bank,
    sales: list[float],
) -> tuple[list[Dwelling], list[Household], Bank]:

    # Update the interest rates.
    bank.updateInterestRate()
    # Update the housing prices.
    updateHousePrices(dwellings, bank.interestRate)

    # Force some households to exit the market before buying/renting commences.
    for x in households.copy():
        # Chance to exit market.
        if np.random.rand() < 0.1:
            # Move out of occupied home.
            if x.occupying:
                x.occupying.occupant = None

            # Clear any mortgages associated with exiting houses.
            bank.activeMortgages = [m for m in bank.activeMortgages if m.borrower != x]

            # Return all owned houses to the market and kick all occupants.
            for house in x.owns:
                house.owner = None
                if house.occupant:
                    house.occupant.occupying = None
                house.occupant = None
                house.isOnMarket = True
            # Remove self from household list and instantiate new household to replace.
            households.remove(x)
            households.append(Household())

    # Process income, mortgage payments, and rent, then allow households to sell dwellings.
    for x in households:
        x.money += max(0, x.income - COST_OF_LIVING)
        for mort in x.mortgages.copy():
            payment = mort.annualPayment()
            x.money -= payment

            interestPaid = mort.loanAmount * mort.interestRate
            principalPaid = payment - interestPaid
            mort.loanAmount -= principalPaid
            mort.yearsPaid += 1

            # Remove mortgage from list if fully paid off.
            if mort.loanAmount <= 0:
                x.mortgages.remove(mort)
                if mort in bank.activeMortgages:
                    bank.activeMortgages.remove(mort)

            # If the loan period expires without loan being paid off, bank takes the house.
            elif mort.yearsPaid >= LOAN_PERIOD and mort.loanAmount > 0:
                x.mortgages.remove(mort)
                if mort in bank.activeMortgages:
                    bank.activeMortgages.remove(mort)

                # Bank takes house
                dwelling = mort.dwelling
                if dwelling in x.owns:
                    x.owns.remove(dwelling)

                # Evict occupants.
                if dwelling.occupant:
                    dwelling.occupant.occupying = None
                    dwelling.occupant = None
                dwelling.owner = None
                dwelling.isOnMarket = True

        # If renting, pay rent.
        if x.occupying and x.occupying.owner != x:
            x.occupying.owner.money += x.occupying.rentPrice
            x.money -= x.occupying.rentPrice

        # Adjust price of household's houses on the market that haven't sold.
        adjustMarketPrices(x)
        # Determine if households want to sell houses. Put those to be sold on the market.
        putOnMarket(determineSale(x))

    # Allow households to purchase dwellings if they can afford one.
    for x in households:
        # Can purchase up to 3 per tick, stop trying to purchase once unsuccessful.
        for i in range(10):
            # Guaranteed at least one chance to purchase, but only 80% chance for further purchases after that.
            if i == 0 or np.random.rand() < 0.8:
                bestPurchaseOption = findHouseToPurchase(dwellings, x)
                if bestPurchaseOption:
                    releaseFromOldOwner(bestPurchaseOption, bank)
                    purchase(x, bestPurchaseOption, bank)
                    sales.append(bestPurchaseOption.salePrice)
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


# Runs the simulation for n steps, producing a list of steps.
def runSimulation(
    nSteps: int,
) -> list[tuple[list[Dwelling], list[Household], Bank, list[float]]]:
    # Calculate coordinates that are water and will not have a dwelling placed on them.
    NO_HOUSE_COORDS = getNonDwellingCoords("../data/map.png")
    numHouses = GRID_DIM * GRID_DIM - len(NO_HOUSE_COORDS)
    steps = []
    # Initialise empty dwellings and households.
    currDwellings: list[Dwelling] = []
    currHouseholds: list[Household] = []
    currSales: list[float] = []
    # Initialise bank.
    bigBank = Bank()
    for i in range(GRID_DIM):
        for j in range(GRID_DIM):
            if (i, j) not in NO_HOUSE_COORDS:
                currDwellings.append(Dwelling((i, j)))

    for i in range(round(0.95 * numHouses)):
        currHouseholds.append(Household())

    for i in range(nSteps):
        steps.append(
            (
                deepcopy(currDwellings),
                deepcopy(currHouseholds),
                deepcopy(bigBank),
                deepcopy(currSales),
            )
        )
        currSales = []
        tick(currDwellings, currHouseholds, bigBank, currSales)
    return steps


def reconstructQualityGrid(dwellings: list[Dwelling]):
    # Adds back in spaces that do not have a dwelling corresponding to them and gets quality for all spaces.
    mapTiles = np.zeros((GRID_DIM, GRID_DIM))
    for dwelling in dwellings:
        i, j = dwelling.coord
        # I have no idea why I need to reverse this here but it seems to work and I want to move on...
        mapTiles[j, i] = dwelling.quality
    return mapTiles


def graphSimulation(
    steps: list[tuple[list[Dwelling], list[Household], Bank, list[float]]],
) -> None:

    historicalUnoccupied = []
    historicalRented = []
    historicalOwnerOccupied = []
    historicalAvgHousePrice: list[float] = []
    historicalAvgHouseListings: list[float] = []

    qualityGrid = reconstructQualityGrid(steps[0][0])
    fig = plt.figure(figsize=(20, 7), constrained_layout=True)
    a = plt.subplot2grid((3, 7), (0, 0), rowspan=3, colspan=3, fig=fig)
    b = plt.subplot2grid((3, 7), (0, 3), colspan=2, fig=fig)
    c = plt.subplot2grid((3, 7), (1, 3), colspan=2, fig=fig)
    d = plt.subplot2grid((3, 7), (2, 3), colspan=2, fig=fig)
    e = plt.subplot2grid((3, 7), (0, 5), colspan=2, fig=fig)
    f = plt.subplot2grid((3, 7), (1, 5), colspan=2, fig=fig)

    for i, (dwellings, households, _bank, sales) in enumerate(steps):
        b.clear()
        incomes = [x.income for x in households]
        b.set_title("Income")
        b.hist(incomes, 100, density=True, log=True)

        unoccupiedDwellings = getUnoccupiedDwellings(dwellings)

        unoccupiedCoords = [x.coord for x in unoccupiedDwellings]
        ownedCoords = [x.coord for x in getOwnedDwellings(dwellings)]
        rentedCoords = [x.coord for x in getRentedDwellings(dwellings)]

        # Save historical data.
        historicalUnoccupied.append(len(unoccupiedCoords))
        historicalRented.append(len(rentedCoords))
        historicalOwnerOccupied.append(len(ownedCoords))
        unoccupiedForSale = [x for x in unoccupiedDwellings if x.owner is None]
        historicalAvgHouseListings.append(
            historicalAvgHouseListings[-1]
            if not unoccupiedForSale
            else sum(x.salePrice for x in unoccupiedForSale) / len(unoccupiedForSale)
        )
        historicalAvgHousePrice.append(sum(sales) / len(sales) if sales else 0)

        a.clear()
        a.axis([0, GRID_DIM, 0, GRID_DIM])
        a.imshow(qualityGrid)
        xs, ys = zip(*unoccupiedCoords) if unoccupiedCoords else ([], [])
        a.plot(xs, ys, "o", color="red", label=f"Unoccupied ({len(unoccupiedCoords)})")
        xs, ys = zip(*ownedCoords) if ownedCoords else ([], [])
        a.plot(xs, ys, "o", color="blue", label=f"Owner Occupied ({len(ownedCoords)})")
        xs, ys = zip(*rentedCoords) if rentedCoords else ([], [])
        a.plot(xs, ys, "o", color="orange", label=f"Rented ({len(rentedCoords)})")
        a.legend(loc="upper left", bbox_to_anchor=(1.02, 0.5), frameon=False)

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
        f.plot(historicalAvgHouseListings, color="red")

        plt.savefig(f"./results/step{i}")
       

def main() -> None:
    steps = runSimulation(20)
    graphSimulation(steps)


if __name__ == "__main__":
    main()
