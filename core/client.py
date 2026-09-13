import httpx
from .config import AASHU4,AASHU5,AASHU10,AASHU11,AASHU12
class AASHU2:
    def __init__(self,h:bool):self.h=h;self.c={}
    def gt(self,p):
        k=p or "__direct__";cl=self.c.get(k)
        if cl is not None:return cl
        kw={"http2":AASHU10 and self.h,"verify":AASHU11,"follow_redirects":AASHU12,"timeout":httpx.Timeout(AASHU4,connect=AASHU5),"limits":httpx.Limits(max_connections=None,max_keepalive_connections=None)}
        if p:kw["proxy"]=p
        cl=httpx.AsyncClient(**kw);self.c[k]=cl;return cl
    async def cls(self):
        for cl in self.c.values():
            try:await cl.aclose()
            except Exception:pass
        self.c.clear()
