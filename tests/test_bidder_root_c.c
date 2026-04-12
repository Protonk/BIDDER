/*
 * test_bidder_root_c.c — Tests for the C twin of project-root bidder.py.
 *
 * Verifies:
 *   1. cipher(period, key) parity surface over [0, period)
 *   2. backend selection remains visible at the root layer
 *   3. sawtooth(n, count) matches acm_n_primes on small cases
 *   4. astronomical-index and overflow behavior on the sawtooth path
 *
 * The overflow case is intentional API surface, not a bug: Python's
 * sawtooth path keeps going with bignums, while the C root wrapper
 * stops at uint64_t and returns BIDDER_ROOT_ERR_OVERFLOW.
 *
 * Build:
 *   gcc -O2 -o test_bidder_root_c tests/test_bidder_root_c.c \
 *       bidder_root.c generator/bidder.c core/acm_core.c -lm
 *
 * Run:
 *   ./test_bidder_root_c
 */

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "../bidder_root.h"
#include "../core/acm_core.h"

static int failures = 0;

#define CHECK(cond, msg) do { \
    if (!(cond)) { printf("  FAIL: %s\n", msg); failures++; } \
} while (0)


static void test_reexports(void)
{
    printf("--- Root constants ---\n");
    CHECK(BIDDER_ROOT_MAX_PERIOD_V1 == UINT32_MAX,
          "MAX_PERIOD_V1 should equal 2^32 - 1");
    printf("  OK\n\n");
}


static void test_cipher_vector(void)
{
    static const uint32_t expected[12] = {
        17, 65, 39, 69, 71, 27, 33, 63, 77, 5, 24, 32
    };
    bidder_block_ctx ctx;

    printf("--- cipher vector ---\n");
    CHECK(bidder_cipher_init(&ctx, 100, (const uint8_t *)"root test", 9)
              == BIDDER_ROOT_OK,
          "cipher init failed");
    CHECK(ctx.period == 100, "period should be stored on the root wrapper");

    for (uint64_t i = 0; i < 12; i++) {
        uint32_t out = 0;
        int rc = bidder_block_at(&ctx, i, &out);
        CHECK(rc == BIDDER_ROOT_OK, "cipher at() should succeed");
        if (rc == BIDDER_ROOT_OK && out != expected[i]) {
            printf("  FAIL: index %llu -> %u, expected %u\n",
                   (unsigned long long)i, out, expected[i]);
            failures++;
        }
    }
    printf("  OK\n\n");
}


static void test_cipher_permutation(void)
{
    bidder_block_ctx ctx;
    uint8_t *seen;

    printf("--- cipher permutation on [0, period) ---\n");
    CHECK(bidder_cipher_init(&ctx, 100, (const uint8_t *)"permute", 7)
              == BIDDER_ROOT_OK,
          "cipher init failed");

    seen = calloc((size_t)ctx.period, sizeof(*seen));
    CHECK(seen != NULL, "seen allocation failed");
    if (seen == NULL)
        return;

    for (uint64_t i = 0; i < ctx.period; i++) {
        uint32_t out = 0;
        int rc = bidder_block_at(&ctx, i, &out);
        CHECK(rc == BIDDER_ROOT_OK, "cipher at() failed inside permutation test");
        if (rc != BIDDER_ROOT_OK)
            continue;
        CHECK(out < ctx.period, "cipher output out of range");
        if (out < ctx.period) {
            CHECK(seen[out] == 0, "cipher output collision");
            seen[out] = 1;
        }
    }

    free(seen);
    printf("  OK\n\n");
}


