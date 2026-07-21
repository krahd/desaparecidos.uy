from __future__ import annotations
import argparse, hashlib, json, math, random, time
from pathlib import Path
import networkx as nx
import numpy as np
from PIL import Image
from skimage import color, data, metrics

ROOT=Path(__file__).resolve().parent
SIZE=200; TILE=20; NS=128; REUSE=8
TARGET_IDS=list(range(6)); SEEDS=[11,17,23]; CAPS=[0,4,2,1]; METHODS=['random','rgb','full6']

def rgb(a):
 a=np.asarray(a)
 if a.ndim==2:a=np.repeat(a[:,:,None],3,2)
 if a.shape[2]==4:a=a[:,:,:3]
 if a.dtype==bool:a=(a*255).astype(np.uint8)
 elif a.dtype!=np.uint8:a=(np.clip(a,0,1)*255).astype(np.uint8) if a.max(initial=0)<=1 else np.clip(a,0,255).astype(np.uint8)
 return Image.fromarray(a,'RGB')

def square(im,n):
 w,h=im.size;s=min(w,h);l=(w-s)//2;t=(h-s)//2
 return im.crop((l,t,l+s,t+s)).resize((n,n),Image.Resampling.LANCZOS)

def desc(p,method='full6'):
 a=np.asarray(Image.fromarray(p).resize((32,32),Image.Resampling.BILINEAR),np.float32)
 m=a.mean((0,1))/255.
 if method=='rgb':return m.astype(np.float32)
 l=(.2126*a[:,:,0]+.7152*a[:,:,1]+.0722*a[:,:,2])/255.
 return np.r_[m,l.std(),np.abs(np.diff(l,axis=1)).mean(),np.abs(np.diff(l,axis=0)).mean()].astype(np.float32)

def targets(n=SIZE, ids=TARGET_IDS):
 l=data.lfw_subset();return [square(rgb((np.clip(l[i],0,1)*255).astype(np.uint8)),n) for i in ids]

def face_sources(n=NS,size=100,start=20):
 l=data.lfw_subset();return [square(rgb((np.clip(l[i],0,1)*255).astype(np.uint8)),size) for i in range(start,start+n)]

