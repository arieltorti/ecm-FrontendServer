import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from models import SplittedSEIR, SIR


initSl = 599800
initSf = 399800
initS = initSl + initSf

initEl = 0
initEf = 0
initE = initEf + initEl

initIl = 200
initIf = 200
initI = initIf + initIl

initRl = 0
initRf = 0
initR = initRf + initRl

beta = 0.3
gamma = 0.2
sigma = 0.14

Nof = 400000
Nol = 600000
N = Nof + Nol

F = 8
L = 1
D = 0

days = 365

# # SEIR Splitted
initial_conditions = [initSl, initSf, initEl, initEf, initIl, initIf, initRl, initRf]
params = [beta, gamma, sigma, F, L, Nof, Nol]
tspan = np.arange(0, days, 1)
model = SplittedSEIR(initial_conditions, tspan, params)
res = model.solve()
Sl, Sf, El, Ef, Il, If, Rl, Rf = res[:, 0], res[:, 1], res[:, 2], res[:, 3], res[:, 4], res[:, 5], res[:, 6], res[:, 7]
step = 1
t = np.arange(0, days, step)
df = pd.DataFrame(data={"Sl":Sl, "Sf":Sf, "El":El, "Ef":Ef, "Il":Il, "If":If, "Rl":Rl, "Rf":Rf},index= t)

df.plot()
plt.grid(True)
plt.show()

# #######################################################################################################

# SIR

initial_conditions = [initS, initI, initR]
params = [beta, gamma, N]
tspan = np.arange(0, days, 1)
model = SIR(initial_conditions, tspan, params)
res = model.solve()
S, I, R = res[:, 0], res[:, 1], res[:, 2]
step = 1
t = np.arange(0, days, step)
df = pd.DataFrame(data={"S":S, "I":I, "R":R},index= t)

df.plot()
plt.grid(True)
plt.show()

# #######################################################################################################


