################# Grid characteristics #####################
GRID_DIM = 50 # Length of sides of grid.
# Simulate high quality areas around Peppermint Grove, Nedlands, Perth CBD.
# Somewhat reflects property prices/crime rates/proximity to river and sea.
MAX_QUALITY_POINTS = [(5,17), (5,22), (12, 22), (17, 23), (20, 27)]
QUALITY_PRICE_INFLUENCE = 1.2 # Factor by which price increases with each quality level

################# Household constants #####################
AVERAGE_INCOME = 80000
MAX_INCOME = 5000000

################# Market constants #####################
# Average rent per year.
AVERAGE_HOUSE_PRICE = 800000
AVERAGE_RENT = 0.05*AVERAGE_HOUSE_PRICE

################## Banking constants #####################
BASE_INTEREST_RATE = 0.05
LOAN_PERIOD = 30 #average loan period to pay it back
DEPOSIT = 0.2
