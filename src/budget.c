#include <math.h>
#include <stdlib.h>
#include "budget.h"

typedef struct { int index; double score; } Rank;
static int by_score_desc(const void *pa, const void *pb) {
    const Rank *a = (const Rank*)pa, *b = (const Rank*)pb;
    if (a->score != b->score) return (a->score < b->score) ? 1 : -1;
    return (a->index > b->index) - (a->index < b->index);
}
/* Counts in action order 1,2,4,8. Favor adjacent actions near mean to
 * avoid extreme allocations. Some integer rates cannot be represented;
 * caller then finds the closest feasible rate and reports it explicitly. */
static int counts_for(int n, int target, int c[4]) {
    if (n <= 0 || target < n || target > 8*n) return -1;
    if (target <= 2*n) {
        c[1] = target-n; c[0] = n-c[1]; c[2] = c[3] = 0; return 0;
    }
    if (target <= 4*n) {
        int found=0, best=1000000;
        for (int n8=0;n8<=2 && n8<=n;n8++) for (int n1=0;n1<=4 && n1<=n;n1++) {
            int numerator=target-2*n+n1-4*n8;
            if (numerator<0 || numerator%2) continue;
            int n4=numerator/2, n2=n-n1-n4-n8;
            if (n2<0) continue;
            int cost=10*n8+2*n1;
            if (!found || cost<best) {c[0]=n1;c[1]=n2;c[2]=n4;c[3]=n8;best=cost;found=1;}
        }
        return found?0:-1;
    }
    int found=0,best=1000000;
    for (int n1=0;n1<=4 && n1<=n;n1++) for (int n2=0;n2<=4 && n2<=n;n2++) {
        int numerator=target-4*n+3*n1+2*n2;
        if (numerator<0 || numerator%4) continue;
        int n8=numerator/4, n4=n-n1-n2-n8;
        if (n4<0) continue;
        int cost=4*n1+n2;
        if (!found || cost<best) {c[0]=n1;c[1]=n2;c[2]=n4;c[3]=n8;best=cost;found=1;}
    }
    return found?0:-1;
}
int budget_plan_demo(const AMBTCImage *im, const PPOPolicy *policy, double target_bpp,
                     int *actions, int *total_bits) {
    if(!im || !policy || !actions || !total_bits || im->block_size!=4 ||
       !isfinite(target_bpp) || target_bpp<0.0625 || target_bpp>0.5) return -1;
    const int n=im->nblocks, pixels=im->w*im->h;
    const int requested=(int)lround(target_bpp*pixels);
    int c[4]={0},t=-1;
    for(int d=0;d<=8 && t<0;d++) {
        if (requested-d>=n && counts_for(n,requested-d,c)==0) {t=requested-d;break;}
        if (d && requested+d<=8*n && counts_for(n,requested+d,c)==0) {t=requested+d;break;}
    }
    if(t<0) return -2;
    Rank *r=(Rank*)malloc((size_t)n*sizeof(Rank)); if(!r) return -3;
    for(int i=0;i<n;i++) {
        float q,v,p[4]; ambtc_block_state(&im->blocks[i],&q,&v);
        policy_softmax(policy,q,v,p);
        r[i].index=i;
        r[i].score=2.0*q+1.5*v+0.25*(p[2]+2*p[3]);
    }
    qsort(r,(size_t)n,sizeof(Rank),by_score_desc);
    int pos=0;
    /* Highest-complexity blocks receive 8/4, lowest receive 1. */
    for(int k=3;k>=0;k--) {
        int bits=(k==0)?1:(1<<k);
        for(int j=0;j<c[k];j++) actions[r[pos++].index]=bits;
    }
    free(r);
    if(pos!=n) return -4;
    *total_bits=t;
    return 0;
}
