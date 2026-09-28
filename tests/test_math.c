#include <math.h>
#include <stdio.h>
#include "generator.h"
int main(void){
    if(fabsf(double_tanh(0,0.15f,8,8))>1e-6f)return 1;
    if(fabsf(double_tanh_centered(0,0.5f,10,5))>1e-6f)return 2;
    if(fabsf(tanhf(-5)-tanhf(2.5f))<1.9f)return 3;
    for(int i=0;i<16;i++)for(int j=i+1;j<16;j++)if(demo_bit_position(5,i)==demo_bit_position(5,j))return 4;
    puts("Math/position checks passed: center-zero and unique bit positions");return 0;
}
