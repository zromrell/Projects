"""
Modern Portfolio Theory - Mean Variance Optimization
"""
import numpy as np
import datetime as dt
import pandas as pd
from pandas_datareader import data as pdr
import scipy.optimize as sc
import matplotlib.pyplot as plt
import yfinance as yf
yf.pdr_override()


# Import data
def get_data(stock, start, end):
    stockData = pdr.get_data_yahoo(stocks, start, end)
    stockData = stockData['Close']
    returns = stockData.pct_change()
    meanReturns = returns.mean()
    covMatrix = returns.cov()
    return meanReturns, covMatrix



# Computes the performance
def portfolioPerformance(weights, meanReturns, covMatrix):
    returns = np.sum(meanReturns*weights)*252
    std = np.sqrt(np.dot(weights.T, np.dot(covMatrix, weights)))*np.sqrt(252)
    return returns, std





# Sharpe ratio calculator
def negativeSR(weights, meanReturns, covMatrix, riskFreeRate = 0):
    pReturns, pStd = portfolioPerformance(weights, meanReturns, covMatrix)
    return -1*(pReturns-riskFreeRate)/pStd

# Minimizes the negative sharpe ratio (maximizes), by altering the weights of portfolio
def maximizeSR(meanReturns, covMatrix, riskFreeRate = 0, constraintSet=(0,1)):
    args = (meanReturns, covMatrix, riskFreeRate)
    constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
    numAssets = len(meanReturns)
    bounds = tuple(constraintSet for asset in range(numAssets))
    results = sc.minimize(negativeSR, numAssets*[1/numAssets], args=args,method = 'SLSQP', bounds=bounds, constraints=constraints)
    return results





# Returns standard deviation of specific portfolio
def portfolioVariance(weights, meanReturns, covMatrix):
    return portfolioPerformance(weights, meanReturns, covMatrix)[1]

# Minimizes variance by minimizing standard deviation (equivalent computation)
def minimizeVariance(meanReturns, covMatrix, riskFreeRate = 0, constraintSet=(0,1)):
    """Minimize the portfolio varaince by alerting the weights/allocation of assets in the portfolio"""
    args = (meanReturns, covMatrix)
    constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
    numAssets = len(meanReturns)
    bounds = tuple(constraintSet for asset in range(numAssets))
    results = sc.minimize(portfolioVariance, numAssets*[1/numAssets], args=args, method = 'SLSQP', bounds=bounds, constraints=constraints)
    return results





# Returns expected returns of specific portfolio
def portfolioReturns(weights, meanReturns, covMatrix):
        return portfolioPerformance(weights, meanReturns, covMatrix)[0]

