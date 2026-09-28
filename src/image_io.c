#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "image_io.h"

static void skip_ws_comments(FILE *fp) {
    int c;
    do {
        c = fgetc(fp);
        if (c == '#') { while ((c = fgetc(fp)) != '\n' && c != EOF) {} }
    } while (isspace(c));
    if (c != EOF) ungetc(c, fp);
}

int pgm_read(const char *path, GrayImage *img) {
    memset(img, 0, sizeof(*img));
    FILE *fp = fopen(path, "rb");
    if (!fp) return -1;
    char magic[3] = {0};
    if (fread(magic,1,2,fp)!=2 || strcmp(magic,"P5")) { fclose(fp); return -2; }
    skip_ws_comments(fp); if (fscanf(fp, "%d", &img->w) != 1) { fclose(fp); return -3; }
    skip_ws_comments(fp); if (fscanf(fp, "%d", &img->h) != 1) { fclose(fp); return -4; }
    skip_ws_comments(fp); int maxv=0;
    if (fscanf(fp, "%d", &maxv) != 1 || maxv != 255 || img->w <= 0 || img->h <= 0 ||
        img->w > 100000 || img->h > 100000 || (size_t)img->w * (size_t)img->h > 100000000u) {
        fclose(fp); return -5;
    }
    int separator=fgetc(fp); /* consume precisely one whitespace after maxval */
    if (separator != ' ' && separator != '\n' && separator != '\r' && separator != '\t') {
        fclose(fp); return -5;
    }
    img->data = (uint8_t*)malloc((size_t)img->w * (size_t)img->h);
    if (!img->data) { fclose(fp); return -6; }
    size_t n = fread(img->data,1,(size_t)img->w*img->h,fp);
    fclose(fp);
    if (n != (size_t)img->w*img->h) { free(img->data); img->data=NULL; return -7; }
    return 0;
}

int pgm_write(const char *path, const GrayImage *img) {
    FILE *fp = fopen(path,"wb");
    if (!fp) return -1;
    fprintf(fp,"P5\n%d %d\n255\n", img->w, img->h);
    size_t n = fwrite(img->data,1,(size_t)img->w*img->h,fp);
    fclose(fp);
    return n == (size_t)img->w*img->h ? 0 : -2;
}

void image_free(GrayImage *img) {
    free(img->data); img->data = NULL; img->w = img->h = 0;
}