def place_sources(n=NS,size=100):
 bases=[data.rocket(),data.hubble_deep_field(),data.brick(),data.grass(),data.gravel(),data.moon(),data.coffee(),data.colorwheel()]
 bases=[np.asarray(rgb(x)) for x in bases];rng=np.random.default_rng(4107);out=[]
 for i in range(n):
  b=bases[i%8];h,w=b.shape[:2];lo=max(100,min(h,w)//5);hi=max(lo+1,min(h,w)//2)
  side=int(rng.integers(lo,hi));y=int(rng.integers(0,h-side+1));x=int(rng.integers(0,w-side+1))
  out.append(Image.fromarray(b[y:y+side,x:x+side]).resize((size,size),Image.Resampling.LANCZOS))
 return out

def fragments(srcs,method,tile=TILE):
 fs=[];ds=[];ss=[]
 for si,im in enumerate(srcs):
  a=np.asarray(im)
  for y in range(0,a.shape[0]-tile+1,tile):
   for x in range(0,a.shape[1]-tile+1,tile):
    p=a[y:y+tile,x:x+tile];fs.append(p);ds.append(desc(p,method));ss.append(si)
 return np.stack(fs),np.stack(ds),np.array(ss)

def run(target,tid,kind,pack,method,cap,seed):
 f,d,s=pack;order=list(range(len(f)));random.Random(seed+tid).shuffle(order);f,d,s=f[order],d[order],s[order]
 fu=np.zeros(len(f),int);su=np.zeros(NS,int);av=np.ones(len(f),bool);a=np.asarray(target);o=np.empty_like(a);grid=np.empty((SIZE//TILE,SIZE//TILE),int);obj=0.
 for gy,y in enumerate(range(0,SIZE,TILE)):
  for gx,x in enumerate(range(0,SIZE,TILE)):
   if method=='random':
    aa=np.flatnonzero(av);j=int(aa[(seed*1009+(gy*10+gx)*9176+tid*37)%len(aa)])
   else:
    q=desc(a[y:y+TILE,x:x+TILE],method);dist=np.linalg.norm(d-q,axis=1);dist[~av]=np.inf;j=int(np.argmin(dist));obj+=float(dist[j])
   o[y:y+TILE,x:x+TILE]=f[j];grid[gy,gx]=s[j];fu[j]+=1;su[s[j]]+=1
   if fu[j]>=REUSE:av[j]=False
   if cap and su[s[j]]>=cap:av[s==s[j]]=False
 ref=a.astype(np.float32)/255.;prd=o.astype(np.float32)/255.;counts=su[su>0].astype(float);shares=counts/counts.sum()
 return {'target':tid,'source_kind':kind,'method':method,'cap':cap,'seed':seed,'ssim':float(metrics.structural_similarity(ref,prd,channel_axis=2,data_range=1.)),'deltaE00':float(color.deltaE_ciede2000(color.rgb2lab(ref),color.rgb2lab(prd)).mean()),'sources':int(len(counts)),'hhi':float((shares**2).sum()),'max_share':float(shares.max()),'objective':obj},grid,np.asarray(o)

def proxy():
 ts=targets();corpora={'faces':face_sources(),'places':place_sources()};packs={(k,m):fragments(v,m) for k,v in corpora.items() for m in METHODS};rows=[];parent=[]
 for kind in corpora:
  for method in METHODS:
   for cap in CAPS:
    for tid,t in zip(TARGET_IDS,ts):
     imgs=[]
     for seed in SEEDS:
      r,g,o=run(t,tid,kind,packs[(kind,method)],method,cap,seed);rows.append(r);imgs.append(o.tobytes())
      if kind=='places' and method=='full6':
       c=np.bincount((g%8).ravel(),minlength=8).astype(float);sh=c/c.sum();parent.append({'target':tid,'cap':cap,'seed':seed,'parent_hhi':float((sh**2).sum()),'max_parent_share':float(sh.max())})
     if method=='full6' and len(set(imgs))!=1:raise AssertionError('descriptor changed across seeds')
 def agg(kind,method,cap,key):
  v=[r[key] for r in rows if r['source_kind']==kind and r['method']==method and r['cap']==cap];return float(np.mean(v))
 puniq={(r['target'],r['cap']):r for r in parent}
 ph=[r['parent_hhi'] for (t,c),r in puniq.items() if c==1];pm=[r['max_parent_share'] for (t,c),r in puniq.items() if c==1]
 return rows,{'runs':len(rows),'faces_ssim_unlimited':agg('faces','full6',0,'ssim'),'faces_ssim_cap1':agg('faces','full6',1,'ssim'),'places_ssim_unlimited':agg('places','full6',0,'ssim'),'places_ssim_cap1':agg('places','full6',1,'ssim'),'faces_hhi_unlimited':agg('faces','full6',0,'hhi'),'faces_hhi_cap1':agg('faces','full6',1,'hhi'),'places_row_hhi_unlimited':agg('places','full6',0,'hhi'),'places_row_hhi_cap1':agg('places','full6',1,'hhi'),'places_parent_hhi_cap1_mean':float(np.mean(ph)),'places_parent_hhi_cap1_sd':float(np.std(ph,ddof=1)),'places_max_parent_share_cap1':float(np.mean(pm))}

def exact_comparison():
 n=32;size=100;tile=20;reuse=2;ids=[0,1];caps=[0,2,1]
 ts=targets(size,ids);corpora={'faces':face_sources(n,size),'places':place_sources(n,size)};rows=[]
 for kind,srcs in corpora.items():
  f,d,s=fragments(srcs,'full6',tile)
  for tid,t in zip(ids,ts):
   a=np.asarray(t);td=[]
   for y in range(0,size,tile):
    for x in range(0,size,tile):td.append(desc(a[y:y+tile,x:x+tile]))
   dist=np.linalg.norm(np.stack(td)[:,None,:]-d[None,:,:],axis=2)
   for cap in caps:
    order=list(range(len(f)));random.Random(17+tid).shuffle(order);oa=np.array(order);rd=dist[:,oa];rs=s[oa];fu=np.zeros(len(f),int);su=np.zeros(n,int);av=np.ones(len(f),bool);gobj=0.
    for i in range(len(td)):
     cur=rd[i].copy();cur[~av]=np.inf;j=int(np.argmin(cur));gobj+=float(cur[j]);fu[j]+=1;src=int(rs[j]);su[src]+=1
     if fu[j]>=reuse:av[j]=False
     if cap and su[src]>=cap:av[rs==src]=False
    G=nx.DiGraph();G.add_node('a',demand=-len(td));G.add_node('z',demand=len(td));ec=len(td) if cap==0 else cap
    for si in range(n):G.add_edge('a',f's{si}',capacity=ec,weight=0)
    for j in range(len(f)):
     fn=f'f{j}';G.add_edge(f's{int(s[j])}',fn,capacity=reuse,weight=0)
     for i in range(len(td)):G.add_edge(fn,f't{i}',capacity=1,weight=int(round(float(dist[i,j])*1_000_000)))
    for i in range(len(td)):G.add_edge(f't{i}','z',capacity=1,weight=0)
    flow=nx.min_cost_flow(G);oobj=0.
    for j in range(len(f)):
     for i in range(len(td)):
      if flow[f'f{j}'].get(f't{i}',0):oobj+=float(dist[i,j])
    rows.append({'kind':kind,'target':tid,'cap':cap,'objective_gap_percent':100*(gobj-oobj)/oobj})
 return {'faces_gap_cap1':float(np.mean([r['objective_gap_percent'] for r in rows if r['kind']=='faces' and r['cap']==1])),'places_gap_cap1':float(np.mean([r['objective_gap_percent'] for r in rows if r['kind']=='places' and r['cap']==1]))}

def audit():
 rng=np.random.default_rng(77);target=rng.integers(0,256,(100,100,3),dtype=np.uint8);srcs=[]
 for i in range(30):
  a=rng.integers(0,256,(60,60,3),dtype=np.uint8);srcs.append((f's{i:03}',a,hashlib.sha256(a.tobytes()).hexdigest()))
 def asm(items):
  fs=[];ds=[];ss=[]
  for k,(_,a,_) in enumerate(items):
   for y in range(0,60,20):
    for x in range(0,60,20):fs.append(a[y:y+20,x:x+20]);ds.append(desc(a[y:y+20,x:x+20]));ss.append(k)
  f=np.stack(fs);d=np.stack(ds);s=np.array(ss);fu=np.zeros(len(f),int);su=np.zeros(len(items),int);av=np.ones(len(f),bool);out=np.empty_like(target);trace=[]
  for y in range(0,100,20):
   for x in range(0,100,20):
    q=desc(target[y:y+20,x:x+20]);di=np.linalg.norm(d-q,axis=1);di[~av]=np.inf;j=int(np.argmin(di));out[y:y+20,x:x+20]=f[j];fu[j]+=1;su[s[j]]+=1;trace.append(items[s[j]][0])
    if fu[j]>=8:av[j]=False
    if su[s[j]]>=1:av[s==s[j]]=False
  return out,trace
 o1,t1=asm(srcs);o2,t2=asm(srcs);used=t1[0];o3,t3=asm([s for s in srcs if s[0]!=used])
 return {'deterministic_replay':o1.tobytes()==o2.tobytes() and t1==t2,'dependency_query_hits':t1.count(used),'excluded_source_absent':used not in t3,'regenerated_output_changed':o1.tobytes()!=o3.tobytes()}

EXPECTED={'runs':432,'faces_ssim_unlimited':0.409427,'faces_ssim_cap1':0.371959,'places_ssim_unlimited':0.283195,'places_ssim_cap1':0.231817,'faces_hhi_unlimited':0.0266,'faces_hhi_cap1':0.01,'places_row_hhi_unlimited':0.0619,'places_row_hhi_cap1':0.01,'places_parent_hhi_cap1_mean':0.1459,'places_parent_hhi_cap1_sd':0.0054,'places_max_parent_share_cap1':0.16,'faces_gap_cap1':15.681,'places_gap_cap1':28.126}

def close(a,b,t=.0006):
 if not np.isclose(a,b,atol=t,rtol=0):raise AssertionError((a,b))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',default='benchmark-results.json');args=ap.parse_args()
 _,p=proxy();e=exact_comparison();a=audit();out={**p,**e,'audit':a}
 for k,v in EXPECTED.items():close(float(out[k]),float(v),.011 if 'gap' in k else .0006)
 if not all(a.values()):raise AssertionError(a)
 (ROOT/args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print(json.dumps(out,indent=2,sort_keys=True));print('All reported values verified.')
if __name__=='__main__':main()
