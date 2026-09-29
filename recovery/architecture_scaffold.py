"""Architecture-only reconstruction from an unverified one-page lab parameter note.

NOT the original experiment code, weights, training pipeline, or scientific reproduction.
All model parameters start randomly initialized. Do not interpret forward outputs as stego data.
"""
from __future__ import annotations
import math
from pathlib import Path
import torch
from torch import nn
from torch.nn import functional as F

ACTIONS_BITS_PER_BLOCK = (1, 2, 4, 8)


def _orthogonal_mlp(seq: nn.Sequential, output_gain: float = 0.01) -> None:
    linear = [m for m in seq.modules() if isinstance(m, nn.Linear)]
    for i, layer in enumerate(linear):
        nn.init.orthogonal_(layer.weight, gain=output_gain if i == len(linear)-1 else math.sqrt(2.0))
        nn.init.zeros_(layer.bias)


def _mlp(input_dim: int, output_dim: int, width: int) -> nn.Sequential:
    return nn.Sequential(nn.Linear(input_dim,width), nn.Tanh(),
                         nn.Linear(width,width), nn.Tanh(),nn.Linear(width,output_dim))


class ActorCriticScaffold(nn.Module):
    """Two 256-wide layers; separate/shared pathways are both exposed because provenance is unresolved."""
    def __init__(self, state_dim: int=2, width: int=256, n_actions: int=4,
                 shared_backbone: bool=False):
        super().__init__()
        self.shared_backbone=shared_backbone
        if shared_backbone:
            self.backbone=nn.Sequential(nn.Linear(state_dim,width),nn.Tanh(),
                                        nn.Linear(width,width),nn.Tanh())
            self.actor_head=nn.Linear(width,n_actions)
            self.value_head=nn.Linear(width,1)
            for m in self.backbone:
                if isinstance(m,nn.Linear):
                    nn.init.orthogonal_(m.weight,gain=math.sqrt(2));nn.init.zeros_(m.bias)
            nn.init.orthogonal_(self.actor_head.weight,gain=0.01)
            nn.init.zeros_(self.actor_head.bias)
            nn.init.orthogonal_(self.value_head.weight,gain=1.0)
            nn.init.zeros_(self.value_head.bias)
        else:
            self.actor=_mlp(state_dim,n_actions,width)
            self.critic=_mlp(state_dim,1,width)
            _orthogonal_mlp(self.actor,0.01)
            _orthogonal_mlp(self.critic,1.0)

    def forward(self,state: torch.Tensor):
        if state.shape[-1]!=2: raise ValueError('State must end with (QLD, variance)')
        if self.shared_backbone:
            x=self.backbone(state)
            return self.actor_head(x),self.value_head(x).squeeze(-1)
        return self.actor(state),self.critic(state).squeeze(-1)


class RewardDQNScaffold(nn.Module):
    """Observation (QLD,variance,epoch_fraction,running_budget_ratio) -> four raw Q values."""
    def __init__(self):
        super().__init__()
        self.network=nn.Sequential(nn.Linear(4,64),nn.ReLU(),nn.Linear(64,64),
                                   nn.ReLU(),nn.Linear(64,4))
        for m in self.network:
            if isinstance(m,nn.Linear):
                nn.init.kaiming_normal_(m.weight,nonlinearity='relu')
                nn.init.zeros_(m.bias)
        # The note says an output bias favored security but provides neither
        # an action-index mapping nor numeric bias: do not invent one.

    def forward(self,observation:torch.Tensor):
        if observation.shape[-1]!=4: raise ValueError('DQN observation last dimension must be 4')
        return self.network(observation)


class ConvPair(nn.Module):
    def __init__(self,c_in,c_out):
        super().__init__()
        self.layers=nn.Sequential(nn.Conv2d(c_in,c_out,3,padding=1),nn.ReLU(inplace=True),
                                  nn.Conv2d(c_out,c_out,3,padding=1),nn.ReLU(inplace=True))
        for m in self.layers:
            if isinstance(m,nn.Conv2d): nn.init.kaiming_normal_(m.weight,nonlinearity='relu');nn.init.zeros_(m.bias)
    def forward(self,x):return self.layers(x)


