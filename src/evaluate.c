#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "image_io.h"
#include "ambtc.h"
#include "policy.h"
#include "generator.h"
#include "budget.h"
#include "metrics.h"
static uint8_t pseudo_bit(unsigned i){i^=i>>16;i*=0x7feb352dU;i^=i>>15;return(uint8_t)(i&1u);}
static const char*basename_local(const char*p){const char*s=strrchr(p,'/');return s?s+1:p;}
static int evaluate_one(const char*path,double target,PPOPolicy*p,FILE*csv){
    GrayImage cover={0},out={0};AMBTCImage a={0},b={0};int rc=-1,actual=0;
    if(pgm_read(path,&cover)||ambtc_encode(&cover,4,&a))goto done;
    b=a;b.blocks=(AMBTCBlock*)calloc((size_t)a.nblocks,sizeof(AMBTCBlock));
    int*actions=(int*)calloc((size_t)a.nblocks,sizeof(int));
    if(!b.blocks||!actions){free(actions);goto done;}
    if(budget_plan_demo(&a,p,target,actions,&actual)){free(actions);goto done;}
    GeneratorLite g;generator_init(&g);int off=0,errors=0;
    for(int i=0;i<a.nblocks;i++){
        uint8_t bits[8],got[8];
        for(int k=0;k<actions[i];k++)bits[k]=pseudo_bit((unsigned)(off+k));
        generator_embed_block(&g,&a.blocks[i],&b.blocks[i],bits,actions[i],i);
        generator_extract_block(&b.blocks[i],got,actions[i],i);
        errors+=bit_error_count(bits,got,actions[i]);off+=actions[i];
    }
    if(ambtc_decode(&b,&out)){free(actions);goto done;}
    fprintf(csv,"%s,%.6f,%.6f,%.4f,%.6f,%d,%d,DEMO_NOT_PAPER\n",basename_local(path),target,
       (double)actual/(cover.w*cover.h),metric_psnr(&cover,&out),metric_ssim_global(&cover,&out),actual,errors);
    free(actions);rc=0;
 done: image_free(&cover);image_free(&out);ambtc_free(&a);free(b.blocks);return rc;
}
int main(int argc,char**argv){
    if(argc<4||argc>5){fprintf(stderr,"Usage: gan_ppo_ambtc_eval <list.txt> <out.csv> <target_bpp> [smoke_policy.txt]\n");return 1;}
    char*end=NULL;double target=strtod(argv[3],&end);if(!end||*end||!isfinite(target)||target<0.0625||target>0.5)return 1;
    PPOPolicy policy;policy_init(&policy);
    if(argc==5&&policy_load_text(&policy,argv[4])){fprintf(stderr,"Cannot read weights\n");return 2;}
    FILE*list=fopen(argv[1],"r"),*out=fopen(argv[2],"w");
    if(!list||!out){if(list)fclose(list);if(out)fclose(out);return 2;}
    fputs("image_id,target_bpp,actual_bpp,psnr,global_ssim,embedded_bits,verified_bitmap_bit_errors,provenance\n",out);
    char path[4096];int n=0,fail=0;
    while(fgets(path,sizeof(path),list)){
        path[strcspn(path,"\r\n")]=0;if(!path[0]||path[0]=='#')continue;
        if(evaluate_one(path,target,&policy,out))fail++;else n++;
    }
    fclose(list);fclose(out);printf("DEMO_ONLY evaluated=%d failed=%d csv=%s\n",n,fail,argv[2]);return fail?3:0;
}
