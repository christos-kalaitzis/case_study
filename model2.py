import numpy as np
import pandas as pd
import time
from datetime import date
from datetime import timedelta
import tensorflow as tf
import tensorflow_probability as tfp
import matplotlib.pyplot as plt
from scipy.stats import norm
from scipy import stats

from data_handling import *
from date_handling import *
from model2_IRR import *
from model2_MSE import *
from model2_calibrate import *
from model2_sampling import *
from model2_barrier import *
from import_data import *
from vanilla import *
from model2_poly import *

##########################
#We start by importing the market data and the fund returns
(market,fund)=import_data()

market_dates=market["dates"]
market_data=market["data"]
Spot=market["Spot"]
Forward=market["Forward"]
Imp_vol=market["Imp_vol"]
Yield=market["Yield"]
Swaption=market["Swaption"]

fund_data=fund["data"]
fund_dates=fund["dates"]
fund_USD=fund["USD"]
fund_Euro=fund["Euro"]
fund_GBP=fund["GBP"]
##########################


#We proceed with calibrating our model
#First we calculate the short rate at time 0 and the drifts of the involved Brownian motions
N=1000
r_USD=np.log((1+Yield["USD"]["3M"][-1]/100))
r_Euro=np.log((1+Yield["EUR"]["3M"][-1]/100))
r_GBP=np.log((1+Yield["GBP"]["3M"][-1]/100))
print("USD short rate: ",r_USD)
print("Euro short rate: ",r_Euro)
print("GBP short rate: ",r_GBP)

print("\nX-Y spot rate: how much of X one unit of Y can buy")
m_USD_Euro=r_USD-r_Euro
m_GBP_USD=r_GBP-r_USD
m_Euro_GBP=r_Euro-r_GBP

print("USD-Euro drift: ",m_USD_Euro)
print("USD-Euro spot rate:",Spot["EURUSD"][-1])

print("GBP-USD drift: ",m_GBP_USD)
print("GBP-USD spot rate:",1/Spot["GBPUSD"][-1])

print("Euro-GBP drift: ",m_Euro_GBP)
print("Euro-GBP spot rate:",1/Spot["EURGBP"][-1])

n=1 #We calibrate with respect to the prices observed in the n last days
maturities=list(Imp_vol['EURUSD'].keys())
m=len(maturities) #We consider options with m different maturities; the choice is made with numerical stability in mind


#We calibrate the volatilities of the 3 exchange rates
print("Calibrating USD-Euro volatility to minimize MSE of option prices in last ",n," day(s)")
(C_USD_Euro,S_USD_Euro)=sample_prices(Imp_vol['EURUSD'],maturities,r_USD,r_Euro,m,n)
a_USD_Euro=calibrate_vol(C_USD_Euro,maturities,r_USD,r_Euro,0.3,0.08)

print("Calibrating GBP-USD volatility to minimize MSE of option prices in last ",n," day(s)")
(C_GBP_USD,S_GBP_USD)=sample_prices(Imp_vol['GBPUSD'],maturities,r_GBP,r_USD,m,n)
a_GBP_USD=calibrate_vol(C_GBP_USD,maturities,r_GBP,r_USD,0.4,0.08)

print("Calibrating Euro-GBP volatility to minimize MSE of option prices in last ",n," day(s)")
(C_Euro_GBP,S_GBP_USD)=sample_prices(Imp_vol['EURGBP'],maturities,r_Euro,r_GBP,m,n)
a_Euro_GBP=calibrate_vol(C_Euro_GBP,maturities,r_Euro,r_GBP,0.4,0.08)


plot_vol("USD-Euro",r_USD,r_Euro,a_USD_Euro,Imp_vol["EURUSD"],maturities,m,n)
plot_vol("GBP-USD",r_GBP,r_USD,a_GBP_USD,Imp_vol["GBPUSD"],maturities,m,n)
plot_vol("Euro-GBP",r_Euro,r_GBP,a_Euro_GBP,Imp_vol["EURGBP"],maturities,m,n)


#We put all the model parameters in a container
model={}
model["m13"]=m_USD_Euro
model["a13"]=a_USD_Euro
model["r13_0"]=Spot["EURUSD"][-1]
model["m21"]=m_GBP_USD
model["a21"]=a_GBP_USD
model["r21_0"]=1/Spot["GBPUSD"][-1]
model["m32"]=m_Euro_GBP
model["a32"]=a_Euro_GBP
model["r32_0"]=1/Spot["EURGBP"][-1]

