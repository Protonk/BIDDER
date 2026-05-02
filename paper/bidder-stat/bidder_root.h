/*
 * bidder_root.h — C twin of the project-root bidder.py entry point.
 *
 * Two construction functions:
 *
 *     bidder_cipher_init(period, key, key_len, &block)
 *     bidder_sawtooth_init(n, count, &seq)
 *
 * The cipher path gives a keyed permutation of [0, period).
 * The sawtooth path gives the first `count` n-primes of monoid nZ+
 * (n >= 2) in ascending order.
 *
 * This header is intentionally small. The cipher path wraps the
 * existing generator/bidder.c backend; the sawtooth path implements the
 * same closed form as core/sawtooth.py. Unlike Python, the C sawtooth
 * path is bounded by uint64_t: lookups that would exceed that range
 * report BIDDER_ROOT_ERR_OVERFLOW instead of returning a bignum.
 */

#ifndef BIDDER_ROOT_H
#define BIDDER_ROOT_H

#include <stddef.h>
#include <stdint.h>

#include "generator/bidder.h"

#define BIDDER_ROOT_MAX_PERIOD_V1 UINT64_C(0xffffffff)

enum {
    BIDDER_ROOT_OK = 0,
    BIDDER_ROOT_ERR_NULL = -1,
    BIDDER_ROOT_ERR_PERIOD = -2,
    BIDDER_ROOT_ERR_UNSUPPORTED_PERIOD = -3,
    BIDDER_ROOT_ERR_N = -4,
    BIDDER_ROOT_ERR_COUNT = -5,
    BIDDER_ROOT_ERR_INDEX = -6,
    BIDDER_ROOT_ERR_OVERFLOW = -7,
    BIDDER_ROOT_ERR_BACKEND = -8,
    BIDDER_ROOT_ERR_KEY_LENGTH = -9,
};

typedef struct {
    uint64_t period;
    bidder_ctx inner;
} bidder_block_ctx;

typedef struct {
    uint64_t n;
    uint64_t count;
} nprime_sequence_ctx;

/*
 * Initialize the period-only cipher wrapper.
 *
 * period: integer in [2, BIDDER_ROOT_MAX_PERIOD_V1].
 * key:    raw key material. NULL is accepted only when key_len == 0.
 *
 * Returns one of the BIDDER_ROOT_* status codes above.
 */
int bidder_cipher_init(
    bidder_block_ctx *ctx,
    uint64_t period,
    const uint8_t *key,
    size_t key_len
);

/*
 * Return the i-th element of the keyed permutation in [0, period).
 * Does not mutate ctx.
 */
int bidder_block_at(const bidder_block_ctx *ctx, uint64_t i, uint32_t *out);

/*
 * Diagnostic backend name: "speck32" or "feistel".
 * Returns NULL if ctx is NULL.
 */
const char *bidder_block_backend(const bidder_block_ctx *ctx);

/*
 * Initialize the deterministic sawtooth sequence wrapper.
 *
 * n:     integer >= 2.
 * count: integer >= 1.
 */
int bidder_sawtooth_init(nprime_sequence_ctx *ctx, uint64_t n, uint64_t count);

/*
 * Return the i-th n-prime (0-indexed) in ascending order.
 *
 * The result is exact when it fits in uint64_t. If the closed form
 * would overflow uint64_t, returns BIDDER_ROOT_ERR_OVERFLOW. This is
 * the one intentional range difference from bidder.py / sawtooth.py,
 * which continue with arbitrary-precision integers.
 */
int bidder_sawtooth_at(const nprime_sequence_ctx *ctx, uint64_t i, uint64_t *out);

#endif /* BIDDER_ROOT_H */
