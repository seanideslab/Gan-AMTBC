#ifndef GAN_PPO_AMBTC_GENERATOR_H
#define GAN_PPO_AMBTC_GENERATOR_H
#include "ambtc.h"
typedef struct {
    float alpha_pos, beta_neg, threshold, compensation_gain;
} GeneratorLite;
void generator_init(GeneratorLite *g);
/* Symmetric Double-Tanh demonstration mapping, zero at origin. */
float double_tanh(float x, float tau, float alpha, float beta);
/* Center corrected asymmetric mapping, zero at origin even when alpha!=beta. */
float double_tanh_centered(float x, float tau, float alpha, float beta);
/* Reversible bitmap demonstration: unique positions derived from block index. */
int demo_bit_position(int block_index,int bit_index);
void generator_embed_block(const GeneratorLite *g, const AMBTCBlock *cover, AMBTCBlock *stego,
                           const uint8_t *bits, int nbits, int block_index);
void generator_extract_block(const AMBTCBlock *stego, uint8_t *bits, int nbits, int block_index);
#endif