#We create a set of dictionaries whose only purpose is to have a convenient way of translating dates to how much time since time 0 passed, and vice versa
#In an ideal world we would only have time as a variable and not dates
#None of this is needed, we just find them handy
t=to_workday(fund_dates[0])
T=to_workday(fund_dates[-1])
dat_to_mat={}
dat_to_mat[t]=0
dat_to_ind={}
dat_to_ind[t]=0
mat_to_ind={}
mat_to_ind[0]=0
ind_to_dat=[]
ind_to_dat.append(t)
i=1

while (t<to_workday(T)):
	dat_to_mat[next_workday(t)]=dat_to_mat[t]+1/252 #this means that we are off by ~1/252 per year; that is an acceptable deviation
	mat_to_ind[dat_to_mat[next_workday(t)]]=i
	t=next_workday(t)
	dat_to_ind[t]=i
	ind_to_dat.append(t)
	i=i+1

time_axis={}
time_axis["dtm"]=dat_to_mat
time_axis["mti"]=mat_to_ind
time_axis["itd"]=ind_to_dat
time_axis["dti"]=dat_to_ind

#Take N samples from the IRR distribution 
(irr,sample_USD_Euro,sample_GBP_USD)=IRR_distribution(fund_data,model,N,time_axis)

#Next we create the barrier options
r_USD_Euro=model["r13_0"]
r_USD_GBP=1/model["r21_0"]

r_USD_Euro=Spot["EURUSD"][-1]
T=5

m_USD_GBP=-m_GBP_USD
a_USD_GBP=a_GBP_USD

#Precomputing for volatilities so we dont have to compute them over and over again
vol_USD_Euro=np.zeros(N)
vol_USD_GBP=np.zeros(N)
T=1/252
print("Precomputing equivalent volatilities...")
for i in range(N):
	T=(i+1)/252
	vol_USD_Euro[i]=poly_square_int(T,a_USD_Euro)
	vol_USD_GBP[i]=poly_square_int(T,a_GBP_USD)

	
#Calculating barrier prices
barriers={}
print("Calculating USD-Euro barrier prices")
(barriers["Euro put"],barriers["Euro call"])=get_barriers(r_USD,r_Euro,r_USD_Euro,m_USD_Euro,a_USD_Euro,1.6,fund_dates,time_axis,N,vol_USD_Euro)
print("Calculating USD-GBP barrier prices")
(barriers["GBP put"],barriers["GBP call"])=get_barriers(r_USD,r_GBP,r_USD_GBP,m_USD_GBP,a_USD_GBP,1.6,fund_dates,time_axis,N,vol_USD_GBP)
#Take N samples from the IRR distribution after we have incorporated the barrier options
(irh,sample_USD_Euro,sample_GBP_USD)=IRR_distribution_hedged(fund_data,model,barriers,N,time_axis,2)

print("IRR at risk before hedging-5%:",sorted(irr)[50])
h=max(plt.hist(irr,50,density=True,color='y')[0])
x=np.linspace(min(irr)-0.05,max(irr)+0.05,1000)
(mu,var)=stats.norm.fit(irr)
y=stats.norm.pdf(x,mu,var)
plt.plot(x,y,color='b')
a=[sorted(irr)[int(N/20)],sorted(irr)[int(N/20)]]
b=[0,h+1]
plt.plot(a,b,linestyle='dashed',color='r')
a=[sorted(irr)[int(19*N/20)],sorted(irr)[int(19*N/20)]]
b=[0,h+1]
plt.plot(a,b,linestyle='dashed',color='r')
a=[sorted(irr)[int(N/2)],sorted(irr)[int(N/2)]]
b=[0,h+1]
plt.plot(a,b,linestyle='dashed',color='r')
plt.show()

print("IRR at risk after hedging-5%:",sorted(irh)[50])
h=max(plt.hist(irh,30,density=True,color='y')[0])
x=np.linspace(min(irh)-0.05,max(irh)+0.05,1000)
a=[sorted(irh)[int(N/20)],sorted(irh)[int(N/20)]]
b=[0,h+1]
plt.plot(a,b,linestyle='dashed',color='r')
a=[sorted(irh)[int(19*N/20)],sorted(irh)[int(19*N/20)]]
b=[0,h+1]
plt.plot(a,b,linestyle='dashed',color='r')
a=[sorted(irh)[int(N/2)],sorted(irh)[int(N/2)]]
b=[0,h+1]
plt.plot(a,b,linestyle='dashed',color='r')
plt.show()
