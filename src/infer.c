#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "config.h"
#include "image_io.h"
#include "ambtc.h"
#include "policy.h"
#include "generator.h"
#include "budget.h"
#include "ambtc_format.h"
#include "metrics.h"
static uint8_t pseudo_bit(unsigned idx){idx^=idx>>16;idx*=0x7feb352dU;idx^=idx>>15;return(uint8_t)(idx&1u);}
static void usage(void){fprintf(stderr,"Usage: gan_ppo_ambtc_infer <input.pgm> <output.pgm> <target_bpp> [smoke_policy.txt] [payload.bin]\n");}
static uint8_t from_bytes(const unsigned char *bytes,int i){return (uint8_t)((bytes[i/8]>>(7-(i%8)))&1u);}
static void set_byte(unsigned char *bytes,int i,uint8_t bit){if(bit)bytes[i/8]|=(unsigned char)(1u<<(7-(i%8)));}
int main(int argc,char**argv){
    if(argc<4||argc>6){usage();return 1;}
    char*end=NULL;double target=strtod(argv[3],&end);
    if(!end||*end||!isfinite(target)||target<0.0625||target>0.5){fprintf(stderr,"Target bpp must be in [0.0625,0.5].\n");return 1;}
    GrayImage cover={0},out={0};AMBTCImage amb={0},stego={0};int rc=2;
    if(pgm_read(argv[1],&cover)){fprintf(stderr,"PGM read failed: %s\n",argv[1]);goto done;}
    if(ambtc_encode(&cover,4,&amb)){fprintf(stderr,"AMBTC encode failed\n");goto done;}
    PPOPolicy policy;policy_init(&policy);
    if(argc>=5&&policy_load_text(&policy,argv[4])){fprintf(stderr,"Cannot read requested weights: %s\n",argv[4]);goto done;}
    stego=amb;stego.blocks=(AMBTCBlock*)calloc((size_t)amb.nblocks,sizeof(AMBTCBlock));
    int*actions=(int*)calloc((size_t)amb.nblocks,sizeof(int));
    if(!stego.blocks||!actions){free(actions);goto done;}
    int total=0;
    if(budget_plan_demo(&amb,&policy,target,actions,&total)){fprintf(stderr,"Payload allocation failed\n");free(actions);goto done;}
    size_t nbytes=((size_t)total+7u)/8u;
    unsigned char*secret=(unsigned char*)calloc(nbytes,1);
    if(!secret){free(actions);goto done;}
    if(argc>=6){
        FILE*f=fopen(argv[5],"rb");
        if(!f||fread(secret,1,nbytes,f)!=nbytes){fprintf(stderr,"Payload file too short or unreadable\n");if(f)fclose(f);free(secret);free(actions);goto done;}
        fclose(f);
    } else for(int k=0;k<total;k++)set_byte(secret,k,pseudo_bit((unsigned)k));
    GeneratorLite gen;generator_init(&gen);
    int off=0,errors=0;
    for(int i=0;i<amb.nblocks;i++){
        uint8_t bits[8],got[8];int len=actions[i];
        for(int j=0;j<len;j++)bits[j]=from_bytes(secret,off+j);
        generator_embed_block(&gen,&amb.blocks[i],&stego.blocks[i],bits,len,i);
        generator_extract_block(&stego.blocks[i],got,len,i);
        errors+=bit_error_count(bits,got,len);off+=len;
    }
    if(off!=total||errors){fprintf(stderr,"Internal bitmap recovery failed: bits=%d errors=%d\n",off,errors);free(secret);free(actions);goto done;}
    if(ambtc_decode(&stego,&out)){free(secret);free(actions);goto done;}
    char path[4096];
    if(pgm_write(argv[2],&out)){free(secret);free(actions);goto done;}
    snprintf(path,sizeof(path),"%s.ambtc",argv[2]);if(ambtc_text_write(path,&stego)){free(secret);free(actions);goto done;}
    snprintf(path,sizeof(path),"%s.map",argv[2]);if(action_map_write(path,actions,amb.nblocks,total)){free(secret);free(actions);goto done;}
    snprintf(path,sizeof(path),"%s.payload.bin",argv[2]);FILE*f=fopen(path,"wb");
    if(!f||fwrite(secret,1,nbytes,f)!=nbytes){if(f)fclose(f);free(secret);free(actions);goto done;}fclose(f);
    printf("DEMO_ONLY target_bpp=%.4f requested_bits=%ld embedded_bits=%d actual_bpp=%.6f ",target,lround(target*cover.w*cover.h),total,(double)total/(cover.w*cover.h));
    printf("bitmap_roundtrip_errors=%d PSNR=%.4f global_SSIM=%.6f\n",errors,metric_psnr(&cover,&out),metric_ssim_global(&cover,&out));
    printf("stego_preview=%s sidecar=%s.ambtc action_map=%s.map payload=%s.payload.bin\n",argv[2],argv[2],argv[2],argv[2]);
    free(secret);free(actions);rc=0;
 done:
    image_free(&cover);image_free(&out);ambtc_free(&amb);free(stego.blocks);return rc;
}
