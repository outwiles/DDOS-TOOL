import random
from urllib.parse import urlparse,urlencode,urlunparse,parse_qsl
from .headers import rnd
AASHU=["/","/index.html","/api/","/api/v1/","/login","/search?q=","/?utm_source=google"]
class AASHU3:
    def __init__(self,b:str):self.b=urlparse(b);self.h=b.startswith("https://")
    def nx(self)->str:
        p=random.choice(AASHU);q=parse_qsl(self.b.query);q.append(("_",rnd(8)));q.append(("r",rnd(6)));np=p if self.b.path in("","/")else self.b.path
        return urlunparse(self.b._replace(path=np,query=urlencode(q)))