# Computes minimal variance of portfolio with return target
def efficientOpt(meanReturns, covMatrix, returnTarget, constraintSet=(0,1)):
    """For each returnTarget we want to optimize portfolio for min variance"""
    args = (meanReturns, covMatrix)
    constraints = ({'type': 'eq', 'fun': lambda x: portfolioReturns(x,  meanReturns, covMatrix) - returnTarget}, {'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    numAssets = len(meanReturns)
    bounds = tuple(constraintSet for asset in range(numAssets))
    effOpt = sc.minimize(portfolioVariance, numAssets*[1/numAssets], args=args, method = 'SLSQP', bounds=bounds, constraints=constraints)
    return effOpt





# Uses functions above to compute portfolio with max sharpe ratio, min volatility, and the efficient frontier
def calculatedResults(meanReturns, covMatrix, riskFreeRate=0, constraintSet=(0,1)):
    # Max Sharpe Ratio Portoflio
    maxSR_Portfolio = maximizeSR(meanReturns, covMatrix)
    maxSR_Returns, maxSR_Std = portfolioPerformance(maxSR_Portfolio['x'], meanReturns, covMatrix)
    maxSR_allocation = pd.DataFrame(maxSR_Portfolio['x'], index=meanReturns.index, columns=['allocation'])
    maxSR_allocation.allocation = [round(i, 3)*100 for i in maxSR_allocation.allocation]

    # Min Volatility Portfolio
    minVol_Portfolio = minimizeVariance(meanReturns, covMatrix)
    minVol_Returns, minVol_Std = portfolioPerformance(minVol_Portfolio['x'], meanReturns, covMatrix)
    minVol_allocation = pd.DataFrame(minVol_Portfolio['x'], index=meanReturns.index, columns=['allocation'])
    minVol_allocation.allocation = [round(i, 3)*100 for i in minVol_allocation.allocation]

    randReturns = []
    randStd = []
    randWeights = []
    for _ in range(5000):
        rw = np.random.rand(len(meanReturns))
        rw /= np.sum(rw)
        rr, rs = portfolioPerformance(rw, meanReturns, covMatrix)
        randReturns.append(round(rr*100, 2))
        randStd.append(round(rs*100,2))
        randWeights.append(rw)
        

    adjustedMean = meanReturns*252
    maxReturns = max(adjustedMean)

    #Efficient Frontier
    efficientList = []
    targetReturns = np.linspace(minVol_Returns, maxReturns, 40)
    for target in targetReturns:
        efficientList.append(round(efficientOpt(meanReturns, covMatrix, target)['fun']*100, 2))

    minReturns = min(adjustedMean)
    lowerHalf = []
    lowerTargetReturns = np.linspace(minReturns, minVol_Returns, 40)
    
    for target in lowerTargetReturns:
        lowerHalf.append(round(efficientOpt(meanReturns, covMatrix, target)['fun']*100, 2))

    targetReturns = np.around(targetReturns*100,2)
    lowerTargetReturns = np.around(lowerTargetReturns*100,2)

    maxSR_Returns, maxSR_Std = round(maxSR_Returns, 3)*100, round(maxSR_Std, 3)*100
    minVol_Returns, minVol_Std = round(minVol_Returns, 3)*100, round(minVol_Std, 3)*100
    
    return (maxSR_Returns, maxSR_Std, maxSR_allocation, minVol_Returns, minVol_Std, minVol_allocation, efficientList, targetReturns, lowerHalf, lowerTargetReturns, randReturns, randStd, randWeights)





# Graphs the results
def EF_graph(meanReturns, covMatrix, riskFreeRate=0, constraintSet=(0,1)):
    maxSR_Returns, maxSR_Std, maxSR_allocation, minVol_Returns, minVol_Std, minVol_allocation, efficientList, targetReturns, lowerHalf, lowerTargetReturns, randReturns, randStd, randWeights = calculatedResults(meanReturns, covMatrix, riskFreeRate=0, constraintSet=(0,1))

    xpoints = np.array([maxSR_Std, minVol_Std])
    ypoints = np.array([maxSR_Returns, minVol_Returns ])
    plt.scatter(xpoints,ypoints,s=8, color = 'gold' )
    
    x1 = efficientList
    y1 = targetReturns
    plt.plot(x1,y1, color='salmon')
    x2 = lowerHalf
    y2 = lowerTargetReturns
    plt.plot(x2,y2, color='salmon', ls = ':')
    

    xpoints1 = np.array(randStd)
    ypoints1 = np.array(randReturns)
    plt.scatter(xpoints1,ypoints1, s = 4, color = 'aqua', marker = '.')
        
    plt.title('Portfolio Optimization with the Efficient Frontier')
    plt.xlabel('Annualized Volatility (%)')
    plt.ylabel('Annualized Return (%)')

    return plt.show()



# List of stocks (tickers from YahooFinance!)
stocks = ['AAPL', 'META', 'NVDA', 'AMZN', 'GOOG', 'NFLX']
# Gets dates for expected returns and covariance matrix
endDate = dt.datetime.now()
startDate = endDate - dt.timedelta(days=365)

# Gets data
meanReturns, covMatrix = get_data(stocks, startDate, endDate)

# graphs
EF_graph(meanReturns, covMatrix)
