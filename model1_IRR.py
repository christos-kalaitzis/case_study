from dateutil.relativedelta import *
from model1_sampling import *
from date_handling import *
from scipy.stats import norm
from scipy import stats
#The IRR formula demands that a certain function of x equates to 0 if x equals the IRR; the following function returns the residual of that function for a given x.
#x: attempted IRR value
#R: n+1-dimensional vector of investment returns; R[0] is the initial investment, expected to be a negative number
#T: n-dimensional vector of the return times
def IRR_residual(x,R,T): 
	y=0
	n=len(T)
	for i in range(n):
		t=relativedelta(T[i],T[0])
		y=y+R[i]/x**(t.years+t.months/12+t.days/252)
	return y

#A function to retrieve the IRR of a deterministic cash flow, in a single currency.
def IRR(R,T):
	l=1
	r=2
	x=(l+r)/2
	tol=10**(-3)
	fl=IRR_residual(l,R,T)
	fr=IRR_residual(r,R,T)
	df=fl-fr
	while (df>tol):
		x=(l+r)/2
		fx=IRR_residual(x,R,T)
		if (fx>0):
			l=x
			fl=fx
			df=fl-fr
		if (fx<=0):
			r=x
			fr=fx
			df=fl-fr
	return x
	

#A function to sample N values from the distribution of the IRR
def IRR_distribution(fund,model,N,time_axis):
	dates=fund['Date'].tolist()
	USD=fund['USD flow'].tolist()
	Euro=fund['Euro flow'].tolist()
	GBP=fund['GBP flow'].tolist()
	
	#We are just setting up some convenient names here
	dtm=time_axis["dtm"]
	mti=time_axis["mti"]
	itd=time_axis["itd"]
	dti=time_axis["dti"]
	
	sample_USD_Euro=[]
	sample_GBP_USD=[]
	irr=[]
	flow=[]
	for i in range(N):
	#At each iteration we sample a path, then we calculate the IRR on this path
		(sample1,sample2)=sample_path(model,time_axis)
		sample_USD_Euro.append(sample1)
		sample_GBP_USD.append(sample2)
		flow.append([])
		for j in range(len(dates)):
			d=to_workday(dates[j])
			flow[i].append(USD[j]+Euro[j]*sample_USD_Euro[i][dti[d]]+GBP[j]/sample_GBP_USD[i][dti[d]])
		irr.append(IRR(flow[i],dates))
		print(i+1,":",irr[i])
	
	return (irr,sample_USD_Euro,sample_GBP_USD)

