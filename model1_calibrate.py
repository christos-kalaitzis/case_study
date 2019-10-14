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

#A function to calibrate the exchange rate volatility to a set of option prices C, with interest rates rd and rf
#The calibration is done my minimizing the mean squared error between predicted and historical option prices
#We use tensorflow to solve the minimization problem, because it offers automatic differentiation
#The optimization algorithm is gradient descent; since the problem is non-convex, choosing a good initial value is important. We choose an initial value in the range of the historic volatilities, and then the algorithm converges; a bad choice will result in unpredictable behavior.
#Due to the automatic differentiation, the running time is inflated. If we wanted this process to be faster, we would just hard-code the gradients and proceed with implementing gradient descent

#C:array with option prices
#maturities:list with the maturities of said options
#rd:domestic rate
#rf:foreign rate
#guess:initial guess for the volatility
def calibrate_vol(C,maturities,rd,rf,guess):
	(m,n)=np.shape(C)
	x = tf.Variable(guess, name='x', dtype=tf.float32)
	E=0

	for i in range(m):
		for j in range(n):
			T=maturities[i]
			d2=(rd-rf-x**2/2)*T/(x*np.sqrt(T))
			d1=d2+x*np.sqrt(T)
			price=tfp.distributions.Normal(0,1).cdf(d1)*np.exp(-rf*T)-tfp.distributions.Normal(0,1).cdf(d2)*np.exp(-rd*T) #Predicted option price
			E=E+(C[i][j]-price)**2/(m*n)#Squared error between historic and predicted price

#Having set up the error function, tensorflow takes care of differentiating and optimizing
	optimizer = tf.train.GradientDescentOptimizer(0.35)
	train = optimizer.minimize(E)
	init = tf.initialize_all_variables()
	def optimize():
		with tf.Session() as session:
			session.run(init)
			fx=session.run(E)
			fprev=0
			print("starting at", "x:", session.run(x), "MSE:", fx)
			step=0
			while np.abs(fx-fprev)>=10**(-10):
				fprev=fx
				session.run(train)
				fx=session.run(E)
				print("step", step, "x:", session.run(x), "MSE:", fx)
				step=step+1
			ret=session.run(x)
			session.close()
			return ret

	x_opt=optimize()
	return x_opt