"""
Order of Initial Conditions and Parameters

SIR:
    - IC: [iS, iI, iR]
    - Params: [beta, gamma, N]

SEIR:
    - IC: [iS, iE, iI, iR]
    - Params: [beta, gamma, sigma, N]

SIR_D:
    - IC: [iS, iI, iR]
    - Params: [beta, gamma, F, L, Nof, Nol, D]

SEIR_D: 
    - IC: [iS, iE, iI, iR]
    - Params: [beta, gamma, sigma, F, L, Nof, Nol, D]

SIR_split:
    - IC: [iSl, iSf, iIl, iIf, iRl, iRf]
    - Params: [beta, gamma, F, L, Nof, Nol]

SEIR_split:
    - IC: [iSl, iSf, iEl, iEf, iIl, iIf, iRl, iRf]
    - Params: [beta, gamma, sigma, F, L, Nof, Nol]

############################

Usage example:

iS = 990
iI = 10
iR = 0

beta = 0.2
gamma = 0.2
N = 100 # N = iS + iI + iR

ic = [iS, iI, iR]
params = [beta, gamma, N]

days = 365
tspan = np.arange(0, days, 1)

model = SIR(ic, tspan, params)
res = model.solve()

S = res[:,0]
I = res[:,1]
R = res[:,2]

"""
import numpy as np
import pandas as pd
from scipy.integrate import odeint

DAYS = 365
STEP = 1


class Model:
    """
    Helper base class to manipulate the models without actually knowing about them.
    """

    def __init__(self, initial_conditions, tspan, params, days=DAYS, step=STEP):
        self.index = np.arange(0, days, step)
        self.initial_conditions = initial_conditions
        self.params = params
        self.tspan = tspan

    @classmethod
    def available_models(cls):
        return cls.__subclasses__()

    @classmethod
    def get_model(cls, name):
        subclasses = cls.__subclasses__()
        return [x for x in subclasses if x.__name__.lower() == name].pop()


class SplittedSIR(Model):
    columns = ("Sl", "Sf", "Il", "If", "Rl", "Rf")

    def solve(self):
        beta, gamma, F, L, Nof, Nol = self.params
        T = Nof * F + Nol * L

        # XXX: `res` could be a proper class. It could handle it's own persistence and lookup.
        #      that way we can store results, compare, etc.
        #      it would make the application logic thinner.

        res = odeint(
            self.__ode_model,
            self.initial_conditions,
            self.tspan,
            args=(beta, gamma, F, L, T),
        )
        res = pd.DataFrame(data=res, columns=self.columns)
        return res

    def __ode_model(self, initial_conditions, tspan, beta, gamma, F, L, T):
        Sl, Sf, Il, If, _, _ = initial_conditions

        dSfdt = -((beta * F * Sf * (If * F + Il * L)) / T)
        dSldt = -((beta * L * Sl * (If * F + Il * L)) / T)
        dIfdt = ((beta * F * Sf * (If * F + Il * L)) / T) - (gamma * If)
        dIldt = ((beta * L * Sl * (If * F + Il * L)) / T) - (gamma * Il)
        dRfdt = gamma * If
        dRldt = gamma * Il

        return [dSldt, dSfdt, dIldt, dIfdt, dRldt, dRfdt]


class SplittedSEIR(Model):
    columns = ("Sl", "Sf", "El", "Ef", "Il", "If", "Rl", "Rf")

    def solve(self):
        beta, gamma, sigma, F, L, Nof, Nol = self.params
        T = Nof * F + Nol * L
        res = odeint(
            self.__ode_model,
            self.initial_conditions,
            self.tspan,
            args=(beta, gamma, sigma, F, L, T),
        )
        res = pd.DataFrame(data=res, columns=self.columns)
        return res

    def __ode_model(self, initial_conditions, tspan, beta, gamma, sigma, F, L, T):
        Sl, Sf, El, Ef, Il, If, _, _ = initial_conditions

        dSfdt = -((beta * F * Sf * (If * F + Il * L)) / T)
        dSldt = -((beta * L * Sl * (If * F + Il * L)) / T)
        dEfdt = ((beta * F * Sf * (If * F + Il * L)) / T) - (sigma * Ef)
        dEldt = ((beta * L * Sl * (If * F + Il * L)) / T) - (sigma * El)
        dIfdt = (sigma * Ef) - (gamma * If)
        dIldt = (sigma * El) - (gamma * Il)
        dRfdt = gamma * If
        dRldt = gamma * Il

        return [dSldt, dSfdt, dEldt, dEfdt, dIldt, dIfdt, dRldt, dRfdt]


class SIR(Model):
    columns = ("S", "I", "R")

    def solve(self):
        beta, gamma, N = self.params
        res = odeint(
            self.__ode_model, self.initial_conditions, self.tspan, args=(beta, gamma, N)
        )
        res = pd.DataFrame(data=res, columns=self.columns)
        return res

    def __ode_model(self, initial_conditions, tspan, beta, gamma, N):
        S, I, _ = initial_conditions

        dSdt = -((beta * S * I) / N)
        dIdt = ((beta * S * I) / N) - (gamma * I)
        dRdt = gamma * I

        return [dSdt, dIdt, dRdt]


class SEIR(Model):
    columns = ("S", "E", "I", "R")

    def solve(self):
        beta, gamma, sigma, N = self.params
        res = odeint(
            self.__ode_model,
            self.initial_conditions,
            self.tspan,
            args=(beta, gamma, sigma, N),
        )
        res = pd.DataFrame(data=res, columns=self.columns)
        return res

    def __ode_model(self, initial_conditions, tspan, beta, gamma, sigma, N):
        S, E, I, _ = initial_conditions

        dSdt = -((beta * S * I) / N)
        dEdt = ((beta * S * I) / N) - (sigma * E)
        dIdt = (sigma * E) - (gamma * I)
        dRdt = gamma * I

        return [dSdt, dEdt, dIdt, dRdt]


class SIR_D(Model):
    columns = ("S", "I", "R")

    def solve(self):
        beta, gamma, F, L, Nof, Nol, D = self.params
        Q = ((Nof * (1 - D) * F) + ((Nol + Nof * D) * L)) / (Nof * F + Nol * L)
        res = odeint(
            self.__ode_model, self.initial_conditions, self.tspan, args=(beta, gamma, Q)
        )
        res = pd.DataFrame(data=res, columns=self.columns)
        return res

    def __ode_model(self, initial_conditions, tspan, beta, gamma, Q):
        S, I, _ = initial_conditions

        dSdt = -(beta * S * I * Q)
        dIdt = (beta * S * I * Q) - (gamma * I)
        dRdt = gamma * I

        return [dSdt, dIdt, dRdt]


class SEIR_D(Model):
    columns = ("S", "E", "I", "R")

    def solve(self):
        beta, gamma, sigma, F, L, Nof, Nol, D = self.params
        Q = ((Nof * (1 - D) * F) + ((Nol + Nof * D) * L)) / (Nof * F + Nol * L)
        res = odeint(
            self.__ode_model,
            self.initial_conditions,
            self.tspan,
            args=(beta, gamma, sigma, Q),
        )
        res = pd.DataFrame(data=res, columns=self.columns)
        return res

    def __ode_model(self, initial_conditions, tspan, beta, gamma, sigma, Q):
        S, E, I, _ = initial_conditions

        dSdt = -(beta * S * I * Q)
        dEdt = (beta * S * I * Q) - (sigma * E)
        dIdt = (sigma * E) - (gamma * I)
        dRdt = gamma * I

        return [dSdt, dEdt, dIdt, dRdt]
