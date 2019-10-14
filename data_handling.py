import pandas as pd

def select_date(self,dat):
	return self.loc[self.Date==dat]

setattr(pd.core.frame.DataFrame,'select_date',select_date)