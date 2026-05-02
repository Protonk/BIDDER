/*
 * bidder_opaque.h — Opaque FFI surface for libbidder.
 *
 * All struct internals are hidden behind heap-allocated handles.
 * The ctypes wrapper in dist/bidder_c/ sees only void pointers.
 * Error codes are the BIDDER_ROOT_ERR_* enum from bidder_root.h.
 */

#ifndef BIDDER_OPAQUE_H
#define BIDDER_OPAQUE_H

#include <stddef.h>
#include <stdint.h>

/* Opaque handles — defined only in bidder_opaque.c */
typedef struct bdo_block bdo_block;
typedef struct bdo_nprime bdo_nprime;

/*
 * Cipher path: keyed permutation of [0, period).
 */
bdo_block  *bdo_block_create(uint64_t period,
                              const uint8_t *key, size_t key_len,
                              int *err);
void        bdo_block_free(bdo_block *h);
int         bdo_block_at(const bdo_block *h, uint64_t i, uint32_t *out);
uint64_t    bdo_block_period(const bdo_block *h);
const char *bdo_block_backend(const bdo_block *h);

/*
 * Sawtooth path: n-prime sequence via the Hardy closed form.
 *
 * bdo_nprime_at returns the result as (lo, hi) so the full 128-bit
 * range is available without struct-layout coupling. With uint64_t
 * inputs, the output provably fits in 128 bits.
 */
bdo_nprime *bdo_nprime_create(uint64_t n, uint64_t count, int *err);
void        bdo_nprime_free(bdo_nprime *h);
int         bdo_nprime_at(const bdo_nprime *h, uint64_t i,
                          uint64_t *out_lo, uint64_t *out_hi);
uint64_t    bdo_nprime_n(const bdo_nprime *h);
uint64_t    bdo_nprime_count(const bdo_nprime *h);

#endif /* BIDDER_OPAQUE_H */
