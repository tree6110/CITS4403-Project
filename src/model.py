import numpy as np
from matplotlib import pyplot as plt
from typing import Any
from utils.helpers import getDwellingQuality, findHouseToRent, findHouseToPurchase, getUnoccupiedDwellings, getRentedDwellings, getOwnedDwellings

# Co-ordinates of points of maximum house quality
MAX_QUALITY_POINTS = [(25,25), (15, 15)]

# Size of grid.
GRID_LENGTH = 50
GRID_WIDTH = 50

# Household constants.
AVERAGE_INCOME = 80000
MAX_INCOME = 5000000

# Market constants.
# Average rent per year.
AVERAGE_HOUSE_PRICE = 800000
AVERAGE_RENT = 0.05*AVERAGE_HOUSE_PRICE

# Banking constants
baseInterestRate = 0.05
loanPeriod = 30 #average loan period to pay it back
deposit = 0.2

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
        # Use lognormal distribution to model income.
        self.income = np.random.lognormal(mean=np.log(AVERAGE_INCOME), sigma=1)
        self.money = 2 * self.income
        self.occupying = None
        self.owns = []
        self.mortgages = [] #Tracks which house has a mortgage (if own multiple)

# Class for Banks
class Bank:
    def __init__(self):
        self.interestRate = baseInterestRate
        self.activeMortgages = []

    #To randomly change the interest rate over the years, similar to a cost of living index
    def updateInterestRate(self):
        self.interestRate += np.random.normal(0, 0.005)

        if self.interestRate < 0.01:
            self.interestRate = 0.01
        elif self.interestRate > 0.2:
            self.interestRate = 0.2

bigBank = Bank()

class Mortgage:
    def __init__(self, borrower: Household, dwelling: Dwelling, loanAmount: float, interestRate: float):
        self.borrower = borrower
        self.dwelling = dwelling
        self.loanAmount = loanAmount
        self.interestRate = interestRate

    def annualPayment(self):
        return (self.loanAmount / loanPeriod) + (self.loanAmount * (1-deposit))


def purchase(household: Household, dwelling: Dwelling):
    #Checks if a house is already mortgaged
    for mort in bigBank.activeMortgages:
        if mort.dwelling == dwelling:
            return 

    requiredDeposit = dwelling.salePrice * deposit

    hasCash = household.money >= dwelling.salePrice
    hasDeposit = household.money >= requiredDeposit

    # Checks to see if a household can leverage an existing property in order to buy a new one (if needed)
    leveragedHouse = None
    if not hasDeposit:
        mortgagedDwellings = {m.dwelling for m in household.mortgages}
        for ownedHouse in household.owns:
            if ownedHouse not in mortgagedDwellings:
                leveragedHouse = ownedHouse
                break

    if hasCash:
        household.money -= dwelling.salePrice
    elif hasDeposit:
        household.money -= requiredDeposit
        loanAmount = dwelling.salePrice - requiredDeposit
        newMortgage = Mortgage(household, dwelling, loanAmount, bigBank.interestRate)
        bigBank.activeMortgages.append(newMortgage)
        household.mortgages.append(newMortgage)
    elif leveragedHouse is not None:
        loanAmount = dwelling.salePrice - requiredDeposit
        newMortgage = Mortgage(household, dwelling, loanAmount, bigBank.interestRate)
        bigBank.activeMortgages.append(newMortgage)
        household.mortgages.append(newMortgage)
    else:
        #Cannot afford regardless
        return

    #Update owners & occupancy
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

def tick():

    #Update the interest rates
    bigBank.updateInterestRate()

    # Force some households to exit the market before buying/renting commences.
    for x in householdGrid.copy():
    # Chance to exit market.
        if np.random.rand() < 0.1:
            # Move out of occupied home.
            if x.occupying: 
                x.occupying.occupant = None

            #Clear any mortgages associated with exiting households
            bigBank.activeMortgages = [m for m in bigBank.activeMortgages if m.borrower != x]

            # Return all owned houses to the market and kick all occupants.
            for house in x.owns:
                house.owner = None
                if house.occupant: 
                    house.occupant.occupying = None
                house.occupant = None
            # Remove self from household list and instantiate new household to replace.
            householdGrid.remove(x)
            householdGrid.append(Household())


    #Process payments and income for households
    for x in householdGrid:
        x.money += x.income

        for mort in x.mortgages:
            payment = mort.annualPayment()
            x.money -= payment

        #If renting, pay rent
        if x.occupying and x.occupying.owner != x:
            if x.occupying.owner:
                x.occupying.owner.money += x.occupying.rentPrice
                x.money -= x.occupying.rentPrice

        # Purchase house if household can afford one.
        # Can purchase up to 3 per tick, stop trying to purchace once unsuccessful.
        for i in range(3):
            bestPurchaseOption = findHouseToPurchase(x, housingGrid)
            if bestPurchaseOption:
                purchase(x, bestPurchaseOption)
            else:
                break

        # Try to rent if not living anywhere.
        if not x.occupying:
            bestRentOption = findHouseToRent(x, housingGrid)
            # TODO: fn
            if bestRentOption:
                bestRentOption.occupant = x
                x.occupying = bestRentOption


def stepAndPlot(nSteps: int):
    historicalUnoccupied = []
    historicalRented = []
    historicalOwnerOccupied = []

    qualityGrid = list(map(lambda x: x.quality, housingGrid))
    qualityGridShaped = (np.array(qualityGrid)).reshape(GRID_LENGTH, GRID_WIDTH)
    fig = plt.figure(figsize=(20, 7), constrained_layout=True)
    a = plt.subplot2grid((3,7), (0,0), rowspan = 3, colspan=3, fig=fig)
    b = plt.subplot2grid((3,7), (0,3), colspan=2, fig=fig)
    c = plt.subplot2grid((3,7), (1,3), colspan=2, fig=fig)
    d = plt.subplot2grid((3,7), (2,3), colspan=2, fig=fig)
    e = plt.subplot2grid((3,7), (0,5), colspan=2, fig=fig)
    
    incomes = list(map(lambda x: x.income, householdGrid))
    b.set_title("Income")
    b.hist(incomes, 100, density=True, log=True)

    for i in range(nSteps):
        unoccupiedCoords = list(map(lambda x: x.coord, getUnoccupiedDwellings(housingGrid)))
        ownedCoords = list(map(lambda x: x.coord, getOwnedDwellings(housingGrid)))
        rentedCoords = list(map(lambda x: x.coord, getRentedDwellings(housingGrid)))

        # Save historical data.
        historicalUnoccupied.append(len(unoccupiedCoords))
        historicalRented.append(len(rentedCoords))
        historicalOwnerOccupied.append(len(ownedCoords))

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
        housesOwned = [len(x.owns) for x in householdGrid]
        c.set_title("Houses Owned")
        c.hist(housesOwned, density=True, log=True)

        # Plot histogram of household money.
        e.clear()
        householdMoney = [x.money for x in householdGrid]
        e.set_title("Money")
        e.hist(householdMoney, density=True, log=True)

        # Plot historical data.
        d.clear()
        d.set_title("Distribution over time")
        d.plot(historicalUnoccupied, color="red")
        d.plot(historicalRented, color="orange")
        d.plot(historicalOwnerOccupied, color="blue")

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

stepAndPlot(50)