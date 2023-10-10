import time
import math
import pandas as pd
import numpy as np
import datetime as dt
import scipy.stats as stats
import matplotlib.pyplot as plt
from py_vollib.black_scholes import black_scholes as bs

# Initial Parameters
S0 = 100          # stock price
K = 98            # strike price
H = 200           # barrier value (for barrier options)
vol = 0.20        # volatility (%)
r = 0.03          # risk-free rate (%)
N = 10            # time steps  #With a closed form solution you do not need to increase time steps  #With more complex SDE you need to approximate with the use of time steps
M = 1000          # number of simulations
optiontype = 'c'  # option type 'c' or 'p'
T = 0.5           # duration of option (years)


# Alternate way of getting time
#T = ((dt.date(2022,3,17)-dt.date(2022,1,17)).days+1)/365  



# Monte Carlo Method (assuming asset price behaves with respect to Geometric Brownian Motion (GBM))
def monteCarlo(S0, K, vol, r, T, N, M, optiontype):
    start_time = time.time() # computation speed purposes

    # natural logarithm simulation (arithmetic brownian motion ~ Normally distributed)
    dt = T/N
    mudt = (r - 0.5*(vol**2))*dt # drift term, if you include dividends => (r - div - 0.5*(vol**2))*dt
    volstd = vol*np.sqrt(dt) # diffusion term
    lnS0 = np.log(S0) # natural log of S0

    # generates random increments for diffusion term
    Z = np.random.normal(size=(N,M))
    # arithmetic brownian motion SDE
    dlnSt = mudt + volstd*Z
    
    # compute stock price over time and concatenate initial price to front
    lnST = lnS0 + np.cumsum(dlnSt, axis=0)
    lnST = np.concatenate((np.full(shape=(1,M), fill_value=lnS0), lnST))

    # Renormalize stock price at time T
    ST = np.exp(lnST)
    
    if (optiontype == 'c'):
        CT = np.maximum(0, ST - K)
        optionString = "Call"
    else:
        CT = np.maximum(0, K - ST)
        optionString = "Put"

    # Price of option is discounted average payoff
    C0 = np.exp(-r*T)*np.sum(CT[-1])/M 

    # Standard Deviation of payoffs
    sigma = np.sqrt(np.sum((np.exp(-r*T)*CT[-1] - C0)**2) / (M-1))     
    # Standard error (sample standard deviation)
    SE = sigma/np.sqrt(M)

    mc_time = time.time() - start_time # get computation time

    print("Traditional Monte Carlo (no-optimizations)")
    print(optionString + " value is ${0} with SE +/- {1}".format(np.round(C0,2), np.round(SE,4)))
    print("Computation time is: ", round(mc_time,4))
    print("\n")
    
    return (C0, SE)

#C0, SE = monteCarlo(S0, K, vol, r, T, N, M, optiontype)





# Antithetic Variates Optimization for Monte Carlo Simulation (assuming asset price behaves with respect to Geometric Brownian Motino (GBM))
def monteCarlo_antithetic_variates(S0, K, vol, r, T, N, M, optiontype):
    start_time = time.time() # computation speed purposes

    # natural logarithm simulation (arithmetic brownian motion ~ Normally distributed)
    dt = T/N 
    mudt = (r - 0.5*(vol**2))*dt # drift term, if you include dividends => (r - div - 0.5*(vol**2))*dt
    volstd = vol*np.sqrt(dt)  # diffusion term
    lnS0 = np.log(S0) # natural log of S0

    # generates random increments for diffusion term
    Z = np.random.normal(size=(N,M))
    # arithmetic brownian motion SDE's
    dlnSt1 = mudt + volstd*Z
    dlnSt2 = mudt - volstd*Z

    # compute stock price over time and concatenate initial price to front
    lnSt1 = lnS0 + np.cumsum(dlnSt1, axis=0)
    lnSt2 = lnS0 + np.cumsum(dlnSt2, axis=0)
    lnSt1 = np.concatenate((np.full(shape=(1,M), fill_value=lnS0), lnSt1))
    lnSt2 = np.concatenate((np.full(shape=(1,M), fill_value=lnS0), lnSt2))

    # Renormalize stock price sequences and get price at time T
    ST1 = np.exp(lnSt1)[-1] 
    ST2 = np.exp(lnSt2)[-1] 

    if (optiontype == 'c'):
        CT = 0.5*(np.maximum(0, ST1 - K) + np.maximum(0, ST2 - K))
        optionString = "Call"
    else:
        CT = 0.5*(np.maximum(0, K - ST1) + np.maximum(0, K - ST2))
        optionString = "Put"
        
    # Price of option is discounted average payoff
    C0 = np.exp(-r*T)*np.sum(CT)/M 

    # Standard Deviation of payoffs
    sigma = np.sqrt(np.sum((np.exp(-r*T)*CT - C0)**2) / (M-1))
    # Standard error (sample standard deviation)
    SE = sigma/np.sqrt(M)

    mc_time_av = time.time() - start_time # get computation time

    print("Antithetic Variates Optimization")
    print(optionString + " value is ${0} with SE +/- {1}".format(np.round(C0,2), np.round(SE,4)))
    print("Computation time is: ", round(mc_time_av,4))
    print("\n")
    
    return (C0,SE)

