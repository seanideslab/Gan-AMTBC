#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ambtc_format.h"
#include "generator.h"
int main(int argc,char**argv){
    if(argc!=4){fprintf(stderr,"Usage: gan_ppo_ambtc_extract <stego.pgm.ambtc> <stego.pgm.map> <recovered.bin>\n");return 1;}
    AMBTCImage im={0};int*actions=NULL,total=0,rc=2;
    if(ambtc_text_read(argv[1],&im)){fprintf(stderr,"Cannot read AMBTC sidecar\n");return rc;}
    if(action_map_read(argv[2],&actions,im.nblocks,&total)){fprintf(stderr,"Cannot read action map\n");goto done;}
    size_t nbytes=((size_t)total+7u)/8u;
    unsigned char*data=(unsigned char*)calloc(nbytes,1);if(!data)goto done;
    int off=0;
    for(int i=0;i<im.nblocks;i++){
        uint8_t bits[8];generator_extract_block(&im.blocks[i],bits,actions[i],i);
        for(int j=0;j<actions[i];j++,off++)if(bits[j])data[off/8]|=(unsigned char)(1u<<(7-(off%8)));
    }
    FILE*f=fopen(argv[3],"wb");if(!f){free(data);goto done;}
    if(fwrite(data,1,nbytes,f)!=nbytes){fclose(f);free(data);goto done;}
    fclose(f);free(data);
    printf("DEMO_ONLY recovered_bits=%d output=%s (last byte may contain padding)\n",total,argv[3]);rc=0;
 done: free(actions);ambtc_free(&im);return rc;
}
