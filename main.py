import asyncio,os,sys,time
from core import banner
from core.config import AASHU as CN
from core.proxies import AASHU as PRX
from core.runner import AASHU1 as RNR
IS_W=sys.platform.startswith("win")
def pmt(m:str,d=None)->str:
    s=f" [{d}]" if d is not None else ""
    v=input(f"{m}{s}: ").strip()
    return v if v else(d or "")
def gt()->dict:
    t=os.environ.get("AASHU_TARGET")or pmt("Target URL/IP")
    if not t:print("no target, exiting");sys.exit(1)
    if not t.startswith(("http://","https://")):t="https://"+t
    pe=os.environ.get("AASHU_PROXIES")
    if pe is not None:up=True;pf=pe
    else:
        a=pmt("Do you want to use proxies? (y/n)","n").lower();up=a.startswith("y")
        pf=pmt("Proxy file path","proxies.txt")if up else None
    return{"t":t,"up":up,"pf":pf}
async def mns(o:dict):
    r=None;t=o["t"]
    if o["up"]:
        r=PRX(o["pf"]);g,b=r.ld()
        print(f"loaded {g} proxies ({b} malformed/duplicates skipped)")
        if g==0:print("no usable proxies, exiting");return
        print(f"probing {g} proxies against {t}...")
        t0=time.time();a=await r.flt(t)
        print(f"probe done: {a}/{g} alive in {time.time()-t0:.1f}s")
        if a==0:print("no proxies survived the probe, exiting");return
    print(f"starting: target={t} concurrency={CN} (Ctrl+C to stop)");print()
    rn=RNR(t,r)
    try:rs=await rn.rn()
    except KeyboardInterrupt:rs={"sent":rn.s,"failed":rn.f}
    print(f"\nresult: {rs}")
def mn():
    if IS_W:asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    banner.rn();o=gt()
    try:asyncio.run(mns(o))
    except KeyboardInterrupt:print("\nstopped")
if __name__=="__main__":mn()
