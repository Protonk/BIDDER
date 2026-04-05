/*
 * hch.h — Hilbert-Champernowne-Hyland block generator (C implementation)
 *
 * Speck32/64 permutation with cycle-walking. For blocks that fit within
 * 2^32 and have a cycle-walk ratio <= 64, this uses the real cipher.
 * For smaller blocks, a balanced Feistel with SHA-256-derived round keys
 * is used (the SHA-256 dependency is in hch.c, not here).
 *
 * Usage:
 *     hch_ctx ctx;
 *     uint8_t key[] = "secret";
 *     hch_init(&ctx, 65536, 2, key, 6);
 *     for (int i = 0; i < 100; i++)
 *         printf("%u\n", hch_next(&ctx));
 */

#ifndef HCH_H
#define HCH_H

#include <stdint.h>

#define HCH_SPECK32_ROUNDS 22
#define HCH_FEISTEL_ROUNDS 8
#define HCH_MAX_CYCLE_WALK_RATIO 64

typedef struct {
    /* Parameters */
    uint64_t base;
    uint32_t digit_class;
    uint64_t block_start;
    uint64_t block_size;

    /* Permutation state */
    int mode;  /* 0 = speck32, 1 = feistel */

    /* Speck32/64 round keys */
    uint16_t speck_rk[HCH_SPECK32_ROUNDS];

    /* Feistel state (for small blocks) */
    uint64_t feistel_keys[HCH_FEISTEL_ROUNDS];
    uint32_t L_size;
    uint32_t R_size;

    /* Counter */
    uint64_t counter;
} hch_ctx;

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
int hch_init(hch_ctx *ctx, uint64_t base, uint32_t digit_class,
             const uint8_t *key, uint32_t key_len);

/*
 * Generate the next output symbol in {1, ..., base-1}.
 * Wraps at the end of the period.
 */
uint32_t hch_next(hch_ctx *ctx);

/* Reset counter to start of period. */
void hch_reset(hch_ctx *ctx);

#endif /* HCH_H */
