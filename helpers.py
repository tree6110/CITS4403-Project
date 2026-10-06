from classes import Dwelling, Household, Bank, Mortgage
from constants import DEPOSIT, BASE_INTEREST_RATE, PROFIT_MARGIN

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
def findHouseToRent(allDwellings: list[Dwelling], household: Household) -> Dwelling | None:
    canRent = list(filter(lambda x: not x.occupant and x.owner and  x.rentPrice <= household.money, allDwellings))
    return sorted(canRent, key=lambda x: (-x.quality, x.rentPrice))[0] if len(canRent) > 0 else None

# Changes house prices based on interest rates
def updateHousePrices(dwellings: list[Dwelling], currentInterestRate: float) -> None:
    rate = 1.0 + (currentInterestRate - BASE_INTEREST_RATE)
    for d in dwellings:
        d.salePrice *= rate 
        d.rentPrice = d.salePrice * 0.05 #Same ratio as in constants.py

# Determines if a household wants to sell
def determineSale(household: Household, dwellings: list[Dwelling]) -> None:
    housesToSell = []

    for house in household.owns.copy():
        #Investment house price is greater than 50% of purchase price
        isInvestment = household.occupying != house
        madeProfit = house.salePrice >= (house.purchasePrice * PROFIT_MARGIN)

        #Household can't afford mortgage payments
        isBroke = household.money < sum(m.annualPayment() for m in household.mortgages) #in case a household has multiple mortgages

        if (isInvestment and madeProfit) or isBroke:
            housesToSell.append(house)

    for house in housesToSell:
        sell(household, house)


def sell(household: Household, dwelling: Dwelling) -> None:
    from model import bigBank

    #Find & clear associated mortgages
    mortgageRemoved = next((m for m in household.mortgages if m.dwelling == dwelling), None)
    if mortgageRemoved:
        household.mortgages.remove(mortgageRemoved)
        if mortgageRemoved in bigBank.activeMortgages:
            bigBang.activeMortgages.remove(mortgageRemoved)
        proceeds = dwelling.salePrice - mortgageRemoved.loanAmount
        household.money += max(0, proceeds) #incase household still owes money
    else:
        household.money += dwelling.salePrice

    #Remove owners
    if dwelling in household.owns:
        household.owns.remove(dwelling)
    dwelling.owner = None

    #If household was occupying the house, they become homeless
    if household.occupying == dwelling:
        household.occupying = None
        dwelling.occupant = None 

def purchase(household: Household, dwelling: Dwelling) -> None:
    from model import bigBank
    
    #Checks if a house is already mortgaged
    for mort in bigBank.activeMortgages:
        if mort.dwelling == dwelling:
            return 

    requiredDeposit = dwelling.salePrice * DEPOSIT

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
        loanAmount = dwelling.salePrice
        newMortgage = Mortgage(household, dwelling, loanAmount, bigBank.interestRate)
        bigBank.activeMortgages.append(newMortgage)
        household.mortgages.append(newMortgage)
    else:
        #Cannot afford regardless
        return

    #Record purchase price for selling profit calculations
    dwelling.purchasePrice = dwelling.salePrice

    # Update owners & occupancy
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