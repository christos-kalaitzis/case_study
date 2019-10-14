import numpy as np
from scipy.stats import norm
from scipy import stats

#For all functions here:
#rd:domestic rate
#rf:foreign rate
#s:volatility
#T:maturity
#S:asset price
#K:strike

def vanilla_call_option(rd,rf,s,T,S,K):
	d2=(np.log(S/K)+(rd-rf-s**2/2)*T)/(s*np.sqrt(T))
	d1=d2+s*np.sqrt(T)
	x=norm.cdf(d1)*np.exp(-rf*T)*S-norm.cdf(d2)*np.exp(-rd*T)*K
	#print("C+K*r",x+K*np.exp(-rd*T))
	#print("P+S*r",vanilla_put_option(rd,rf,s,T,S,K)+np.exp(-rf*T)*S)
	return x

def vanilla_put_option(rd,rf,s,T,S,K):
	d2=(np.log(S/K)+(rd-rf-s**2/2)*T)/(s*np.sqrt(T))
	d1=d2+s*np.sqrt(T)
	x=(norm.cdf(d1)-1)*np.exp(-rf*T)*S-(norm.cdf(d2)-1)*np.exp(-rd*T)*K
	return x

#Here we are just reverting implied volatilities into actual option prices
#We are using at-the-money options, so strike=original rate; in this case we can normalize the original rate to 1 since the original rate only affects the price by a multiplicative factor
def vanilla_atm_call_option(rd,rf,s,T):
	d2=(rd-rf-s**2/2)*T/(s*np.sqrt(T))
	d1=d2+s*np.sqrt(T)
	x=norm.cdf(d1)*np.exp(-rf*T)-norm.cdf(d2)*np.exp(-rd*T)
	return x