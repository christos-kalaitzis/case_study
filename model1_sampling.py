import numpy as np
from vanilla import *

#A simple function to transform implied volatilities into option prices
#imp_vol:the implied volatilities we are given
#rd:domestic rate
#rf:foreign rate
#m:how many volatilities we take into account
#n:how many days back we go
def sample_prices(imp_vol,maturities,rd,rf,m,n):
	S=np.zeros(shape=(m,n))
	C=np.zeros(shape=(m,n))
	maturities=list(imp_vol.keys())
	for i in range(m):
		for j in range(n):
			S[i][j]=imp_vol[maturities[i]][-j-1]
			C[i][j]=vanilla_atm_call_option(rd,rf,S[i][j]/100,maturities[i])
	return (C,S)

#Sample a single path of the 2 Brownian motions associated with the exchange rates
def sample_path(model,time_axis):
	m13=model["m13"]
	s13=model["s13"]
	r13_0=model["r13_0"]
	m21=model["m21"]
	s21=model["s21"]
	r21_0=model["r21_0"]
	m32=model["m32"]
	s32=model["s32"]
	r32_0=model["r32_0"]
	
	#Some variables just introduced for convenience
	dtm=time_axis["dtm"]
	mti=time_axis["mti"]
	itd=time_axis["itd"]
	dti=time_axis["dti"]

	rho_13_21=(s32**2-s13**2-s21**2)/(2*s13*s21)

	N=len(dtm.keys())

	W1=np.zeros(N)
	Wh=np.zeros(N)
	W2=np.zeros(N)
	sample_13=np.zeros(N)
	norm_13=np.zeros(N)
	sample_21=np.zeros(N)
	
	#We could also write down the covariance matrices of the brownian motions and sample using Cholesky decomposition, but that would be slower
	for i in range(1,N):
	#Sample one realization of two independent Brownian motions
		W1[i]=W1[i-1]+np.sqrt(1/252)*np.random.normal()
		Wh[i]=Wh[i-1]+np.sqrt(1/252)*np.random.normal()
		#Extract a Brownian motion that is correlated with W1
		W2[i]=rho_13_21*W1[i]+np.sqrt(1-rho_13_21**2)*Wh[i]

	for i in range(N):
	#Extract the realization exchange rates from the realization of the Brownian motions
		sample_13[i]=r13_0*np.exp((m13-s13**2/2)*dtm[itd[i]])*np.exp(s13*W1[i])
		norm_13[i]=r13_0*np.exp(s13*W1[i])
		sample_21[i]=r21_0*np.exp((m21-s21**2/2)*dtm[itd[i]])*np.exp(s21*W2[i])
	return (sample_13,sample_21)