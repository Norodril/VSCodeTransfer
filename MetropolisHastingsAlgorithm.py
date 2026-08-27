"""
We want to create a Markov chain that eventually haves like the target distribution:
proportional to i^-3/2
"""
import numpy as np

#Proposal Chain - Simple Symmetric Random Walk
def ssrrw(i):
    if i == 1:
        return 2
    else: 
        return np.random.choice([i - 1, i + 1])

#Metropolis-Hastings Acceptance/Rejection
def ars(i):
    j = ssrrw(i) #Proposing new state
    u = np.random.uniform(0, 1)
    #currently at state 1
    if i == 1:
        a = 2 ** (-5/2)
        if u <= a:
            return j 
        else: 
            return i 
    
    #moving from i to i + 1
    elif j == i + 1:
        a = (i / (i + 1)) ** (3 / 2)
        if u <= a:
            return j
        else:
            return i
        
    #moving from i to i - 1
    elif j == i - 1:
        a = (i / (i - 1)) ** (3 / 2)
        if u <= a:
            return j
        else: 
            return i
    
#Running the Metropolis-Hastings Chain
np.random.seed(20251110)
nsim = 2000000

#starting chain at state 1
mcsample = np.ones(nsim, dtype = int)
for k in range(nsim - 1):
    i = mcsample[k]
    mcsample[k + 1] = ars(i)

#burn-in
bi = 1000000
samples_after_burnin = mcsample[bi:]

#Counting how often states 1 through 10 appear
counts = np.bincount(samples_after_burnin, minlength = 11)[1:11]

#Converting counts to frequencies
frequencies = counts / len(samples_after_burnin)
print(frequencies)