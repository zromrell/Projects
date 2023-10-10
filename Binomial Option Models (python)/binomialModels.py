import numpy as np
from py_vollib.black_scholes import black_scholes as bs
import matplotlib.pyplot as plt

# Initial Parameters
S0 = 100       # initial stock price
K = 100        # strike price
T = 3          # time to maturity in years
H = 125        # up-and-out barrier price/value ***specific to up-and-out  or down-and-out***
r = 0.06       # annual risk-free rate
N = 3          # number of time steps
u = 1.1        # up factor in binomial model
d = 1/u        # ensure recombining tree
opttype = 'c'  # Option Type 'c' or 'p'
vol = 0.2      # volatility of asset


if (opttype == 'c'):
    optionString = "Call"
else:
    optionString = "Put"


# European Option
def european_option(K,T,S0,r,N,u,d,opttype):
    # compute constants
    dt = T/N
    p = (np.exp(r*dt)-d)/(u-d)
    disc = np.exp(-r*dt)

    # initialize asset prices at maturity
    C = S0 * u**(np.arange(N,-1, -1)) * d**(np.arange(0,N+1,1))

    # compute payoffs
    if (opttype == 'c'):
        C = np.maximum(C-K, np.zeros(N+1))
    else:
        C = np.maximum(K-C, np.zeros(N+1))

    # compute value of option at each time step with risk-neutral probabilities
    for i in np.arange(N,0,-1):
        C = disc * (p*C[0:i] + (1-p)*C[1:i+1])

    return C[0]

print("European Option")
print(optionString + " price: {} ".format(european_option(K,T,S0,r,N,u,d,opttype)))





# European UP-AND-OUT Option
def european_option_up_and_out(K,T,S0,H,r,N,u,d,opttype):
    # compute constants
    dt = T/N
    p = (np.exp(r*dt)-d)/(u-d)
    disc = np.exp(-r*dt)

    # initialize asset prices at maturity
    S = S0 * u**(np.arange(N,-1, -1)) *  d**(np.arange(0,N+1,1))

    # compute payoffs
    if (opttype == 'c'):
        C = np.maximum(S-K, 0)
    else:
        C = np.maximum(K-S, 0)

    # condition on C relative to S
    C[S >= H] = 0

    # compute value of option at each time step with risk-neutral probabilities
    for i in np.arange(N-1,-1,-1):
        S =  S0 * u**(np.arange(i,-1, -1)) * d**(np.arange(0,i+1,1))
        C[:i+1] = disc * (p*C[0:i+1] + (1-p)*C[1:i+2])
        C = C[:-1]
        C[S >= H] = 0
        
    return C[0]

print("European Up-And-Out Option")
print(optionString + " price: {} ".format(european_option_up_and_out(K,T,S0,H,r,N,u,d,opttype)))





# European DOWN-AND-OUT Option
def european_option_down_and_out(K,T,S0,H,r,N,u,d,opttype):
    # compute constants
    dt = T/N
    p = (np.exp(r*dt)-d)/(u-d)
    disc = np.exp(-r*dt)

    # initialize asset prices at maturity
    S = S0 * u**(np.arange(N,-1, -1)) *  d**(np.arange(0,N+1,1))

    # compute payoffs
    if (opttype == 'c'):
        C = np.maximum(S-K, 0)
    else:
        C = np.maximum(K-S, 0)

    # condition on C relative to S
    C[S <= H] = 0

    # compute value of option at each time step with risk-neutral probabilities    
    for i in np.arange(N-1,-1,-1):
        S =  S0 * u**(np.arange(i,-1, -1)) * d**(np.arange(0,i+1,1))
        C[:i+1] = disc * (p*C[0:i+1] + (1-p)*C[1:i+2])
        C = C[:-1]
        C[S <= H] = 0
        
    return C[0]

print("European Down-And-Out Option")
print(optionString + " price: {} ".format(european_option_down_and_out(K,T,S0,H,r,N,u,d,opttype)))





