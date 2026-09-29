"""NEW reconstruction candidate, not recovered original weights or exact original architecture.
The one-channel head follows an unverified old note, NOT the paper's joint BM/H/L claim.
"""
from __future__ import annotations
import math
import torch
from torch import nn
from torch.nn import functional as F


def kaiming(model):
    for m in model.modules():
        if isinstance(m,nn.Conv2d):
            nn.init.kaiming_normal_(m.weight,mode='fan_in',nonlinearity='relu')
            if m.bias is not None:nn.init.zeros_(m.bias)
        if isinstance(m,nn.ConvTranspose2d):
            nn.init.kaiming_normal_(m.weight,mode='fan_in',nonlinearity='relu')
            if m.bias is not None:nn.init.zeros_(m.bias)


class ResidualBlock(nn.Module):
    def __init__(self,cin,cout):
        super().__init__()
        self.conv1=nn.Conv2d(cin,cout,3,padding=1)
        self.act1=nn.ReLU(inplace=True)
        self.conv2=nn.Conv2d(cout,cout,3,padding=1)
        self.shortcut=nn.Conv2d(cin,cout,1) if cin!=cout else nn.Identity()
        self.act2=nn.ReLU(inplace=True)
    def forward(self,x):
        return self.act2(self.conv2(self.act1(self.conv1(x)))+self.shortcut(x))

class AttentionGate(nn.Module):
    def __init__(self,g_ch,x_ch,mid):
        super().__init__()
        self.W_g=nn.Conv2d(g_ch,mid,1)
        self.W_x=nn.Conv2d(x_ch,mid,1)
        self.psi=nn.Conv2d(mid,1,1)
    def forward(self,g,x):
        return x*torch.sigmoid(self.psi(F.relu(self.W_g(g)+self.W_x(x))))

class UpBlock(nn.Module):
    def __init__(self,cin,cout,skip_ch):
        super().__init__()
        self.up=nn.ConvTranspose2d(cin,cout,2,2)
        self.att=AttentionGate(cout,skip_ch,max(cout//2,1))
        self.refine=ResidualBlock(cout+skip_ch,cout)
    def forward(self,x,skip):
        y=self.up(x)
        if y.shape[-2:]!=skip.shape[-2:]:
            y=F.interpolate(y,size=skip.shape[-2:],mode='bilinear',align_corners=False)
        return self.refine(torch.cat([y,self.att(y,skip)],1))

class CandidateAttentionResUNet(nn.Module):
    """Candidate 1->1 channel residual map. Defaults match nine reported shape fingerprints.
    Three stride-2 down blocks + three up blocks, NOT a verified exact 4.87M source.
    """
    def __init__(self,base=50):
        super().__init__()
        self.base=base
        self.inc=ResidualBlock(1,base)
        self.downs=nn.ModuleList([ResidualBlock(base,2*base),
                                  ResidualBlock(2*base,4*base),
                                  ResidualBlock(4*base,8*base)])
        self.ups=nn.ModuleList([UpBlock(8*base,4*base,4*base),
                                UpBlock(4*base,2*base,2*base),
                                UpBlock(2*base,base,base)])
        self.outc=nn.Conv2d(base,1,1)
        kaiming(self)
        # Preserve low-amplitude starting corrections, not inferred original training behavior.
        with torch.no_grad():self.outc.weight.mul_(0.01);self.outc.bias.zero_()
    def forward(self,x):
        if x.ndim!=4 or x.shape[1]!=1 or x.shape[-1]%8 or x.shape[-2]%8:
            raise ValueError('Expected Bx1xHxW with spatial size divisible by 8')
        skips=[]
        z=self.inc(x);skips.append(z)
        for down in self.downs:
            z=down(F.avg_pool2d(z,2));skips.append(z)
        for up,skip in zip(self.ups,reversed(skips[:-1])):
            z=up(z,skip)
        return torch.tanh(self.outc(z))


def fingerprint(model):
    return {k:list(v.shape) for k,v in model.state_dict().items()}


def count_parameters(model):return sum(p.numel() for p in model.parameters())
