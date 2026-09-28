#!/usr/bin/env python3
"""Evaluate supplied, REAL TorchScript steganalysis checkpoint on paired cover/stego images.
NO pretrained SRM, SRNet, ERANet, or SiaStegNet checkpoints are shipped or invented.
The checkpoint is responsible for any SRM/maxSRMd2 feature extraction it requires.
"""
import argparse, csv, hashlib, math, sys
from pathlib import Path

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        while True:
            b=f.read(1<<20)
            if not b: break
            h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--model',required=True,help='Real trained TorchScript checkpoint')
    ap.add_argument('--pairs',required=True,help='CSV: image_id,cover_path,stego_path')
    ap.add_argument('--out',required=True)
    ap.add_argument('--detector',required=True)
    ap.add_argument('--variant',required=True)
    ap.add_argument('--bpp',type=float,required=True)
    ap.add_argument('--seed',type=int,required=True)
    ap.add_argument('--threshold',type=float,default=0.5)
    a=ap.parse_args()
    try:
        import numpy as np
        import torch
        from PIL import Image
        from skimage.metrics import structural_similarity
    except ImportError as e:
        ap.error('Need verified runtime dependencies; see reproduction/requirements.txt: '+str(e))
    if not Path(a.model).is_file(): ap.error('Checkpoint not found; cannot use placeholder weights')
    model=torch.jit.load(a.model,map_location='cpu').eval() # Load only trusted checkpoints.
    def predict(path):
        im=np.array(Image.open(path).convert('L'),dtype=np.uint8)
        x=torch.from_numpy(im.astype('float32')/255.0)[None,None]
        with torch.inference_mode(): score=model(x)
        if isinstance(score,(tuple,list)): score=score[0]
        val=score.reshape(-1)
        if val.numel()==2: prob=torch.softmax(val,dim=0)[1].item()
        elif val.numel()==1: prob=torch.sigmoid(val[0]).item()
        else: raise ValueError('Detector must return [1,2] logits or [1] binary logit')
        return im,prob
    with open(a.pairs,newline='',encoding='utf-8') as f:
        reader=csv.DictReader(f)
        if not {'image_id','cover_path','stego_path'}.issubset(reader.fieldnames or []):
            ap.error('Paired CSV must contain image_id,cover_path,stego_path')
        pairs=list(reader)
    if not pairs: ap.error('Empty image-pair list; refusing fabricated evaluation')
    if len({r['image_id'] for r in pairs})!=len(pairs): ap.error('Duplicated image IDs')
    fp=tn=fn=tp=0; fidelity=[];seen=[]
    for r in pairs:
        cp=Path(r['cover_path']);sp=Path(r['stego_path'])
        if not cp.is_file() or not sp.is_file(): raise FileNotFoundError(f'Missing image for {r["image_id"]}')
        ca,pc=predict(cp);sa,ps=predict(sp)
        if ca.shape!=sa.shape: raise ValueError(f'Shape mismatch: {r["image_id"]}')
        if pc>=a.threshold:fp+=1
        else:tn+=1
        if ps>=a.threshold:tp+=1
        else:fn+=1
        mse=np.mean((ca.astype(np.float64)-sa.astype(np.float64))**2)
        fidelity.append((float('inf') if mse==0 else 10*math.log10(255*255/mse),
                         float(structural_similarity(ca,sa,data_range=255))))
        seen.append(r['image_id'])
    pe=50*(fp/(fp+tn)+fn/(fn+tp))
    cols=['variant','detector','bpp','seed','psnr','ssim','fp','tn','fn','tp','split_sha256','model_sha256','pe_percent','n_pairs','provenance']
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
        w.writerow({'variant':a.variant,'detector':a.detector,'bpp':a.bpp,'seed':a.seed,
           'psnr':np.mean([i[0] for i in fidelity]),'ssim':np.mean([i[1] for i in fidelity]),
           'fp':fp,'tn':tn,'fn':fn,'tp':tp,'split_sha256':sha(a.pairs),'model_sha256':sha(a.model),
           'pe_percent':f'{pe:.6f}','n_pairs':len(pairs),'provenance':'measured_by_supplied_torchscript_checkpoint'})
    print(f'MEASURED n_pairs={len(pairs)} FP={fp} TN={tn} FN={fn} TP={tp} P_E={pe:.4f}%')
    print('CAUTION: evaluation quality depends on verified checkpoint, train/test separation, normalization and detector protocol.')
if __name__=='__main__':main()
