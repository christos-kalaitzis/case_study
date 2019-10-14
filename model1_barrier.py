import numpy as np
from date_handling import *

#Monte Carlo evaluation of a barrier put option 
#barrier:the barrier value
#strike:the strike value
#r0:original FX rate
#maturity:the expiry time of the option
#rd:domestic rate
#rf:foreign rate
#volatility:the volatility of the FX rate
#time_axis:container used to manipulate time
#N:number of samples
def evaluate_barrier_put_option(barrier,strike,r0,maturity,rd,rf,volatility,time_axis,N):
#Setting up some convenience variables
	dtm=time_axis["dtm"]
	mti=time_axis["mti"]
	itd=time_axis["itd"]
	dti=time_axis["dti"]
	
	V=0
	A=[]
	B=[]
	x=0
	activations=0
	for i in range(N): #We sample N paths
		t=0
		W=0
		activate=False
		while (t<maturity and activate==False):
			W=W+np.sqrt(1/252)*np.random.normal()
			R=r0*np.exp((rd-rf-volatility**2/2)*t)*np.exp(volatility*W)
			
			#For each path we check if the barrier is activated
			if (R<=barrier):
				activate=True
				activations=activations+1
				#print(t,A[-1])
			
			t=t+1/252
		
		#If the barrier is activated, add the discounted payoff to the value
		if activate==True:
			while (t<maturity):
				W=W+np.random.normal()*np.sqrt(1/252)
				t=t+1/252
			R=r0*np.exp((rd-rf-volatility**2/2)*t)*np.exp(volatility*W)
			V=V+max(0,strike-R)/N*np.exp(-rd*maturity)
	#print("Activation probability",activations/N)
	return V

#Same as above, but for call options
def evaluate_barrier_call_option(barrier,strike,r0,maturity,rd,rf,volatility,time_axis,N):
	dtm=time_axis["dtm"]
	mti=time_axis["mti"]
	itd=time_axis["itd"]
	dti=time_axis["dti"]
	
	V=0
	A=[]
	B=[]
	x=0
	activations=0
	for i in range(N):
		t=0
		W=0
		activate=False
		while (t<=maturity and activate==False):
			W=W+np.sqrt(1/252)*np.random.normal()
			R=r0*np.exp((rd-rf-volatility**2/2)*t)*np.exp(volatility*W)
			#print("rd,rf,volatility,maturity-t,R,strike,barrier")
			#print(rd,rf,volatility,maturity-t,R,strike,barrier)
			#print("vanilla price:",vanilla_call_option(rd,rf,volatility,maturity-t,R,strike))
			
			if (R>=barrier):
				activate=True
				activations=activations+1
				#print(t,A[-1])
			
			t=t+1/252
		
		if activate==True:
			while (t<maturity):
				W=W+np.random.normal()*np.sqrt(1/252)
				t=t+1/252
			R=r0*np.exp((rd-rf-volatility**2/2)*t)*np.exp(volatility*W)
			V=V+max(0,R-strike)/N*np.exp(-rd*maturity)
			
	#print("Activation probability",activations/N)
	return V

#A function to retrieve the prices of a pair of options
#r12:original FX rate
#r1:domestic rate
#r2:foreign rate
#m:drift of the FX rate
#s:the volatility of the FX rate
#q:determines on how many sigmas the barrier and strike are calculated
#time_axis:container used to manipulate time
#N:number of samples
def get_barriers(r1,r2,r12,m,s,q,fund_dates,time_axis,N):
	bput=[]
	bcall=[]
	for d in fund_dates[1:]:
	#Here we just calculate the value of each option, if the nominal value was 1

		T=time_axis['dtm'][to_workday(d)]
		print("maturity:",T)
		
		barrier=r12*np.exp((m-s**2/2)*T)*np.exp(-q*s*np.sqrt(T))
		strike=r12*np.exp((m-s**2/2)*T)*np.exp(q*s*np.sqrt(T))
		x=evaluate_barrier_put_option(barrier,strike,r12,T,r1,r2,s,time_axis,N)
		print("Put value:",x)
		bput.append({"maturity":T, "barrier":barrier, "strike":strike, "value":x})
		
		barrier=r12*np.exp((m-s**2/2)*T)*np.exp(q*s*np.sqrt(T))
		strike=r12*np.exp((m-s**2/2)*T)*np.exp(-q*s*np.sqrt(T))
		x=evaluate_barrier_call_option(barrier,strike,r12,T,r1,r2,s,time_axis,N)
		print("Call value:",x)
		bcall.append({"maturity":T, "barrier":barrier, "strike":strike, "value":x})
		
		print('alternative')
		barrier=r12*np.exp((m-s**2/2)*T)*np.exp(-q*s*np.sqrt(T))
		strike=r12*np.exp((m-s**2/2)*T)*np.exp(q*s*np.sqrt(T))
		x=0
		for i in range(1000):
			R=-r12*np.exp((m-s**2/2)*T)*np.exp(np.random.normal()*s*np.sqrt(T))
			M=(R+np.sqrt(R**2-2*T*np.log(np.random.uniform(0,1))))/2
			x=max(0,R+strike)*(M>-barrier)+x
		print("call values:",x/1000)
		
		barrier=r12*np.exp((m-s**2/2)*T)*np.exp(q*s*np.sqrt(T))
		strike=r12*np.exp((m-s**2/2)*T)*np.exp(-q*s*np.sqrt(T))
		
		x=0
		for i in range(1000):
			R=r12*np.exp((m-s**2/2)*T)*np.exp(np.random.normal()*s*np.sqrt(T))
			M=(R+np.sqrt(R**2-2*T*np.log(np.random.uniform(0,1))))/2
			x=max(0,R-strike)*(M>barrier)+x
		print("call values:",x/1000)

		print()
	return (bput,bcall)