#C0_av, SE_av = monteCarlo_antithetic_variates(S0, K, vol, r, T, N, M, optiontype)





# Computes the delta hedge of a given option contract
def delta_calc(S0, K, vol, r, T, optiontype):
    d1 = (np.log(S0/K) + (r + 0.5*vol**2)*(T))/(vol*np.sqrt(T))
    if (optiontype == 'c'):
        delta_val = stats.norm.cdf(d1, 0, 1)
    elif (optiontype == 'p'):
        delta_val =  -stats.norm.cdf(-d1, 0, 1)
    return delta_val





# Delta Control Variates Optimization for Monte Carlo Simulation (assuming asset price behaves with respect to Geometric Brownian Motino (GBM))
def monteCarlo_delta_control_variates(S0, K, vol, r, T, N, M, optiontype):
    start_time = time.time() # computation speed purposes

    # natural logarithm simulation (arithmetic brownian motion ~ Normally distributed)
    dt = T/N 
    mudt = (r - 0.5*(vol**2))*dt # drift term, if you include dividends => (r - div - 0.5*(vol**2))*dt
    volstd = vol*np.sqrt(dt) # diffusion term
    erdt = np.exp(r*dt) # forward factor

    cv1 = 0
    beta = -1 # need to confirm same delta regardless of option type

    # generates random increments for diffusion term
    Z = np.random.normal(size=(N,M))

    # compute stock price over time and concatenate initial price to front
    St = S0*np.cumprod(np.exp(mudt + volstd*Z), axis=0)
    St = np.concatenate((np.full(shape=(1,M), fill_value=S0), St))

    # compute delta hedge for each timestep (except for last) (transpose then untranspose)
    deltaSt = delta_calc(St[:-1].T, K, vol, r, np.linspace(T,dt,N), optiontype).T

    # compute summation of hedge payoffs
    cv1 = np.cumsum(deltaSt*(St[1:]-St[:-1]*erdt), axis = 0)

    # compute payoff using relationship between option payoff and summation of delta hedges
    if (optiontype == 'c'):
        CT = np.maximum(0, St[-1] - K) + beta*cv1[-1]
        optionString = "Call"
    else:
        CT = np.maximum(0, K - St[-1]) + beta*cv1[-1]
        optionString = "Put"

    # Price of option is discounted average payoff
    C0 = np.exp(-r*T)*np.sum(CT)/M

    # Standard Deviation of payoffs
    sigma = np.sqrt(np.sum((np.exp(-r*T)*CT - C0)**2) / (M-1)) 
    # Standard error (sample standard deviation)
    SE = sigma/np.sqrt(M)

    mc_time_cv1 = time.time() - start_time # get computation time

    print("Delta Control Variates Optimization")
    print(optionString + " value is ${0} with SE +/- {1}".format(np.round(C0,2), np.round(SE,4)))
    print("Computation time is: ", round(mc_time_cv1,4))
    print("\n")

    return (C0,SE)

#C0_cv1, SE_cv1 = monteCarlo_delta_control_variates(S0, K, vol, r, T, N, M, optiontype)





def gamma_calc(S0, K, vol, r, T):
    d1 = (np.log(S0/K) + (r + 0.5*vol**2)*(T))/(vol*np.sqrt(T))
    gamma_val = stats.norm.pdf(d1, 0, 1)/ (S0*vol*np.sqrt(T))
    return gamma_val





