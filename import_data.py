import pandas as pd

#This is just some data importing and cleaning
def import_data():
	market_data=pd.read_excel(r'data.xls')

	market_data.rename(columns={"Unnamed: 1":"Date"},inplace=True)
	market_data.drop("Unnamed: 0",axis=1,inplace=True)


	Spot={"EURUSD":[]}
	Forward={"EURUSD":{},"GBPUSD":{},"EURGBP":{}}
	Imp_vol={"EURUSD":{},"GBPUSD":{},"EURGBP":{}}
	Yield={"EUR":{},"USD":{},"GBP":{}}
	Swaption={"EUR":{},"USD":{},"GBP":{}}

	for c in market_data.columns:
		if c[0:3]=='Dat':
			market_dates=market_data[c][7:].tolist()
		if c[0:3]=='Spo':
			Spot[market_data[c][0]]=market_data[c][7:].tolist()
			s="Spot "+market_data[c][0]
			market_data.rename(columns={c:s},inplace=True)
			market_data[s]=market_data[s].apply(pd.to_numeric,errors='coerce')
		if c[0:3]=='For':
			if market_data[c][1] in {"MAR","JUN","SEP","DEC"}:
				market_data.drop(c,axis=1,inplace=True)
			else:
				Forward[market_data[c][0]][market_data[c][1]]=market_data[c][7:].tolist()
				s="Forward "+market_data[c][0]+" "+market_data[c][1]
				market_data.rename(columns={c:s},inplace=True)
				market_data[s]=market_data[s].apply(pd.to_numeric,errors='coerce')
		if c[0:3]=='Imp':
			maturity=market_data[c][1]
			if maturity=='ON':
				T=1/252
			if 'W' in maturity:
				T=int(maturity[0:-1])/52
			if 'M' in maturity:
				T=int(maturity[0:-1])/12
			if 'Y' in maturity:
				T=int(maturity[0:-1])
			Imp_vol[market_data[c][3][0:6]][T]=market_data[c][7:].tolist()
			s="Implied Volatility "+market_data[c][3][0:6]+" "+market_data[c][1]
			market_data.rename(columns={c:s},inplace=True)
			market_data[s]=market_data[s].apply(pd.to_numeric,errors='coerce')
		if c[0:3]=='Yie':
			Yield[market_data[c][0]][market_data[c][1]]=market_data[c][7:].tolist()
			s="Yield curve "+market_data[c][0]+" "+market_data[c][1]
			market_data.rename(columns={c:s},inplace=True)
			market_data[s]=market_data[s].apply(pd.to_numeric,errors='coerce')
		if c[0:3]=='Swa':
			Swaption[market_data[c][0]][market_data[c][1]]=market_data[c][7:].tolist()
			s="Swaption "+market_data[c][0]+" "+market_data[c][1]
			market_data.rename(columns={c:s},inplace=True)
			market_data[s]=market_data[s].apply(pd.to_numeric,errors='coerce')
			

	market_data.drop(range(7),axis=0,inplace=True)
	#####################
	fund_data=pd.read_excel(r'fund.xls')
	fund_dates=fund_data['Date'].tolist()
	fund_USD=fund_data['USD flow'].tolist()
	fund_Euro=fund_data['Euro flow'].tolist()
	fund_GBP=fund_data['GBP flow'].tolist()
	##########################
	market={}
	market["dates"]=market_dates
	market["data"]=market_data
	market["Spot"]=Spot
	market["Forward"]=Forward
	market["Imp_vol"]=Imp_vol
	market["Yield"]=Yield
	market["Swaption"]=Swaption
	
	fund={}
	fund["data"]=fund_data
	fund["dates"]=fund_dates
	fund["USD"]=fund_USD
	fund["Euro"]=fund_Euro
	fund["GBP"]=fund_GBP
	return (market,fund)