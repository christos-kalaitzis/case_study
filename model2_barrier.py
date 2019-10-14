import numpy as np
from model2_poly import *
import matplotlib.pyplot as plt
from date_handling import *

#Monte Carlo evaluation of a barrier put option 
#barrier:the barrier value
#strike:the strike value
#r0:original FX rate
#maturity:the expiry time of the option
#rd:domestic rate
#rf:foreign rate
#a:the coefficients of the volatility polynomial
#time_axis:container used to manipulate time
#N:number of samples
def evaluate_barrier_put_option(barrier,strike,r0,maturity,rd,rf,a,time_axis,N,volatility=0):
#Setting up some convenience variables
	dtm=time_axis["dtm"]
	mti=time_axis["mti"]
	itd=time_axis["itd"]
	dti=time_axis["dti"]
	
	V=0
	activations=0

	if (isinstance(volatility,np.ndarray)==False):
		volatility=[]
		T=1/252
		while T<=maturity:
			volatility.append(poly_square_int(T,a))
			T=T+1/252
	
	for i in range(N): #We sample N paths
		t=0
		W=0
		activate=False
		while (t<maturity and activate==False):
			W=W+np.random.normal()*np.sqrt(1/252)
			R=r0*np.exp((rd-rf-volatility[i]**2/2)*t)*np.exp(volatility[i]*W)
			
			#For each path we check if the barrier is activated
			if (R<=barrier):
				activate=True
				activations=activations+1
			
			t=t+1/252
		
		#If the barrier is activated, add the discounted payoff to the value
		if activate==True:
			while (t<maturity):
				W=W+np.random.normal()*np.sqrt(1/252)
				t=t+1/252
			R=r0*np.exp((rd-rf-volatility[i]**2/2)*t)*np.exp(volatility[i]*W)
			V=V+max(0,strike-R)/N*np.exp(-rd*maturity)
	#print("Activation probability",activations/N)
	return V

#Same as above, but for call options
def evaluate_barrier_call_option(barrier,strike,r0,maturity,rd,rf,a,time_axis,N,volatility=0):
	dtm=time_axis["dtm"]
	mti=time_axis["mti"]
	itd=time_axis["itd"]
	dti=time_axis["dti"]
	
	V=0
	activations=0
	
	if (isinstance(volatility,np.ndarray)==False):
		volatility=[]
		T=1/252
		while T<=maturity:
			volatility.append(poly_square_int(T,a))
			
	for i in range(N):
		t=0
		W=0
		activate=False
		while (t<=maturity and activate==False):
			W=W+np.random.normal()*np.sqrt(1/252)
			R=r0*np.exp((rd-rf-volatility[i]**2/2)*t)*np.exp(volatility[i]*W)

			if (R>=barrier):
				activate=True
				activations=activations+1
			
			t=t+1/252

		if activate==True:
			while (t<maturity):
				W=W+np.random.normal()*np.sqrt(1/252)
				t=t+1/252
			R=r0*np.exp((rd-rf-volatility[i]**2/2)*t)*np.exp(volatility[i]*W)
			V=V+max(0,R-strike)/N*np.exp(-rd*maturity)
	#print("Activation probability",activations/N)
	return V

#A function to calculate the prices of a pair of options
#r12:original FX rate
#r1:domestic rate
#r2:foreign rate
#m:drift of the FX rate
#a:the coefficients of the volatiltiy polynomial
#q:determines on how many sigmas the barrier and strike are calculated
#time_axis:container used to manipulate time
#N:number of samples
def get_barriers(r1,r2,r12,m,a,q,fund_dates,time_axis,N,vol):
	bput=[]
	bcall=[]
	for d in fund_dates[1:]:
	#Here we just calculate the value of each option, if the nominal value was 1

		T=time_axis['dtm'][to_workday(d)]
		print("maturity:",T)
		
		s=poly_square_int(T,a)
		barrier=r12*np.exp((m-s**2/2)*T)*np.exp(-q*s*np.sqrt(T))
		strike=r12*np.exp((m-s**2/2)*T)*np.exp(q*s*np.sqrt(T))
		x=evaluate_barrier_put_option(barrier,strike,r12,T,r1,r2,a,time_axis,N,vol)
		print("Put value:",x)
		bput.append({"maturity":T, "barrier":barrier, "strike":strike, "value":x})
		
		barrier=r12*np.exp((m-s**2/2)*T)*np.exp(q*s*np.sqrt(T))
		strike=r12*np.exp((m-s**2/2)*T)*np.exp(-q*s*np.sqrt(T))
		x=evaluate_barrier_call_option(barrier,strike,r12,T,r1,r2,a,time_axis,N,vol)
		print("Call value:",x)
		bcall.append({"maturity":T, "barrier":barrier, "strike":strike, "value":x})

		print()
	return (bput,bcall)