# **demonstration it does not work on its own** Gamma Control Variates Optimization for Monte Carlo Simulation (assuming asset price behaves with respect to Geometric Brownian Motino (GBM)) 
def monteCarlo_gamma_control_variates(S0, K, vol, r, T, N, M, optiontype):
    start_time = time.time() # computation speed purposes

    # natural logarithm simulation (arithmetic brownian motion ~ Normally distributed)
    dt = T/N
    mudt = (r - 0.5*(vol**2))*dt # drift term, if you include dividends => (r - div - 0.5*(vol**2))*dt
    volstd = vol*np.sqrt(dt) # diffusion term
    erdt = np.exp(r*dt) # forward factor
    ergamma = np.exp((2*r + vol**2)*dt) - 2*erdt + 1 # expectation of gamma

    cv2 = 0
    beta2 = -0.5 # need to confirm same delta regardless of option type
    
    # generates random increments for diffusion term
    Z = np.random.normal(size=(N,M))
    
    # compute stock price over time and concatenate initial price to front
    St = S0*np.cumprod(np.exp(mudt + volstd*Z), axis=0)
    St = np.concatenate((np.full(shape=(1,M), fill_value=S0), St))

    # compute gamma hedge for each timestep (except for last) (transpose then untranspose)
    gammaSt = gamma_calc(St[:-1].T, K, vol, r, np.linspace(T,dt,N)).T
    
    # compute summation of hedge payoffs
    cv2 = np.cumsum(gammaSt*((St[1:]-St[:-1])**2 - ergamma*(St[:-1]**2)), axis = 0)


    # compute payoff using relationship between option payoff and summation of gamma hedges
    if (optiontype == 'c'):
        CT = np.maximum(0, St[-1] - K) + beta2*cv2[-1]
        optionString = "Call"
    else:
        CT = np.maximum(0, K - St[-1]) + beta2*cv2[-1]
        optionString = "Put"

    # Price of option is discounted average payoff
    C0 = np.exp(-r*T)*np.sum(CT)/M

    # Standard Deviation of payoffs
    sigma = np.sqrt(np.sum( (np.exp(-r*T)*CT - C0)**2) / (M-1)) #sd of payoff paths
    # Standard error (sample standard deviation)
    SE = sigma/np.sqrt(M)

    mc_time_cv2 = time.time() - start_time # get computation time

    print("Gamma Control Variates Optimization")
    print(optionString + " value is ${0} with SE +/- {1}".format(np.round(C0,2), np.round(SE,4)))
    print("Computation time is: ", round(mc_time_cv2,4))
    print("\n")
    
    return (C0,SE)

#C0_cv2, SE_cv2 = monteCarlo_gamma_control_variates(S0, K, vol, r, T, N, M, optiontype)





# Antithetic and Delta Control Variates Optimization for Monte Carlo Simulation (assuming asset price behaves with respect to Geometric Brownian Motino (GBM))
def monteCarlo_antithetic_and_delta(S0, K, vol, r, T, N, M, optiontype):
    start_time = time.time() # computation speed purposes

    # natural logarithm simulation (arithmetic brownian motion ~ Normally distributed)
    dt = T/N
    mudt = (r - 0.5*(vol**2))*dt # drift term, if you include dividends => (r - div - 0.5*(vol**2))*dt
    volstd = vol*np.sqrt(dt) # diffusion term
    erdt = np.exp(r*dt) # forward factor

    cv1 = 0
    beta = -1 # confirm

    # generates random increments for diffusion term
    Z = np.random.normal(size=(N,M))
    
    # compute stock price over time and concatenate initial price to front
    St1 = S0*np.cumprod(np.exp(mudt + volstd*Z), axis=0)
    St2 = S0*np.cumprod(np.exp(mudt - volstd*Z), axis=0)
    St1 = np.concatenate((np.full(shape=(1,M), fill_value=S0), St1))
    St2 = np.concatenate((np.full(shape=(1,M), fill_value=S0), St2))

    
    # compute delta hedge for each timestep (except for last) (transpose then untranspose)
    deltaSt1 = delta_calc(St1[:-1].T, K, vol, r, np.linspace(T,dt,N), optiontype).T
    deltaSt2 = delta_calc(St2[:-1].T, K, vol, r, np.linspace(T,dt,N), optiontype).T
    
    # compute summation of hedge payoffs
    cv1_1 = np.cumsum(deltaSt1*(St1[1:]-St1[:-1]*erdt), axis = 0)
    cv1_2 = np.cumsum(deltaSt2*(St2[1:]-St2[:-1]*erdt), axis = 0)

    # compute payoff using relationship between option payoff and summation of delta hedges
    if (optiontype == 'c'):
        CT = 0.5*(np.maximum(0, St1[-1] - K) + beta*cv1_1[-1] + np.maximum(0, St2[-1] - K) + beta*cv1_2[-1])
        optionString = "Call"
    else:
        CT = 0.5*(np.maximum(0, K - St1[-1]) + beta*cv1_1[-1] + np.maximum(0, K - St2[-1]) + beta*cv1_2[-1])
        optionString = "Put"

    # Price of option is discounted average payoff
    C0 = np.exp(-r*T)*np.sum(CT)/M

    # Standard Deviation of payoffs
    sigma = np.sqrt(np.sum( (np.exp(-r*T)*CT - C0)**2) / (M-1)) #sd of payoff paths
    # Standard error (sample standard deviation)
    SE = sigma/np.sqrt(M)
    
    mc_time_adv = time.time() - start_time # get computation time

    print("Antithetic and Delta Control Variates Optimization")
    print(optionString + " value is ${0} with SE +/- {1}".format(np.round(C0,2), np.round(SE,4)))
    print("Computation time is: ", round(mc_time_adv,4))
    print("\n")
    
    return (C0,SE)

