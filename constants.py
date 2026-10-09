################# Grid characteristics #####################
GRID_DIM = 50 # Length of sides of grid.
# Simulate high quality areas around Peppermint Grove, Nedlands, Perth CBD.
# Somewhat reflects property prices/crime rates/proximity to river and sea.
MAX_QUALITY_POINTS = [(5,17), (5,22), (12, 22), (17, 23), (20, 27)]
QUALITY_PRICE_INFLUENCE = 1.2 # Factor by which price increases with each quality level

################# Household constants #####################
AVERAGE_INCOME = 1865 * 52
MAX_INCOME = 5000000

################# Market constants #####################
# Average rent per year.
AVERAGE_HOUSE_PRICE = 965000
AVERAGE_RENT = 750 * 52
PROFIT_MARGIN = 1.5 # Buyer's want to sell once house gains 50% of original value


################## Banking constants #####################
BASE_INTEREST_RATE = 0.046 #Will change between 0.01 and 0.175 in experiments
LOAN_PERIOD = 30 # Average loan period to pay it back
DEPOSIT = 0.2 #Will be changed to 0.02 in experiments