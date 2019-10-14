import matplotlib.pyplot as plt
import numpy as np
from vanilla import *

def plot_MSE(r_name,rd,rf,s,C,maturities,m,n):
	print(r_name," volatility: ",s)
	print("Plotting MSE of option prices VS volatility to verify:")
	gx=np.linspace(max(0.001,s-0.1),s+0.1,100)
	gy=MSE(rd,rf,gx,C,maturities,m,n)
	plt.plot(gx,gy,color='b')
	plt.plot(s,MSE(rd,rf,s,C,maturities,m,n),marker="x",color='r')
	plt.xlabel(str(r_name+" volatility"))
	plt.ylabel("MSE")
	plt.title("MSE of predicted vs historical option prices as a function of volatility\n For perspective, min/avg/max option prices are\n"+'{:.2e}'.format(np.min(C))+"/"+'{:.2e}'.format(np.mean(C))+"/"+'{:.2e}'.format(np.max(C))+"\n optimum MSE="+'{:.2e}'.format(MSE(rd,rf,s,C,maturities,m,n)))
	plt.show()
	
def MSE(rd,rf,s,C,maturities,m,n):
	E=0
	for i in range(m):
		for j in range(n):
			C_predicted=vanilla_atm_call_option(rd,rf,s,maturities[i])
			E=E+(C_predicted-C[i][j])**2/(m*n)
	return E