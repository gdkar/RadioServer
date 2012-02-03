import EasyDTMF

class DTMFBuffer:
    def __init__(self):
        self.output=""
        self.blanks=0
        self.seen=0
        self.last=''
        self.valid_seen=False
        self.wrote=False
    def update(self,X,RATE):
        self.valid_seen=False
        s=EasyDTMF.DTMF(X,RATE)
        if s==None:
            self.blanks+=1
            if self.blanks>2:
                self.wrote=False
                self.seen=0
        else:
            self.blanks=0
            if s==self.last: self.seen+=1
            else: self.seen=1
            if self.seen>=2 and not self.wrote:
                self.wrote=True
                self.output+=s
                self.valid_seen=True
            self.last=s
    def get(self):
        return self.output
    def trig(self):
        return self.valid_seen
    def pop(self):
        if len(self.output)>0:
            s=self.output[0]
            self.output=self.output[1:]
            return s
        return '' 
    def isempty(self):
        return self.output==""
        
