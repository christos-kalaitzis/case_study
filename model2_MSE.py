import matplotlib.pyplot as plt
import numpy as np
from vanilla import *
from model2_poly import *

def plot_vol(r_name,rd,rf,a,C,maturities,m,n):
	x=np.linspace(1/252,5,100)
	plt.plot(x,np.abs(poly(x,a)),color='b')
	for i in maturities[0:-2]:
		plt.plot(i,C[i][-1]/100,marker="x",color='r')
	plt.ylabel("Volatility")
	plt.xlabel("Time")
	plt.title(str(r_name+" instantaenous volatility as a function of time"))
	plt.show()
	
	plt.plot(x,np.abs(poly_square_int(x,a)),color='b')
	for i in maturities[0:-2]:
		plt.plot(i,C[i][-1]/100,marker="x",color='r')
	plt.xlabel("Time")
	plt.ylabel("Volatility")
	plt.title(str(r_name+" equivalent volatility as a function of time"))
	plt.show()
	
	
	
def MSE(rd,rf,s,C,maturities,m,n):
	E=0
	for i in range(m):
		for j in range(n):
			C_predicted=vanilla_atm_call_option(rd,rf,s,maturities[i])
			E=E+(C_predicted-C[i][j])**2/(m*n)
	return E