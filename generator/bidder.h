/*
 * bidder.h — BIDDER block generator (C implementation)
 *
 * Speck32/64 permutation with cycle-walking. For blocks that fit within
 * 2^32 and have a cycle-walk ratio <= 64, this uses the real cipher.
 * For smaller blocks, a balanced Feistel with SHA-256-derived round keys
 * is used (the SHA-256 dependency is in bidder.c, not here).
 *
 * Usage:
 *     bidder_ctx ctx;
 *     uint8_t key[] = "secret";
 *     bidder_init(&ctx, 65536, 2, key, 6);
 *     for (int i = 0; i < 100; i++)
 *         printf("%u\n", bidder_next(&ctx));
 */

#ifndef BIDDER_H
#define BIDDER_H

#include <stdint.h>

#define BIDDER_SPECK32_ROUNDS 22
#define BIDDER_FEISTEL_ROUNDS 8
#define BIDDER_MAX_CYCLE_WALK_RATIO 64

typedef struct {
    /* Parameters */
    uint64_t base;
    uint32_t digit_class;
    uint64_t block_start;
    uint64_t block_size;

    /* Permutation state */
    int mode;  /* 0 = speck32, 1 = feistel */

    /* Speck32/64 round keys */
    uint16_t speck_rk[BIDDER_SPECK32_ROUNDS];

    /* Feistel state (for small blocks) */
    uint64_t feistel_keys[BIDDER_FEISTEL_ROUNDS];
    uint32_t L_size;
    uint32_t R_size;

    /* Counter */
    uint64_t counter;
} bidder_ctx;

/*
 * Initialize the generator.
 *
 * base:        output symbols are in {1, ..., base-1}
 * digit_class: operating block is [base^(d-1), base^d - 1]
 * key:         raw key material
 * key_len:     length of key in bytes
 *
 * Returns 0 on success, -1 if block_size exceeds 2^32 (use Python for larger).
 */
int bidder_init(bidder_ctx *ctx, uint64_t base, uint32_t digit_class,
             const uint8_t *key, uint32_t key_len);

/*
 * Generate the next output symbol in {1, ..., base-1}.
 * Wraps at the end of the period.
 */
uint32_t bidder_next(bidder_ctx *ctx);

/* Reset counter to start of period. */
void bidder_reset(bidder_ctx *ctx);

#endif /* BIDDER_H */
