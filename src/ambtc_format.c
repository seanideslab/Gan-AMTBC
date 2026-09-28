#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ambtc_format.h"
int ambtc_text_write(const char *path,const AMBTCImage *im){
    FILE*f=fopen(path,"w");if(!f)return-1;
    fprintf(f,"GPA1 %d %d %d %d\n",im->w,im->h,im->block_size,im->nblocks);
    for(int i=0;i<im->nblocks;i++)fprintf(f,"%u %u %u\n",im->blocks[i].H,im->blocks[i].L,im->blocks[i].BM);
    int err=ferror(f);fclose(f);return err?-2:0;
}
int ambtc_text_read(const char *path,AMBTCImage *im){
    memset(im,0,sizeof(*im));FILE*f=fopen(path,"r");if(!f)return-1;
    char magic[16];int w,h,bs,n;
    if(fscanf(f,"%15s%d%d%d%d",magic,&w,&h,&bs,&n)!=5||strcmp(magic,"GPA1")||
       w<=0||h<=0||bs!=4||w%bs||h%bs||n!=(w/bs)*(h/bs)){fclose(f);return-2;}
    im->w=w;im->h=h;im->block_size=bs;im->blocks_x=w/bs;im->blocks_y=h/bs;im->nblocks=n;
    im->blocks=(AMBTCBlock*)calloc((size_t)n,sizeof(AMBTCBlock));if(!im->blocks){fclose(f);return-3;}
    for(int i=0;i<n;i++){
       unsigned H,L,BM;
       if(fscanf(f,"%u%u%u",&H,&L,&BM)!=3||H>255||L>255||BM>65535){
          fclose(f);ambtc_free(im);return-4;
       }
       im->blocks[i].H=(uint8_t)H;im->blocks[i].L=(uint8_t)L;
       im->blocks[i].BM=(uint16_t)BM;im->blocks[i].qld=(float)(H-L);
    }
    fclose(f);return 0;
}
int action_map_write(const char *path,const int *actions,int n,int total){
    FILE*f=fopen(path,"w");if(!f)return-1;
    fprintf(f,"GPA_MAP1 %d %d\n",n,total);
    for(int i=0;i<n;i++)fprintf(f,"%d\n",actions[i]);
    int err=ferror(f);fclose(f);return err?-2:0;
}
int action_map_read(const char *path,int **actions,int expected_n,int *total){
    FILE*f=fopen(path,"r");if(!f)return-1;char magic[24];int n,bits;
    if(fscanf(f,"%23s%d%d",magic,&n,&bits)!=3||strcmp(magic,"GPA_MAP1")||n!=expected_n||bits<0){fclose(f);return-2;}
    int*a=(int*)calloc((size_t)n,sizeof(int));if(!a){fclose(f);return-3;}
    int sum=0;
    for(int i=0;i<n;i++){
        if(fscanf(f,"%d",&a[i])!=1||(a[i]!=1&&a[i]!=2&&a[i]!=4&&a[i]!=8)){free(a);fclose(f);return-4;}
        sum+=a[i];
    }
    fclose(f);if(sum!=bits){free(a);return-5;}
    *actions=a;*total=bits;return 0;
}
