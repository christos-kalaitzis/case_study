from datetime import date
from datetime import timedelta
from dateutil.relativedelta import *
#A few functions to accomodate the handling of dates; the names are self-explanatory
#A significant part of the running time is often spent on converting dates to time values; it would be more convenient to just have time values only.
def add_days(d,x):
	d=d+timedelta(days=x)
	t=0
	if (d.weekday()==5):
		d=d+timedelta(days=2)
		t=2
	if (d.weekday()==6):
		d=d+timedelta(days=1)
		t=1
	return d
	
def next_workday(d):
	if (d.weekday()!=5 and d.weekday!= 6):
		d=d+timedelta(days=1)
	if (d.weekday()==5):
		d=d+timedelta(days=2)
	if (d.weekday()==6):
		d=d+timedelta(days=1)
	return d

def previous_workday(d):
	if (d.weekday()!=5 and d.weekday!= 6):
		d=d+timedelta(days=-1)
	if (d.weekday()==5):
		d=d+timedelta(days=-1)
	if (d.weekday()==6):
		d=d+timedelta(days=-2)
	return d

def to_workday(d):
    if (d.weekday()==5):
        d=d+timedelta(days=2)
    if (d.weekday()==6):
        d=d+timedelta(days=1)
    return d

def add_months(d,x):
    d=d+relativedelta(months=x)
    if (d.weekday()==5):
        d=d+timedelta(days=2)
    if (d.weekday()==6):
        d=d+timedelta(days=1)
    return d

def add_years(d,x):
    return add_months(d,x*12)