#A function to sample N values from the distribution of the IRR, after having incorporated the barrier options
def IRR_distribution_hedged(fund,model,barriers,N,time_axis,nominal_ratio): #nominal ratio:determines the nominal value of each option in the foreign currency
	dates=fund['Date'].tolist()
	USD=fund['USD flow'].tolist()
	Euro=fund['Euro flow'].tolist()
	GBP=fund['GBP flow'].tolist()
	
	dtm=time_axis["dtm"]
	mti=time_axis["mti"]
	itd=time_axis["itd"]
	dti=time_axis["dti"]
	
	#Choosing the correct nominal values, so that the hedging strategy is self-financing
	for i in range(len(barriers["Euro call"])):
		if (barriers["Euro put"][i]["value"]<=barriers["Euro call"][i]["value"]):
			barriers["Euro put"][i]["nominal"]=Euro[i+1]/nominal_ratio
			barriers["Euro call"][i]["nominal"]=barriers["Euro put"][i]["nominal"]*barriers["Euro put"][i]["value"]/barriers["Euro call"][i]["value"]
		else:
			barriers["Euro call"][i]["nominal"]=Euro[i+1]/nominal_ratio
			barriers["Euro put"][i]["nominal"]=barriers["Euro call"][i]["nominal"]*barriers["Euro call"][i]["value"]/barriers["Euro put"][i]["value"]
		
		if (barriers["GBP put"][i]["value"]<=barriers["GBP call"][i]["value"]):
			barriers["GBP put"][i]["nominal"]=GBP[i+1]/nominal_ratio
			barriers["GBP call"][i]["nominal"]=barriers["GBP put"][i]["nominal"]*barriers["GBP put"][i]["value"]/barriers["GBP call"][i]["value"]
		else:
			barriers["GBP call"][i]["nominal"]=GBP[i+1]/nominal_ratio
			barriers["GBP put"][i]["nominal"]=barriers["GBP call"][i]["nominal"]*barriers["GBP call"][i]["value"]/barriers["GBP put"][i]["value"]
		

	
	sample_USD_Euro=[]
	sample_GBP_USD=[]
	irr=[]
	flow=[]
	for i in range(N):
	#At each iteration we sample a path, then we calculate the IRR on this path
		(sample1,sample2)=sample_path(model,time_axis)
		sample_USD_Euro.append(sample1)
		sample_GBP_USD.append(sample2)
		flow.append([])
		
		activate_put={}
		activate_call={}
		for b in barriers["Euro put"]:
			activate_put[b["maturity"]]=False
			
		for b in barriers["Euro call"]:
			activate_call[b["maturity"]]=False
			
		for b in barriers["GBP put"]:
			activate_put[b["maturity"]]=False
			
		for b in barriers["GBP call"]:
			activate_call[b["maturity"]]=False
		
		#Go through the path to see which barriers are activated
		for j in range(len(itd)):
			t=dtm[itd[j]]
			for b in barriers["Euro put"]:
				if sample1[j]<=b["barrier"]:
					activate_put[b["maturity"]]=True
			for b in barriers["Euro call"]:
				if sample1[j]>=b["barrier"]:
					activate_call[b["maturity"]]=True
			for b in barriers["GBP put"]:
				if sample1[j]<=b["barrier"]:
					activate_put[b["maturity"]]=True
			for b in barriers["GBP call"]:
				if sample1[j]>=b["barrier"]:
					activate_call[b["maturity"]]=True
		
		
		for j in range(len(dates)):
			d=to_workday(dates[j])
			flow[i].append(USD[j]+GBP[j]/sample_GBP_USD[i][dti[d]]+Euro[j]*sample_USD_Euro[i][dti[d]])
			
			#Add the cash flow of the activated barriers
			for b in barriers["Euro put"]:
				if b["maturity"]==dtm[d] and activate_put[b["maturity"]]==True:
					R=sample_USD_Euro[i][dti[d]]
					flow[i][-1]=flow[i][-1]+b["nominal"]*max(0,b["strike"]-R)
					
			for b in barriers["Euro call"]:
				if b["maturity"]==dtm[d] and activate_call[b["maturity"]]==True:
					R=sample_USD_Euro[i][dti[d]]
					flow[i][-1]=flow[i][-1]-b["nominal"]*max(0,R-b["strike"])
			
			for b in barriers["GBP put"]:
				if b["maturity"]==dtm[d] and activate_put[b["maturity"]]==True:
					R=1/sample_GBP_USD[i][dti[d]]
					flow[i][-1]=flow[i][-1]+b["nominal"]*max(0,b["strike"]-R)
					
			for b in barriers["GBP call"]:
				if b["maturity"]==dtm[d] and activate_call[b["maturity"]]==True:
					R=1/sample_GBP_USD[i][dti[d]]
					flow[i][-1]=flow[i][-1]-b["nominal"]*max(0,R-b["strike"])
					
		irr.append(IRR(flow[i],dates))
		print(i+1,":",irr[i])
	

	#plt.hist(irr,100,normed=True)
	#gx=np.linspace(1,1.3,100)
	#(mu,var)=stats.norm.fit(irr)
	#gy=stats.norm.pdf(gx,gy)
	#plt.show()
	return (irr,sample_USD_Euro,sample_GBP_USD)