static void test_cipher_validation_and_backends(void)
{
    bidder_block_ctx small;
    bidder_block_ctx large;
    bidder_block_ctx empty_key;
    uint32_t out = 0;

    printf("--- cipher validation and backends ---\n");
    CHECK(bidder_cipher_init(&small, 1, (const uint8_t *)"x", 1)
              == BIDDER_ROOT_ERR_PERIOD,
          "period < 2 should be rejected");
    CHECK(bidder_cipher_init(&small, BIDDER_ROOT_MAX_PERIOD_V1 + 1,
                             (const uint8_t *)"x", 1)
              == BIDDER_ROOT_ERR_UNSUPPORTED_PERIOD,
          "period above MAX_PERIOD_V1 should be rejected");
    CHECK(bidder_cipher_init(&small, 10, NULL, 1)
              == BIDDER_ROOT_ERR_NULL,
          "NULL key with non-zero length should be rejected");
    CHECK(bidder_cipher_init(&empty_key, 10, NULL, 0)
              == BIDDER_ROOT_OK,
          "empty key should be accepted");
    CHECK(bidder_block_at(&empty_key, 0, &out) == BIDDER_ROOT_OK,
          "empty-key cipher should be usable");

    CHECK(bidder_cipher_init(&small, 100, (const uint8_t *)"small", 5)
              == BIDDER_ROOT_OK,
          "small cipher init failed");
    CHECK(strcmp(bidder_block_backend(&small), "feistel") == 0,
          "small period should use feistel");

    CHECK(bidder_cipher_init(&large, UINT64_C(1) << 27,
                             (const uint8_t *)"large", 5)
              == BIDDER_ROOT_OK,
          "large cipher init failed");
    CHECK(strcmp(bidder_block_backend(&large), "speck32") == 0,
          "large period should use speck32");

    CHECK(bidder_block_at(&small, small.period, &out) == BIDDER_ROOT_ERR_INDEX,
          "cipher out-of-range index should be rejected");
    printf("  OK\n\n");
}


static void test_sawtooth_vector(void)
{
    static const uint64_t expected[10] = {
        3, 6, 12, 15, 21, 24, 30, 33, 39, 42
    };
    nprime_sequence_ctx seq;

    printf("--- sawtooth vector ---\n");
    CHECK(bidder_sawtooth_init(&seq, 3, 10) == BIDDER_ROOT_OK,
          "sawtooth init failed");
    for (uint64_t i = 0; i < 10; i++) {
        uint64_t out = 0;
        int rc = bidder_sawtooth_at(&seq, i, &out);
        CHECK(rc == BIDDER_ROOT_OK, "sawtooth at() should succeed");
        if (rc == BIDDER_ROOT_OK && out != expected[i]) {
            printf("  FAIL: sawtooth index %llu -> %llu, expected %llu\n",
                   (unsigned long long)i,
                   (unsigned long long)out,
                   (unsigned long long)expected[i]);
            failures++;
        }
    }
    printf("  OK\n\n");
}


static void test_sawtooth_matches_acm_n_primes(void)
{
    printf("--- sawtooth matches acm_n_primes ---\n");

    for (int64_t n = 2; n <= 12; n++) {
        const int counts[] = {1, 5, 50};
        for (size_t c = 0; c < sizeof(counts) / sizeof(counts[0]); c++) {
            nprime_sequence_ctx seq;
            int64_t expected[50];
            int count = counts[c];
            CHECK(acm_n_primes(n, count, expected) == 0,
                  "acm_n_primes failed");
            CHECK(bidder_sawtooth_init(&seq, (uint64_t)n, (uint64_t)count)
                      == BIDDER_ROOT_OK,
                  "sawtooth init failed");
            for (int i = 0; i < count; i++) {
                uint64_t out = 0;
                int rc = bidder_sawtooth_at(&seq, (uint64_t)i, &out);
                CHECK(rc == BIDDER_ROOT_OK, "sawtooth at() failed");
                if (rc == BIDDER_ROOT_OK && out != (uint64_t)expected[i]) {
                    printf("  FAIL: n=%lld count=%d index=%d -> %llu, expected %lld\n",
                           (long long)n, count, i,
                           (unsigned long long)out,
                           (long long)expected[i]);
                    failures++;
                }
            }
        }
    }
    printf("  OK\n\n");
}


