def poly(x,a):
	d=len(a)-1
	v=0
	for i in range(d+1):
		v=v+x**i*a[i]
	return v
	
def poly_square_int(x,a):
	d=len(a)-1
	s2t=0
	for d1 in range(d+1):
		for d2 in range(d+1):
			s2t=s2t+x**(d1+d2+1)/(d1+d2+1)*a[d1]*a[d2]
	return (s2t/x)**0.5