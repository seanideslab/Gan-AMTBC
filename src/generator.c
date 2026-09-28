#include <math.h>
#include "generator.h"
static int popcount16(uint16_t x) {int c=0;while(x){c+=(int)(x&1u);x>>=1;}return c;}
static unsigned char clampi(int x){if(x<0)return 0;if(x>255)return 255;return (unsigned char)x;}
void generator_init(GeneratorLite *g){g->alpha_pos=8.0f;g->beta_neg=8.0f;g->threshold=0.15f;g->compensation_gain=0.35f;}
float double_tanh_centered(float x,float tau,float alpha,float beta){
    /* Independent bounded, zero-centered candidate for a two-slope function.
       It is NOT verified as the equation actually used in the publication. */
    float center=tanhf(-alpha*tau)+tanhf(beta*tau);
    float f=tanhf(alpha*(x-tau))+tanhf(beta*(x+tau));
    float delta=f-center;
    return delta>=0 ? delta/(2.0f-center) : delta/(2.0f+center);
}
float double_tanh(float x,float tau,float alpha,float beta){
    return double_tanh_centered(x,tau,alpha,beta);
}
int demo_bit_position(int block_index,int bit_index){return (5*bit_index+7*(block_index&15))&15;}
void generator_embed_block(const GeneratorLite *g,const AMBTCBlock *cover,AMBTCBlock *stego,
                           const uint8_t *bits,int nbits,int block_index){
    *stego=*cover;
    if(nbits<0||nbits>8||!bits)return;
    const int before_ones=popcount16(cover->BM);
    for(int k=0;k<nbits;k++){
        int pos=demo_bit_position(block_index,k);
        if(bits[k])stego->BM|=(uint16_t)(1u<<pos);
        else stego->BM&=(uint16_t)~(1u<<pos);
    }
    int after_ones=popcount16(stego->BM);
    int correction=(int)lrintf(g->compensation_gain*(after_ones-before_ones)*
                               (int)(cover->H-cover->L)/16.0f);
    stego->H=clampi((int)stego->H-correction);
    stego->L=clampi((int)stego->L-correction);
    if(stego->H<stego->L){unsigned char u=stego->H;stego->H=stego->L;stego->L=u;}
    stego->qld=(float)(stego->H-stego->L);
}
void generator_extract_block(const AMBTCBlock *stego,uint8_t *bits,int nbits,int block_index){
    for(int k=0;k<nbits;k++)bits[k]=(uint8_t)((stego->BM>>demo_bit_position(block_index,k))&1u);
}
