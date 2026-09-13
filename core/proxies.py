import asyncio
from pathlib import Path
import httpx
from .config import AASHU2,AASHU3,AASHU6,AASHU10,AASHU11,AASHU12,AASHU13,AASHU14
def nrm(l:str):
    l=l.strip()
    if not l or l.startswith("#"):return None
    if "://" not in l:l="http://"+l
    s=l.split("://",1)[0].lower()
    if s not in("http","https","socks4","socks5"):return None
    try:
        p=httpx.URL(l)
        if not p.host or not p.port:return None
    except Exception:return None
    return l
async def prb(p:str,t:str)->bool:
    try:
        async with httpx.AsyncClient(proxy=p,timeout=AASHU3,verify=AASHU11,follow_redirects=AASHU12,http2=AASHU10 and t.startswith("https://"))as c:
            r=await c.get(t);return r.status_code>0
    except Exception:return False
class AASHU:
    def __init__(self,p:str,mf:int=AASHU6):self.p=Path(p);self.mf=mf;self.r=[];self.fl={};self.i=0;self.lk=asyncio.Lock()
    def ld(self,h:bool=False):
        if not self.p.exists():raise FileNotFoundError(f"proxy file missing: {self.p}")
        raw=self.p.read_text().splitlines()
        good=[];bad=0;seen=set()
        for ln in raw:
            n=nrm(ln)
            if n is None:
                if ln.strip() and not ln.strip().startswith("#"):bad+=1
                continue
            if AASHU13:
                if n in seen:continue
                seen.add(n)
            good.append(n)
        self.r=good
        return len(good),bad
    async def nx(self):
        async with self.lk:
            if not self.r:return None
            for _ in range(len(self.r)):
                u=self.r[self.i%len(self.r)];self.i+=1
                if self.fl.get(u,0)<self.mf:return u
            return None
    async def fa(self,u:str):
        async with self.lk:self.fl[u]=self.fl.get(u,0)+1
    async def ok(self,u:str):
        async with self.lk:self.fl[u]=0
    def al(self)->int:return sum(1 for u in self.r if self.fl.get(u,0)<self.mf)
    async def flt(self,t:str,c:int=AASHU2)->int:
        if not self.r:return 0
        if len(self.r)>AASHU14:
            print(f"  list size {len(self.r)} exceeds probe threshold {AASHU14}, skipping probe")
            return len(self.r)
        s=asyncio.Semaphore(c);g=[];d=0;tot=len(self.r)
        async def ck(p:str):
            nonlocal d
            async with s:
                o=await prb(p,t);d+=1
                if o:g.append(p)
                if d%500==0:print(f"  probed {d}/{tot} | alive so far: {len(g)}")
        await asyncio.gather(*(ck(p) for p in self.r),return_exceptions=True)
        self.r=g;self.fl.clear();return len(g)