#American Option
def american_option(K,T,S0,r,N,u,d,opttype):
    # compute constants
    dt = T/N
    p = (np.exp(r*dt)-d)/(u-d)
    disc = np.exp(-r*dt)

    # initialize asset prices at maturity
    S = S0 * u**(np.arange(N,-1, -1)) *  d**(np.arange(0,N+1,1))

    # compute payoffs
    if (opttype == 'c'):
        C = np.maximum(S-K, 0)
    else:
        C = np.maximum(K-S, 0)
        
    # compute value of option at each time step with risk-neutral probabilities
    for i in np.arange(N-1,-1,-1):
        S =  S0 * u**(np.arange(i,-1, -1)) * d**(np.arange(0,i+1,1))
        C[:i+1] = disc * (p*C[0:i+1] + (1-p)*C[1:i+2])
        C = C[:-1]
        if (opttype == 'C'):
            C = np.maximum(S-K, C)
        else:
            C = np.maximum(K-S, C)

    return C[0]

print("American Option")
print(optionString + " price: {} ".format(american_option(K,T,S0,r,N,u,d,opttype)))





#American UP-AND-OUT Option
def american_up_and_out_option(K,T,S0,H,r,N,u,d,opttype):
    # compute constants
    dt = T/N
    p = (np.exp(r*dt)-d)/(u-d)
    disc = np.exp(-r*dt)

    # initialize asset prices at maturity
    S = S0 * u**(np.arange(N,-1, -1)) *  d**(np.arange(0,N+1,1))

    # compute payoffs
    if (opttype == 'c'):
        C = np.maximum(S-K, 0)
    else:
        C = np.maximum(K-S, 0)

    # condition on C relative to S
    C[S >= H] = 0
        
    # compute value of option at each time step with risk-neutral probabilities 
    for i in np.arange(N-1,-1,-1):
        S =  S0 * u**(np.arange(i,-1, -1)) * d**(np.arange(0,i+1,1))
        C[:i+1] = disc * (p*C[0:i+1] + (1-p)*C[1:i+2])
        C = C[:-1]
        if (opttype == 'C'):
            C = np.maximum(S-K, C)
        else:
            C = np.maximum(K-S, C)
        C[S >= H] = 0

    return C[0]

print("American Up-And-Out Option")
print(optionString + " price: {} ".format(american_up_and_out_option(K,T,S0,H,r,N,u,d,opttype)))





#American DOWN-AND-OUT Option
def american_down_and_out_option(K,T,S0,H,r,N,u,d,opttype):
    # compute constants
    dt = T/N
    p = (np.exp(r*dt)-d)/(u-d)
    disc = np.exp(-r*dt)

    # initialize asset prices at maturity
    S = S0 * u**(np.arange(N,-1, -1)) *  d**(np.arange(0,N+1,1))

    # compute payoffs
    if (opttype == 'c'):
        C = np.maximum(S-K, 0)
    else:
        C = np.maximum(K-S, 0)

    # condition on C relative to S
    C[S <= H] = 0
        
    # compute value of option at each time step with risk-neutral probabilities
    for i in np.arange(N-1,-1,-1):
        S =  S0 * u**(np.arange(i,-1, -1)) * d**(np.arange(0,i+1,1))
        C[:i+1] = disc * (p*C[0:i+1] + (1-p)*C[1:i+2])
        C = C[:-1]
        if (opttype == 'c'):
            C = np.maximum(S-K, C)
        else:
            C = np.maximum(K-S, C)
        C[S <= H] = 0

    return C[0]

print("American Down-And-Out Option")
print(optionString + " price: {} ".format(american_down_and_out_option(K,T,S0,H,r,N,u,d,opttype)))





# Cox, Ross, and Rubinstein method for choosing u,d,p,(1-p)
def CRR_method(T,N,r,sigma):
    dt = T/N
    mu = (r - 0.5*(sigma**2))
    u = np.exp(mu*dt + sigma*np.sqrt(dt))
    d = np.exp(mu*dt - sigma*np.sqrt(dt))
    p = 1/2
    return (u,d,p)





