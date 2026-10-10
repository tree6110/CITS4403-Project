################# Grid characteristics #####################
GRID_DIM = 50 # Length of sides of grid.
# Simulate high quality areas around Peppermint Grove, Nedlands, Perth CBD.
# Somewhat reflects property prices/crime rates/proximity to river and sea.
MAX_QUALITY_POINTS = [(5,17), (5,22), (12, 22), (17, 23), (20, 27)]
QUALITY_PRICE_INFLUENCE = 1.2 # Factor by which price increases with each quality level.

################# Household constants #####################
AVERAGE_INCOME = 1865 * 52 
COST_OF_LIVING = 40000

################# Market constants #####################
AVERAGE_HOUSE_PRICE = 524000 # Once scaled, average income is approximately 965000
AVERAGE_RENT = 750 * 52 # For simplicity, rent is not scaled for quality.
PROFIT_MARGIN = 1.5 # Buyers want to sell once house gains 50% of original value.


################## Banking constants #####################

BASE_INTEREST_RATE = 0.046 #Will change between 0.01 and 0.175 in experiments
LOAN_PERIOD = 30 # Average loan period to pay it back
DEPOSIT = 0.2
