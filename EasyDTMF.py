import numpy
import math
import cmath
def detect_coefficient(X,RATE,FREQ):
    s_prev=0
    s_prev2=0
    norm_freq=FREQ*1./RATE
    coeff=math.cos(2*math.pi*norm_freq)
    for x in X:
        s=x/32768.+2*coeff*s_prev-s_prev2
        s_prev2=s_prev
        s_prev=s
    return s_prev2**2+s_prev**2-2*coeff*s_prev*s_prev2
def approx_coeff(X,RATE,FREQ):
    out=[]
    for i in range(-2,2):
       out.append(detect_coefficient(X,RATE,FREQ+i*2))
    return max(out) 

def DTMF(X,RATE):
    freqs=[697,778,852,941,1209,1336,1477,1633] 
    r=[approx_coeff(X,RATE,freqs[i]) for i in range(len(freqs))]
     
    row_col_ascii_codes = [["1","2","3","A"],["4","5","6","B"],["7","8","9","C"],["*","0","#","D"]]
    maxval=0.0
    row=0
    col=0
    see_digit=0
    max_index=0
    t=0
    i=0
    for i in range(4):
        if r[i]>maxval:
            maxval=r[i]
            row=i
    for i in range(4,8):
        if r[i]>maxval:
            maxval=r[i]
            col = i
    if True:
        see_digit=True

        if r[col]>r[row]:
            max_index = col
            if r[row]< (r[col]*0.016): 
                see_digit=False
        else:
            max_index=row
            if r[col]< (r[row]*0.016): 
                see_digit=False
            
        peak_count=0
        if r[max_index]>1.0e9:
            t = r[max_index]*0.063
        else:
            t = r[max_index] * 0.063
        for i in range(8):
            if r[i]>t:
                peak_count+=1
        if peak_count>2: 
            see_digit=False
        if see_digit: return row_col_ascii_codes[row][col-4]
        
    return None