class UNetArchitectureScaffold(nn.Module):
    """4-level channel sketch (32,64,128,256). A shape/architecture prototype ONLY.

    Tensor schema is NOT recovered from the paper. The 5-channel input represents
    a proposed [bitmap,H_map,L_map,secret_map,load_map] engineering interface;
    the three channels output uncalibrated bitmap/logit and H/L delta maps.
    It neither embeds a decodable payload nor reconstructs published weights.
    """
    def __init__(self,in_channels:int=5,channels=(32,64,128,256)):
        super().__init__()
        if len(channels)!=4:raise ValueError('Four channels/stages required')
        self.encoder=nn.ModuleList()
        prev=in_channels
        for c in channels:
            self.encoder.append(ConvPair(prev,c));prev=c
        self.up=nn.ModuleList()
        self.decoder=nn.ModuleList()
        for c_in,c_out in zip(reversed(channels[1:]),reversed(channels[:-1])):
            self.up.append(nn.ConvTranspose2d(c_in,c_out,2,stride=2))
            self.decoder.append(ConvPair(c_out*2,c_out))
        self.head=nn.Conv2d(channels[0],3,1)
        nn.init.kaiming_normal_(self.head.weight,nonlinearity='linear')
        nn.init.zeros_(self.head.bias)

    def forward(self,x:torch.Tensor):
        if x.ndim!=4 or x.shape[1]!=5 or x.shape[-1]%16 or x.shape[-2]%16:
            raise ValueError('Expected [B,5,H,W], H/W divisible by 16')
        skips=[];z=x
        for block in self.encoder:
            z=block(z);skips.append(z)
            if len(skips)<4:z=F.avg_pool2d(z,2)
        for up,block,skip in zip(self.up,self.decoder,reversed(skips[:-1])):
            z=up(z)
            z=block(torch.cat((z,skip),dim=1))
        return self.head(z)


class VerifiedSRMFrontEnd(nn.Module):
    """Requires a genuine, verified 30x1x5x5 SRM kernel array; no synthetic filters supplied."""
    def __init__(self,verified_kernels:torch.Tensor):
        super().__init__()
        t=torch.as_tensor(verified_kernels,dtype=torch.float32)
        if tuple(t.shape)!=(30,1,5,5):raise ValueError('Expected 30 genuine SRM kernels: [30,1,5,5]')
        if not torch.isfinite(t).all():raise ValueError('Nonfinite SRM kernel weights')
        if (t.flatten(start_dim=1).abs().sum(dim=1)<1e-8).any():
            raise ValueError('Empty SRM kernel detected')
        conv=nn.Conv2d(1,30,5,padding=2,bias=False)
        with torch.no_grad():conv.weight.copy_(t)
        conv.weight.requires_grad_(False)
        self.conv=conv
    def forward(self,x):return self.conv(x)


def load_verified_srm_kernels(path:str|Path,sha256:str) -> torch.Tensor:
    """A .npy file is accepted only with a matching externally supplied SHA-256."""
    import hashlib,numpy as np
    p=Path(path)
    real=hashlib.sha256(p.read_bytes()).hexdigest()
    if real.lower()!=sha256.lower():raise ValueError('SRM coefficients hash mismatch')
    return torch.tensor(np.load(p,allow_pickle=False),dtype=torch.float32)


def published_double_tanh(t, alpha=10.0,beta=5.0,tau=.5):
    """Published subtraction expression; retained solely for discrepancy tests."""
    return torch.tanh(alpha*(t-tau))-torch.tanh(beta*(t+tau))


def centered_double_tanh_candidate(t,alpha=10.0,beta=5.0,tau=.5):
    """NEW candidate, not recovered: center-calibrated asymmetric soft function."""
    base=math.tanh(-alpha*tau)+math.tanh(beta*tau)
    return .5*(torch.tanh(alpha*(t-tau))+torch.tanh(beta*(t+tau))-base)


def nparams(model:nn.Module) -> int:
    return sum(p.numel() for p in model.parameters())