static void test_sawtooth_crosscheck_python(void)
{
    /* Values computed by Python's NPrimeSequence (bignum path).
       Closes the cross-language fixture gap for the Hardy closed form. */
    static const struct {
        uint64_t n;
        uint64_t count;
        uint64_t K;
        uint64_t expected;
    } cases[] = {
        {      2,     1000001,        1000000,           4000002 },
        {      7,     1000000,         999999,           8166662 },
        {    100,       50001,          50000,           5050600 },
        {      3,      777778,         777777,           3499998 },
        {     13,          13,             12,               182 },
        {      2, UINT64_C(1) << 40, (UINT64_C(1) << 40) - 1,
                                                  4398046511102ULL },
        {      5,      250001,         250000,           1562505 },
    };
    size_t n_cases = sizeof(cases) / sizeof(cases[0]);

    printf("--- sawtooth cross-check against Python fixtures ---\n");
    for (size_t i = 0; i < n_cases; i++) {
        nprime_sequence_ctx seq;
        uint64_t out = 0;
        CHECK(bidder_sawtooth_init(&seq, cases[i].n, cases[i].count)
                  == BIDDER_ROOT_OK,
              "sawtooth init failed for cross-check case");
        int rc = bidder_sawtooth_at(&seq, cases[i].K, &out);
        CHECK(rc == BIDDER_ROOT_OK, "sawtooth at() failed for cross-check case");
        if (rc == BIDDER_ROOT_OK && out != cases[i].expected) {
            printf("  FAIL: n=%llu K=%llu -> %llu, expected %llu\n",
                   (unsigned long long)cases[i].n,
                   (unsigned long long)cases[i].K,
                   (unsigned long long)out,
                   (unsigned long long)cases[i].expected);
            failures++;
        }
    }
    printf("  OK\n\n");
}


static void test_sawtooth_validation_and_limits(void)
{
    nprime_sequence_ctx seq;
    uint64_t out = 0;

    printf("--- sawtooth validation and limits ---\n");
    CHECK(bidder_sawtooth_init(&seq, 1, 10) == BIDDER_ROOT_ERR_N,
          "n < 2 should be rejected");
    CHECK(bidder_sawtooth_init(&seq, 3, 0) == BIDDER_ROOT_ERR_COUNT,
          "count < 1 should be rejected");

    CHECK(bidder_sawtooth_init(&seq, 5, 100) == BIDDER_ROOT_OK,
          "sawtooth init failed");
    CHECK(bidder_sawtooth_at(&seq, 100, &out) == BIDDER_ROOT_ERR_INDEX,
          "out-of-range sawtooth index should be rejected");

    CHECK(bidder_sawtooth_init(&seq, 2, UINT64_C(1) << 40) == BIDDER_ROOT_OK,
          "astronomical sawtooth init failed");
    CHECK(bidder_sawtooth_at(&seq, (UINT64_C(1) << 40) - 1, &out)
              == BIDDER_ROOT_OK,
          "astronomical sawtooth lookup failed");
    CHECK(out == (UINT64_C(1) << 42) - 2,
          "astronomical sawtooth value mismatch");

    CHECK(bidder_sawtooth_init(&seq, UINT64_MAX, 2) == BIDDER_ROOT_OK,
          "max-n sawtooth init failed");
    /* Python would keep going here with a bignum; the C root API
       intentionally reports overflow once the closed form leaves
       uint64_t. */
    CHECK(bidder_sawtooth_at(&seq, 1, &out) == BIDDER_ROOT_ERR_OVERFLOW,
          "overflowing sawtooth value should be rejected");
    printf("  OK\n\n");
}


int main(void)
{
    printf("=== bidder root C tests ===\n\n");

    test_reexports();
    test_cipher_vector();
    test_cipher_permutation();
    test_cipher_validation_and_backends();
    test_sawtooth_vector();
    test_sawtooth_matches_acm_n_primes();
    test_sawtooth_crosscheck_python();
    test_sawtooth_validation_and_limits();

    if (failures != 0) {
        printf("%d failure(s)\n", failures);
        return 1;
    }

    printf("All bidder root C tests passed.\n");
    return 0;
}
