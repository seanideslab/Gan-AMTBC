#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "ambtc.h"

static uint8_t clamp_u8(float x) { if (x < 0) return 0; if (x > 255) return 255; return (uint8_t)(x + 0.5f); }

int ambtc_encode(const GrayImage *img, int block_size, AMBTCImage *out) {
    memset(out,0,sizeof(*out));
    if (!img || !img->data || block_size != 4 || img->w % block_size || img->h % block_size) return -1;
    out->w = img->w; out->h = img->h; out->block_size = block_size;
    out->blocks_x = img->w / block_size; out->blocks_y = img->h / block_size;
    out->nblocks = out->blocks_x * out->blocks_y;
    out->blocks = (AMBTCBlock*)calloc((size_t)out->nblocks, sizeof(AMBTCBlock));
    if (!out->blocks) return -2;
    int idx=0, n=block_size*block_size;
    for (int by=0; by<out->blocks_y; ++by) for (int bx=0; bx<out->blocks_x; ++bx, ++idx) {
        float sum=0, vals[64];
        for (int y=0; y<block_size; ++y) for (int x=0; x<block_size; ++x) {
            int px=(by*block_size+y)*img->w + (bx*block_size+x);
            vals[y*block_size+x] = img->data[px]; sum += vals[y*block_size+x];
        }
        float mean=sum/n, var=0, sumH=0, sumL=0; int cntH=0,cntL=0; uint16_t bm=0;
        for (int i=0;i<n;++i) {
            float d=vals[i]-mean; var += d*d;
            if (vals[i] >= mean) { bm |= (uint16_t)(1u<<i); sumH += vals[i]; cntH++; }
            else { sumL += vals[i]; cntL++; }
        }
        AMBTCBlock *b=&out->blocks[idx];
        b->H = clamp_u8(cntH ? sumH/cntH : mean);
        b->L = clamp_u8(cntL ? sumL/cntL : mean);
        if (b->H < b->L) { uint8_t t=b->H; b->H=b->L; b->L=t; }
        b->BM = bm; b->qld = (float)(b->H - b->L); b->var = var/n;
    }
    return 0;
}

int ambtc_decode(const AMBTCImage *amb, GrayImage *out) {
    memset(out,0,sizeof(*out));
    if (!amb || !amb->blocks) return -1;
    int bs=amb->block_size;
    out->w=amb->w; out->h=amb->h;
    out->data=(uint8_t*)malloc((size_t)out->w*out->h);
    if (!out->data) return -2;
    int idx=0;
    for (int by=0; by<amb->blocks_y; ++by) for (int bx=0; bx<amb->blocks_x; ++bx, ++idx) {
        const AMBTCBlock *b=&amb->blocks[idx];
        for (int y=0;y<bs;++y) for (int x=0;x<bs;++x) {
            int i=y*bs+x;
            out->data[(by*bs+y)*out->w + (bx*bs+x)] = (b->BM & (1u<<i)) ? b->H : b->L;
        }
    }
    return 0;
}

void ambtc_free(AMBTCImage *amb) { free(amb->blocks); memset(amb,0,sizeof(*amb)); }
void ambtc_block_state(const AMBTCBlock *b, float *qld_norm, float *var_norm) {
    *qld_norm = fminf(1.0f, b->qld / 255.0f);
    *var_norm = fminf(1.0f, b->var / (128.0f*128.0f));
}
