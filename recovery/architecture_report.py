import json,torch
from architecture_scaffold import ActorCriticScaffold,RewardDQNScaffold,UNetArchitectureScaffold,nparams
models={
 'ppo_shared_backbone_candidate':ActorCriticScaffold(shared_backbone=True),
 'ppo_separate_actor_critic_candidate':ActorCriticScaffold(shared_backbone=False),
 'dqn_architecture_candidate':RewardDQNScaffold(),
 'unet_architecture_candidate':UNetArchitectureScaffold(),
}
print(json.dumps({'status':'ARCHITECTURE_ONLY_UNTRAINED_NOT_PAPER_REPRODUCTION',
 'torch_version':torch.__version__,
 'parameter_counts':{k:nparams(v) for k,v in models.items()},
 'parameter_note':'The archived ~0.12M PPO and ~4.87M U-Net values are approximate and architecture details are incomplete; no exact match is implied.',
 'checkpoint_available':False},indent=2))