#C0_adv, SE_adv = monteCarlo_antithetic_and_delta(S0, K, vol, r, T, N, M, optiontype)





# Antithetic, Delta, and Gamma Control Variates Optimization for Monte Carlo Simulation (assuming asset price behaves with respect to Geometric Brownian Motino (GBM))
def monteCarlo_antithetic_delta_and_gamma(S0, K, vol, r, T, N, M, optiontype):
    start_time = time.time() # computation speed purposes

    # natural logarithm simulation (arithmetic brownian motion ~ Normally distributed)
    dt = T/N 
    mudt = (r - 0.5*(vol**2))*dt # drift term, if you include dividends => (r - div - 0.5*(vol**2))*dt
    volstd = vol*np.sqrt(dt) # diffusion term
    erdt = np.exp(r*dt) # forward factor
    ergamma = np.exp((2*r + vol**2)*dt) - 2*erdt + 1 # expectation of gamma
    
    cv1 = 0
    cv2 = 0
    beta1 = -1
    beta2 = -0.5

    # generates random increments for diffusion term
    Z = np.random.normal(size=(N,M))
    
    # compute stock price over time and concatenate initial price to front
    St1 = S0*np.cumprod(np.exp(mudt + volstd*Z), axis=0)
    St2 = S0*np.cumprod(np.exp(mudt - volstd*Z), axis=0)
    St1 = np.concatenate((np.full(shape=(1,M), fill_value=S0), St1))
    St2 = np.concatenate((np.full(shape=(1,M), fill_value=S0), St2))
    
    # compute delta hedge for each timestep (except for last) (transpose then untranspose)
    deltaSt1 = delta_calc(St1[:-1].T, K, vol, r, np.linspace(T,dt,N), optiontype).T
    deltaSt2 = delta_calc(St2[:-1].T, K, vol, r, np.linspace(T,dt,N), optiontype).T
    # compute gamma hedge for each timestep (except for last) (transpose then untranspose)
    gammaSt1 = gamma_calc(St1[:-1].T, K, vol, r, np.linspace(T,dt,N)).T
    gammaSt2 = gamma_calc(St2[:-1].T, K, vol, r, np.linspace(T,dt,N)).T
    
    # compute summation of hedge payoffs
    cv1 = np.cumsum(deltaSt1*(St1[1:]-St1[:-1]*erdt), axis = 0) + np.cumsum(deltaSt2*(St2[1:]-St2[:-1]*erdt), axis = 0)
    cv2 = np.cumsum(gammaSt1*((St1[1:]-St1[:-1])**2 - ergamma*(St1[:-1]**2)), axis = 0) + np.cumsum(gammaSt2*((St2[1:]-St2[:-1])**2 - ergamma*(St2[:-1]**2)), axis = 0)

    # compute payoff using relationship between option payoff and summation of delta and gamma hedges
    if (optiontype == 'c'):
        CT = 0.5*(np.maximum(0, St1[-1] - K) + np.maximum(0, St2[-1] - K) + beta1*cv1[-1]+  beta2*cv2[-1])
        optionString = "Call"
    else:
        CT = 0.5*(np.maximum(0, K - St1[-1]) + np.maximum(0, K - St2[-1]) + beta1*cv1[-1]+  beta2*cv2[-1])
        optionString = "Put"

    # Price of option is discounted average payoff
    C0 = np.exp(-r*T)*np.sum(CT)/M

    # Standard Deviation of payoffs
    sigma = np.sqrt(np.sum( (np.exp(-r*T)*CT - C0)**2) / (M-1))
    # Standard error (sample standard deviation)
    SE = sigma/np.sqrt(M)

    mc_time_adgv = time.time() - start_time # get computation time

    print("Antithetic, Delta, and Gamma Control Variates Optimization")
    print(optionString + " value is ${0} with SE +/- {1}".format(np.round(C0,2), np.round(SE,4)))
    print("Computation time is: ", round(mc_time_adgv,4))
    print("\n")
    
    return (C0,SE)

