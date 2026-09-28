#ifndef GAN_PPO_AMBTC_BUDGET_H
#define GAN_PPO_AMBTC_BUDGET_H
#include "ambtc.h"
#include "policy.h"
/* DEMONSTRATION ONLY: deterministic projection onto a feasible image-level payload.
 * This is NOT the published PPO's learned budget-controller or trained policy. */
int budget_plan_demo(const AMBTCImage *im, const PPOPolicy *policy, double target_bpp,
                     int *actions, int *total_bits);
#endif
