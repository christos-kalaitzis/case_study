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
from itertools import product
#A function to calibrate the exchange rate volatility to a set of option prices C, with interest rates rd and rf
#The calibration is done my minimizing the mean squared error between predicted and historical option prices
#Volatility is a function of time, which we model as a polynomial

#C:array with option prices
#maturities:list with the maturities of said options
#rd:domestic rate
#rf:foreign rate
#learning_rate:learning rate of gradient descent; currently this is obsolete
#guess:initial guess for the volatility
def calibrate_vol(C,maturities,rd,rf,learning_rate,guess): #the learning rate is not needed, I just leave it if someone wants to play around.
	(m,n)=np.shape(C)
	
	
	#The degree of the volatility polynomial
	d=4
	#Number of iterations of the iterative refinement
	level=4
	#Granularity of the iterative refinement
	gran=5
	#The array of the maturities with respect to which the error is calculated
	included=[0,1,4,8,11,13,15,16,17]
	
	MSE=1
	xmin=[]
	xmin.append(guess)
	for i in range(d):
		xmin.append(0)
	
	for l in range(level):
		I=[]
		
		I.append(np.linspace(xmin[0]*(1-2**(-l-1)),xmin[0]*(1+2**(-l-1)),gran))
		for i in range(d):
			I.append(np.linspace((xmin[i+1]*(1-2**(-l-1))-10**(-l))/((i+1)**5/5),(xmin[i+1]*(1+2**(-l-1))+10**(-l))/((i+1)**5/5),gran))
		
		J=list(product(*I))
		for x in J:
			#print(x)
			E=0
			for i  in included:
				for j in range(n):
					T=maturities[i]
				
					s=0 #s is integral of simga^2(t) from 0 to T; for example if sigma(t) is constant we get the constant volatility model and s is sigma^2*T
					for d1 in range(d+1):
						for d2 in range(d+1):
							s=s+T**(d1+d2+1)/(d1+d2+1)*x[d1]*x[d2]
					d2=((rd-rf)*T-s/2)/(s**0.5)
					d1=d2+s**0.5
					price=norm.cdf(d1)*np.exp(-rf*T)-norm.cdf(d2)*np.exp(-rd*T)#Predicted option price
					E=E+(C[i][j]-price)**2/(len(included)*n)
			if E<=MSE:
				MSE=E
				xmin=x
			
	print(xmin)
	print("MSE",MSE)
	return xmin
	###########
	#The degree of the volatility polynomial
	#Gradient descent is tough to make work; feel free to try.
	d=2

	x=[]
	x.append(tf.Variable(0.05, name='x0', dtype=tf.float32))
	for i in range(d):
		x.append(tf.Variable(0, name='x'+str(i+1), dtype=tf.float32))
	
	#The array of the maturities with respect to which the error is calculated
	included=[0,1,4,8,11,13,15,16,17]

	E=tf.math.exp(-1000*(x[0]-10**(-5)))
	n=1
	for i in range(m-2):
		for j in range(n):
			T=maturities[i]
			
			s=0 #s is integral of simga^2(t) from 0 to T; for example if sigma(t) is constant we get the constant volatility model and s is sigma^2*T
			for d1 in range(d+1):
				for d2 in range(d+1):
					s=s+T**(d1+d2+1)/(d1+d2+1)*x[d1]*x[d2]
			
			d2=((rd-rf)*T-s/2)/(s**0.5)
			d1=d2+s**0.5
			price=tfp.distributions.Normal(0,1).cdf(d1)*np.exp(-rf*T)-tfp.distributions.Normal(0,1).cdf(d2)*np.exp(-rd*T)#Predicted option price
			E=E+(C[i][j]-price)**2/(len(included)*n)#Squared error between historic and predicted price

	#Having set up the error function, tensorflow takes care of differentiating and optimizing
	ret=[]
	optimizer = tf.train.GradientDescentOptimizer(learning_rate)
	train = optimizer.minimize(E)
	init = tf.initialize_all_variables()
	def optimize():
		with tf.Session() as session:
			session.run(init)
			fx=session.run(E)
			fprev=0
			print("starting at MSE:", fx)
			step=0
			while step<=30000 and  np.abs()>=10**(-7):
				fprev=fx
				session.run(train)
				fx=session.run(E)
				print("step ",step," MSE:", fx)
				step=step+1
				for i in range(d+1):
					print('Coefficient of degree ',i,':',session.run(x[i]))
			for i in range(d+1):
				print('Coefficient of degree ',i,':',session.run(x[i]))
			
			for i in range(m-2):
				s2t=0
				for d1 in range(d+1):
					for d2 in range(d+1):
						s2t=s2t+(maturities[i])**(d1+d2+1)/(d1+d2+1)*session.run(x[d1])*session.run(x[d2])
				print("Equivalent constant volatility at time",maturities[i],":",(s2t/maturities[i])**0.5)
			for i in range(d+1):
				ret.append(session.run(x[i]))
			session.close()
			return ret

	x_opt=optimize()
	return x_opt