# Jarrow and Rudd's method for choosing u,d,p,(1-p)
def JR_method(T,N,r,sigma):
    dt = T/N
    u = np.exp(sigma*np.sqrt(dt))
    d = 1/u
    #p = (np.exp(r*dt)-d)/(u-d) #yield same thing
    p = 0.5 + ((r - 0.5*sigma**2)*np.sqrt(dt))/(2*sigma)
    return (u,d,p)
    




# European Option
def alternative_european_option(S0,K,T,r,N,vol,opttype,method):
    # compute constants
    dt = T/N
    if method == 'CRR':
        u,d,p = CRR_method(T,N,r,vol)
    else:
        u,d,p = JR_method(T,N,r,vol)
    disc = np.exp(-r*dt)

    # initialize asset prices at maturity
    C = S0 * u**(np.arange(N,-1, -1)) * d**(np.arange(0,N+1,1))


    # compute payoffs
    if (opttype == 'c'):
        C = np.maximum(C-K, np.zeros(N+1))
    else:
        C = np.maximum(K-C, np.zeros(N+1))

    # compute value of option at each time step with risk-neutral probabilities
    for i in np.arange(N,0,-1):
        C = disc * (p*C[0:i] + (1-p)*C[1:i+1])

    return C[0]

print("European Option CRR")
print(optionString + " price: {} ".format(alternative_european_option(S0,K,T,r,N,vol,opttype,'CRR')))
print("European Option JR")
print(optionString + " price: {} ".format(alternative_european_option(S0,K,T,r,N,vol,opttype,'JR')))





# American Option
def alternative_american_option(S0,K,T,r,N,vol,opttype,method):
    # compute constants
    dt = T/N
    if method == 'CRR':
        u,d,p = CRR_method(T,N,r,vol)
    else:
        u,d,p = JR_method(T,N,r,vol)
    disc = np.exp(-r*dt)

    # initialize asset prices at maturity
    S = S0 * u**(np.arange(N,-1, -1)) * d**(np.arange(0,N+1,1))


    # compute payoffs
    if (opttype == 'c'):
        C = np.maximum(S-K, 0)
    else:
        C = np.maximum(K-S, 0)
        

    # compute value of option at each time step with risk-neutral probabilities
    for i in np.arange(N-1,-1,-1):
        S =  S0 * u**(np.arange(i,-1, -1)) * d**(np.arange(0,i+1,1))
        C[:i+1] = disc * (p*C[0:i+1] + (1-p)*C[1:i+2])
        C = C[:-1]
        if (opttype == 'c'):
            C = np.maximum(S-K, C)
        else:
            C = np.maximum(K-S, C)
            
    return C[0]

print("American Option CRR")
print(optionString + " price: {} ".format(alternative_american_option(S0,K,T,r,N,vol,opttype,'CRR')))
print("American Option JR")
print(optionString + " price: {} ".format(alternative_american_option(S0,K,T,r,N,vol,opttype,'JR')))





# Equal Probability Method
def EQP_method(T,N,r,vol):
    dt = T/N
    mu = r - 0.5*(vol**2)
    dx_u = 0.5*mu*dt + 0.5*np.sqrt(4*vol**2 * dt - 3*mu**2 * dt**2)
    dx_d = 1.5*mu*dt - 0.5*np.sqrt(4*vol**2 * dt - 3*mu**2 * dt**2)
    p = 0.5
    return (dx_u,dx_d,p)





# Trigeorgis Method
def TRG_method(T,N,r,vol):
    dt = T/N
    mu = r - 0.5*(vol**2)
    dx_u = np.sqrt(vol**2 *dt + mu**2 * dt**2)
    dx_d = -1*dx_u
    p = 0.5 + (0.5*mu*dt)/dx_u
    return (dx_u,dx_d,p)





