"""Run: python3 -m unittest discover -s recovery -p 'test_*.py' -v"""
import math, unittest
import torch
from architecture_scaffold import (ActorCriticScaffold, RewardDQNScaffold,
 UNetArchitectureScaffold, VerifiedSRMFrontEnd, centered_double_tanh_candidate,
 published_double_tanh, nparams)

class RecoveryUnitTests(unittest.TestCase):
 def test_ppo_both_variants(self):
  x=torch.rand(2,2)
  for shared in (True,False):
   m=ActorCriticScaffold(shared_backbone=shared)
   logits,v=m(x)
   self.assertEqual(tuple(logits.shape),(2,4));self.assertEqual(tuple(v.shape),(2,))
   self.assertTrue(torch.isfinite(logits).all());self.assertGreater(nparams(m),50000)
 def test_dqn_output(self):
  y=RewardDQNScaffold()(torch.rand(2,4));self.assertEqual(tuple(y.shape),(2,4))
 def test_unet_shape_grad(self):
  m=UNetArchitectureScaffold()
  x=torch.rand(1,5,64,64,requires_grad=True)
  y=m(x);self.assertEqual(tuple(y.shape),(1,3,64,64))
  y.mean().backward();self.assertIsNotNone(x.grad)
 def test_srm_needs_verified_real_kernels(self):
  with self.assertRaises(ValueError):VerifiedSRMFrontEnd(torch.zeros(30,1,5,5))
  with self.assertRaises(ValueError):VerifiedSRMFrontEnd(torch.rand(29,1,5,5))
 def test_centered_candidate_at_origin(self):
  zero=torch.tensor([0.0]);a=centered_double_tanh_candidate(zero)
  self.assertAlmostEqual(float(a.item()),0.0,places=7)
  self.assertLess(float(published_double_tanh(zero).item()),-1.9)
 def test_no_original_weights_in_package(self):
  from pathlib import Path
  root=Path(__file__).parents[1]
  self.assertFalse((root/'recovery'/'checkpoints').exists())
if __name__=='__main__':unittest.main()
