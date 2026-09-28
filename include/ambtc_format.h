#ifndef GAN_PPO_AMBTC_FORMAT_H
#define GAN_PPO_AMBTC_FORMAT_H
#include "ambtc.h"
int ambtc_text_write(const char *path,const AMBTCImage *im);
int ambtc_text_read(const char *path,AMBTCImage *im);
int action_map_write(const char *path,const int *actions,int n,int total);
int action_map_read(const char *path,int **actions,int expected_n,int *total);
#endif