#C0_adgv, SE_adgv = monteCarlo_antithetic_delta_and_gamma(S0, K, vol, r, T, N, M, optiontype)





# **can incorporate variance reduction methods** Barrier Monte Carlo Method (assuming asset price behaves with respect to Geometric Brownian Motion (GBM))
def monteCarlo_barrier_option(S0, K, H, vol, r, T, N, M, optiontype):
    start_time = time.time() # computation speed purposes

    # natural logarithm simulation (arithmetic brownian motion ~ Normally distributed)
    dt = T/N
    mudt = (r - 0.5*(vol**2))*dt # drift term, if you include dividends => (r - div - 0.5*(vol**2))*dt
    volstd = vol*np.sqrt(dt) # diffusion term
    lnS0 = np.log(S0) # natural log of S0

    # generates random increments for diffusion term
    Z = np.random.normal(size=(N,M))
    # arithmetic brownian motion SDE
    dlnSt = mudt + volstd*Z

    # compute stock price over time and concatenate initial price to front
    lnSt = lnS0 + np.cumsum(dlnSt, axis=0)
    lnSt = np.concatenate((np.full(shape=(1,M), fill_value=lnS0), lnSt))

    # Renormalize stock price at time T
    St = np.exp(lnSt)
    
    # Copy array for plotting purposes
    S0 = np.copy(St)

    # check barrier conditions for each simulated stock path
    # up-and-out change to mask = np.any(St <= H, axis = 0) for down-and-out
    mask = np.any(St >= H, axis = 0)
    St[:, mask] = 0

    # compute payoff for non-violating paths
    if (optiontype == 'c'):
        CT = np.maximum(0, St[-1][St[-1] != 0] - K)
        optionString = "Call"
    else:
        CT = np.maximum(0, K - St[-1][St[-1] != 0])
        optionString = "Put"

    # Price of option is discounted average payoff
    C0 = np.exp(-r*T)*np.sum(CT)/M 

    # Standard Deviation of payoffs
    sigma = np.sqrt(np.sum((np.exp(-r*T)*CT - C0)**2) / (M-1))
    # Standard error (sample standard deviation)
    SE = sigma/np.sqrt(M)

    mc_time_b = time.time() - start_time # get computation time

    print("Traditional Monte Carlo (no-optimizations) Barrier Option")
    print(optionString + " value is ${0} with SE +/- {1}".format(np.round(C0,2), np.round(SE,4)))
    print("Computation time is: ", round(mc_time_b,4))
    print("\n")
    
    return (S0, mask)

#S0_b, mask_b = monteCarlo_barrier_option(S0, K, H, vol, r, T, N, M, optiontype)





#Visualization of Convergence
'''
market_value = 50 # market price of options, for graphing purposes
x1 = np.linspace(C0-3*SE, C0-1*SE, 100)
x2 = np.linspace(C0-1*SE, C0+1*SE, 100)
x3 = np.linspace(C0+1*SE, C0+3*SE, 100)
xw = np.linspace(C0w-3*SEw, C0w+3*SEw, 100)

s1 = stats.norm.pdf(x1, C0, SE)
s2 = stats.norm.pdf(x2, C0, SE)
s3 = stats.norm.pdf(x3, C0, SE)
sw = stats.norm.pdf(xw, C0w, SEw)

plt.fill_between(x1, s1, color='tab:blue', label='> StDev')
plt.fill_between(x2, s2, color='cornflowerblue', label='1 StDev')
plt.fill_between(x3, s3, color='tab:blue')
plt.plot(xw, sw, 'g-')
plt.fill_between(xw, sw, alpha=0.2, color='tab:green', label='w/o Antithetic')

plt.plot([C0, C0],[0, max(s2)*1.1], 'k', label='Theoretical Value')
plt.plot([C0w, C0w],[0, max(s2)*1.1], 'g-', label='Value w/o Antithetic')
plt.plot([market_value, market_value], [0, max(s2)*1.1], 'r', label='Market Value')

plt.ylabel('Probability')
plt.xlabel('Option Price')
plt.legend()
plt.show()
'''


# Barrier Option Plot
'''
plt.figure(figsize=(8,6))

plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = "16"

plt.plot(np.linspace(0,T,N+1), S0_b[:,mask_b], 'r')
plt.plot(np.linspace(0,T,N+1), S0_b[:,~mask_b], 'g')
plt.plot([0,T],[H,H], 'k-', linewidth=5.0)
plt.annotate('H', (0.05,130))
plt.xlim(0,T)
plt.xlabel('Time')
plt.ylabel('Price')
plt.title('European Up-and-Out Put Option')

plt.show()
'''










