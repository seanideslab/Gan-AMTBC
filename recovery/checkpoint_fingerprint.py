#!/usr/bin/env python3
"""Inspect a recovered .pth candidate against the nine shape fingerprints in a lab note.

By default, only file metadata and the ZIP member directory are inspected: no pickle is loaded.
Use --trusted-weights-only ONLY on a locally sourced checkpoint you trust; weights_only
reduces arbitrary-code risks but does not eliminate denial-of-service or other risks.
A tensor-shape match does NOT validate original experimental identity or performance.
"""
import argparse, hashlib, json, zipfile
from pathlib import Path

NOTE = Path(__file__).with_name('pth_candidate_fingerprint.json')

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for buf in iter(lambda: f.read(1024*1024), b''):h.update(buf)
    return h.hexdigest()

def compare_shapes(observed,expected):
    # Allow unambiguous common DataParallel and generator name prefixes, never fuzzy shapes.
    pref=('module.','model.','generator.','netG.')
    found={}
    for key,exp in expected.items():
        matches=[]
        for actual,shape in observed.items():
            norm=actual
            while any(norm.startswith(p) for p in pref):
                norm=next(norm[len(p):] for p in pref if norm.startswith(p))
            if norm == key: matches.append((actual,list(shape)))
        if not matches:found[key]={'status':'MISSING','expected':exp}
        elif len(matches)>1:found[key]={'status':'AMBIGUOUS','expected':exp,'matches':matches}
        else:
            name,sh=matches[0]
            found[key]={'status':'MATCH' if sh==exp else 'SHAPE_MISMATCH',
                        'actual_key':name,'observed':sh,'expected':exp}
    return found

def flatten_state_dict(obj):
    import torch
    if isinstance(obj,dict):
        for candidate in ('state_dict','model_state_dict','generator_state_dict','netG_state_dict','model','generator','netG','weights'):
            if candidate in obj and isinstance(obj[candidate],dict):
                return flatten_state_dict(obj[candidate])
        tensors={str(k):v for k,v in obj.items() if isinstance(v,torch.Tensor)}
        if tensors:return tensors
    raise ValueError('No conventional plain tensor state_dict found; do not execute custom classes')

def inspect(path:Path,allow_load:bool=False):
    note=json.loads(NOTE.read_text(encoding='utf-8'))
    out={'file_name':path.name,'file_size_bytes':path.stat().st_size,
         'sha256':sha256(path),'note_sha256':note['source_sha256'],
         'status':'FILE_FOUND_NOT_VERIFIED_AS_ORIGINAL',
         'expected_shape_keys':len(note['fingerprint'])}
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            out['zip_entry_count']=len(z.infolist())
            out['zip_member_names_sample']=[i.filename for i in z.infolist()[:12]]
    else:out['container_format']='non-ZIP or legacy Torch serialization'
    if allow_load:
        if path.stat().st_size>512*1024*1024:raise ValueError('File exceeds 512 MiB inspection limit')
        try:
            import torch
            raw=torch.load(path,map_location='cpu',weights_only=True)
            state=flatten_state_dict(raw)
            shapes={k:list(t.shape) for k,t in state.items()}
            out['number_of_tensor_keys']=len(state)
            out['number_of_tensor_elements']=sum(int(t.numel()) for t in state.values())
            out['key_shape_comparison']=compare_shapes(shapes,note['fingerprint'])
            out['matched_shape_keys']=sum(v['status']=='MATCH' for v in out['key_shape_comparison'].values())
            out['interpretation']='Shape matches identify a candidate only; not authentic experimental provenance.'
        except Exception as e:
            out['inspection_error']=type(e).__name__+': '+str(e)[:300]
            out['status']='NOT_INSPECTED_OR_NOT_COMPATIBLE'
    else:out['next_step']='Review source and hash; opt in with --trusted-weights-only to inspect tensor keys.'
    return out

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--checkpoint',type=Path,required=True)
    p.add_argument('--out',type=Path)
    p.add_argument('--trusted-weights-only',action='store_true',help='Explicit opt-in for weights_only Torch loading of your own trusted file')
    args=p.parse_args()
    if not args.checkpoint.is_file():p.error('checkpoint file does not exist')
    res=inspect(args.checkpoint,args.trusted_weights_only)
    serialized=json.dumps(res,indent=2,ensure_ascii=False)+'\n'
    if args.out:args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(serialized,encoding='utf-8')
    print(serialized)
if __name__=='__main__':main()
