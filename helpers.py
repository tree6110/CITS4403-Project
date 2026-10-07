from classes import Dwelling, Household, Mortgage, Bank
from constants import DEPOSIT, BASE_INTEREST_RATE, PROFIT_MARGIN, RENT_PORTION_OF_PRICE
import random

# Find all unoccupied dwellings.
def getUnoccupiedDwellings(allDwellings: list[Dwelling]) -> list[Dwelling]:
    return list(filter(lambda x: x.occupant == None, allDwellings))


# Find all dwellings lived in by the owner.
def getOwnedDwellings(allDwellings: list[Dwelling]) -> list[Dwelling]:
    return list(filter(lambda x: x.owner and x.occupant and x.occupant == x.owner, allDwellings))


# Find all dwellings lived in by renters.
def getRentedDwellings(allDwellings: list[Dwelling]) -> list[Dwelling]:
    return list(filter(lambda x: x.occupant and x.owner and x.occupant != x.owner, allDwellings))


# Find all dwellings the owners have listed as for sale.
def getOnMarketDwellings(allDwellings: list[Dwelling]) -> list[Dwelling]:
    return list(filter(lambda x: x.isOnMarket, allDwellings))


# Search available houses for the one with the highest quality that can be purchased.
def findHouseToPurchase(allDwellings: list[Dwelling], household: Household) -> Dwelling | None:
    # canPurchase = list(filter(lambda x: x.isOnMarket and (x.salePrice <= household.money or x.salePrice*DEPOSIT <= household.money), allDwellings))
    canPurchase = list(filter(lambda x: x.isOnMarket and not x.owner == household and (x.salePrice <= household.money or x.salePrice*DEPOSIT <= household.money), allDwellings))
    # If purchasing investment property, pick randomly.
    if household.owns:
        return random.choice(canPurchase) if canPurchase else None
    # Otherwise, prioritise quality. 
    return sorted(canPurchase, key=lambda x: (-x.quality, x.salePrice))[0] if len(canPurchase) > 0 else None


# Search available houses for the one with the highest quality that can be rented.
def findHouseToRent(allDwellings: list[Dwelling], household: Household) -> Dwelling | None:
    canRent = list(filter(lambda x: not x.occupant and x.owner and  x.rentPrice <= household.money, allDwellings))
    return sorted(canRent, key=lambda x: (-x.quality, x.rentPrice))[0] if len(canRent) > 0 else None


# Changes house prices based on interest rates.
def updateHousePrices(dwellings: list[Dwelling], currentInterestRate: float) -> None:
    rate = 1.0 + (currentInterestRate - BASE_INTEREST_RATE)
    for d in dwellings:
        d.salePrice *= rate 
        d.rentPrice = d.salePrice * RENT_PORTION_OF_PRICE


# Determines if a household wants to sell.
def determineSale(household: Household) -> list[Dwelling]:
    housesToSell = []

    for house in household.owns.copy():
        # Investment house price is greater than 50% of purchase price
        isInvestment = household.occupying != house
        madeProfit = house.salePrice >= (house.purchasePrice * PROFIT_MARGIN)

        #Household can't afford mortgage payments
        isBroke = household.money < sum(m.annualPayment() for m in household.mortgages) #in case a household has multiple mortgages

        if (isInvestment and madeProfit) or isBroke:
            housesToSell.append(house)
        
    return(housesToSell)


def putOnMarket(dwellings: list[Dwelling]) -> None:
    for dwelling in dwellings:
        dwelling.isOnMarket = True


def adjustMarketPrices(household: Household) -> None:
    # If this house was already on the market and didn't sell, adjust it's price down by 10%
    for dwelling in household.owns:
        if dwelling.isOnMarket:
            if dwelling.salePrice >= 0.8 * dwelling.purchasePrice:
                dwelling.salePrice = dwelling.salePrice * 0.9
                dwelling.rentPrice = dwelling.salePrice * RENT_PORTION_OF_PRICE
            else:
                dwelling.isOnMarket = False



def releaseFromOldOwner(dwelling: Dwelling, bank: Bank) -> None:
    # If dwelling has an existing owner.
    if dwelling.owner:
        oldOwner = dwelling.owner
        # Find & clear associated mortgages.
        mortgageRemoved = next((m for m in oldOwner.mortgages if m.dwelling == dwelling), None)
        if mortgageRemoved:
            oldOwner.mortgages.remove(mortgageRemoved)
            if mortgageRemoved in bank.activeMortgages:
                bank.activeMortgages.remove(mortgageRemoved)
            proceeds = dwelling.salePrice - mortgageRemoved.loanAmount
            oldOwner.money += max(0, proceeds) # Incase household still owes money
        else:
            oldOwner.money += dwelling.salePrice

        # Remove owners.
        if dwelling in oldOwner.owns:
            oldOwner.owns.remove(dwelling)
        dwelling.owner = None

        # Those living in the house now become homeless.
        if dwelling.occupant:
            dwelling.occupant.occupying = None
            dwelling.occupant = None


def purchase(household: Household, dwelling: Dwelling, bank: Bank) -> None:
    # Take house off the market
    dwelling.isOnMarket = False
    
    # Checks if a house is already mortgaged
    for mort in bank.activeMortgages:
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
        newMortgage = Mortgage(household, dwelling, loanAmount, bank.interestRate)
        bank.activeMortgages.append(newMortgage)
        household.mortgages.append(newMortgage)
    elif leveragedHouse is not None:
        loanAmount = dwelling.salePrice
        newMortgage = Mortgage(household, dwelling, loanAmount, bank.interestRate)
        bank.activeMortgages.append(newMortgage)
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