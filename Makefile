CC ?= cc
CFLAGS ?= -O2 -std=c11 -Wall -Wextra -Wpedantic -Iinclude
LDFLAGS ?= -lm
COMMON = src/image_io.c src/ambtc.c src/policy.c src/generator.c src/budget.c src/metrics.c
FORMAT = src/ambtc_format.c
BIN = bin
.PHONY: all clean smoke test
all: $(BIN)/gan_ppo_ambtc_infer $(BIN)/gan_ppo_ambtc_eval $(BIN)/gan_ppo_ambtc_extract $(BIN)/gan_ppo_ambtc_split
$(BIN):
	mkdir -p $(BIN)
$(BIN)/gan_ppo_ambtc_infer: $(COMMON) $(FORMAT) src/infer.c | $(BIN)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)
$(BIN)/gan_ppo_ambtc_eval: $(COMMON) src/evaluate.c | $(BIN)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)
$(BIN)/gan_ppo_ambtc_extract: src/ambtc.c src/image_io.c src/generator.c $(FORMAT) src/extract.c | $(BIN)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)
$(BIN)/gan_ppo_ambtc_split: src/split_tool.c | $(BIN)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)
smoke: all
	mkdir -p results
	$(BIN)/gan_ppo_ambtc_infer example/lena_like_64.pgm results/demo_0p2.pgm 0.2 weight/policy_smoke.txt
	$(BIN)/gan_ppo_ambtc_extract results/demo_0p2.pgm.ambtc results/demo_0p2.pgm.map results/demo_0p2_recovered.bin
	cmp results/demo_0p2.pgm.payload.bin results/demo_0p2_recovered.bin
	$(BIN)/gan_ppo_ambtc_infer example/lena_like_64.pgm results/demo_0p4.pgm 0.4 weight/policy_smoke.txt
	$(BIN)/gan_ppo_ambtc_extract results/demo_0p4.pgm.ambtc results/demo_0p4.pgm.map results/demo_0p4_recovered.bin
	cmp results/demo_0p4.pgm.payload.bin results/demo_0p4_recovered.bin
	printf 'example/lena_like_64.pgm\n' > results/demo_images.txt
	$(BIN)/gan_ppo_ambtc_eval results/demo_images.txt results/demo_eval.csv 0.4 weight/policy_smoke.txt
	test "$$(sha256sum results/demo_0p2.pgm results/demo_0p4.pgm | cut -d' ' -f1 | uniq | wc -l)" -eq 2
test: smoke
	$(CC) $(CFLAGS) -o $(BIN)/test_math src/generator.c tests/test_math.c $(LDFLAGS)
	$(BIN)/test_math
	python3 -m unittest discover -s tests -v
clean:
	rm -rf $(BIN) results/demo_* results/*.ambtc results/*.map results/*_recovered.bin
