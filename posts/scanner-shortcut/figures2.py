"""Extra figures: what the model looks at, and how the scores move. Writes JSON that the charts read."""
import json, numpy as np
from experiment import *
def weights(p, seed):
    rng=np.random.default_rng(seed); X,d,s=sample(N_TRAIN,p,rng)
    mu,sd=X.mean(0),X.std(0)+1e-9; Z=(X-mu)/sd; K=Z@Z.T/300.0+1.0; a=np.zeros(len(d))
    for _ in range(25):
        f=K@a; q=1/(1+np.exp(-f)); w=np.maximum(q*(1-q),1e-6); z=f+(d-q)/w; a=np.linalg.solve(K+np.diag(1/w),z)
    return Z.T@a/300.0
out={}
for p in (.5,.7,.9): out[str(p)]=np.mean([weights(p,s) for s in range(10)],0).tolist()
rng=np.random.default_rng(1)
def mean_img(d,s,n=800): return make_images(np.full(n,d),np.full(n,s),rng).mean(0)
out["disease"]=(mean_img(1,0)-mean_img(0,0)).tolist(); out["scanner"]=(mean_img(0,1)-mean_img(0,0)).tolist()
rng=np.random.default_rng(0); X,d,s=sample(N_TRAIN,.9,rng); m=fit_logistic(X,d); Xe,de,se=sample(600,.5,rng); sc=m(Xe)
out["scores"]=[dict(score=float(a),d=int(b),s=int(c)) for a,b,c in zip(sc,de,se)]
json.dump(out,open("maps.json","w"))