# European version of general additive binomial model
def european_general_additive_binomial(S0,K,T,r,N,vol,opttype,method):
    # compute constants
    dt = T/N

    if method == 'EQP':
        dx_u, dx_d, p = EQP_method(T,N,r,vol)
    else:
        dx_u, dx_d, p = TRG_method(T,N,r,vol)
    
    disc = np.exp(-r*dt)

    # initialize asset prices at maturity
    C = S0 * np.exp(dx_u*(np.arange(N,-1, -1)) + dx_d*(np.arange(0,N+1,1)))
    

    # compute payoffs
    if (opttype == 'c'):
        C = np.maximum(C-K, np.zeros(N+1))
    else:
        C = np.maximum(K-C, np.zeros(N+1))

    # compute value of option at each time step with risk-neutral probabilities 
    for i in np.arange(N,0,-1):
        C = disc * (p*C[0:i] + (1-p)*C[1:i+1])

    return C[0]

print("European General Additive Binomial Model EQP")
print(optionString + " price: {} ".format(european_general_additive_binomial(S0,K,T,r,N,vol,opttype,'EQP')))
print("European General Additive Binomial Model TRG")
print(optionString + " price: {} ".format(european_general_additive_binomial(S0,K,T,r,N,vol,opttype,'TRG')))





# American version of general additive binomial model
def american_general_additive_binomial(S0,K,T,r,N,vol,opttype,method):
    # compute constants
    dt = T/N
    if method == 'EQP':
        dx_u,dx_d,p = EQP_method(T,N,r,vol)
    else:
        dx_u,dx_d,p = TRG_method(T,N,r,vol)
    disc = np.exp(-r*dt)

    # initialize asset prices at maturity
    S = S0 * np.exp(dx_u*(np.arange(N,-1, -1)) + dx_d*(np.arange(0,N+1,1)))

    # compute payoffs
    if (opttype == 'c'):
        C = np.maximum(S-K, 0)
    else:
        C = np.maximum(K-S, 0)
        
    # compute value of option at each time step with risk-neutral probabilities 
    for i in np.arange(N-1,-1,-1):
        S = S0 * np.exp(dx_u*(np.arange(i,-1, -1)) + dx_d*(np.arange(0,i+1,1)))
        C[:i+1] = disc * (p*C[0:i+1] + (1-p)*C[1:i+2])
        C = C[:-1]
        if (opttype == 'c'):
            C = np.maximum(S-K, C)
        else:
            C = np.maximum(K-S, C)
            
    return C[0]

print("American General Additive Binomial Model EQP")
print(optionString + " price: {} ".format(american_general_additive_binomial(S0,K,T,r,N,vol,opttype,'EQP')))
print("American General Additive Binomial Model TRG")
print(optionString + " price: {} ".format(american_general_additive_binomial(S0,K,T,r,N,vol,opttype,'TRG')))





# Comparison of methods
def compareMethods():
    CRR, JR, EQP, TRG = [],[],[],[]
    
    periods = range(10,100,10)

    for X in periods:
        CRR.append(alternative_american_option(S0,K,T,r,X,vol,opttype,'CRR'))
        JR.append(alternative_american_option(S0,K,T,r,X,vol,opttype,'JR'))
        EQP.append(american_general_additive_binomial(S0,K,T,r,X,vol,opttype,'EQP'))
        TRG.append(american_general_additive_binomial(S0,K,T,r,X,vol,opttype,'TRG'))
        
        
    BS = [bs('c', S0, K, T, r, vol) for i in periods]

    plt.plot(periods, CRR, label='Cox_Ross_Rubinstein')
    plt.plot(periods, JR, label='Jarrow_Rudd')
    plt.plot(periods, EQP, label='EQP')
    plt.plot(periods, TRG, 'r--', label='Trigeorgis')
    plt.plot(periods, BS, 'k', label='Black-Scholes')
    plt.legend(loc='upper right')
    plt.show()

compareMethods()
