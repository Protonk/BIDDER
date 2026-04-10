/*
 * test_bidder_c.c — Tests for the C implementation of BIDDER.
 *
 * Verifies:
 *   1. Speck32/64 test vector from the paper
 *   2. Exact uniformity over full period (base 10, d=2..4)
 *   3. Key sensitivity
 *   4. Determinism (reset)
 *   5. Cross-check against Python (printed for manual comparison)
 *
 * Build: gcc -O2 -o test_bidder_c tests/test_bidder_c.c generator/bidder.c -lm
 * Run:   ./test_bidder_c
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../generator/bidder.h"

static int failures = 0;

#define CHECK(cond, msg) do { \
    if (!(cond)) { printf("  FAIL: %s\n", msg); failures++; } \
} while(0)


/* ================================================================
 * Test 1: Speck32/64 test vector
 * ================================================================ */

/* Expose the internal encrypt for testing */
extern uint32_t speck32_encrypt(uint32_t pt, const uint16_t rk[22]);
extern void speck32_expand_key(const uint8_t key[8], uint16_t rk[22]);

static void test_speck_vector(void)
{
    printf("--- Speck32/64 test vector ---\n");
    /* Key: 1918 1110 0908 0100 (little-endian byte order) */
    uint8_t key[8] = {0x00, 0x01, 0x08, 0x09, 0x10, 0x11, 0x18, 0x19};
    uint16_t rk[22];
    speck32_expand_key(key, rk);

    /* PT: 6574 694c -> packed as (0x6574 << 16) | 0x694c */
    uint32_t pt = (0x6574u << 16) | 0x694cu;
    uint32_t ct = speck32_encrypt(pt, rk);
    uint32_t expected = (0xa868u << 16) | 0x42f2u;

    printf("  PT: %08x  CT: %08x  expected: %08x\n", pt, ct, expected);
    CHECK(ct == expected, "Speck32/64 test vector mismatch");
    printf("  OK\n\n");
}


/* ================================================================
 * Test 2: Exact uniformity
 * ================================================================ */

static void test_uniformity(uint64_t base, uint32_t digit_class)
{
    printf("--- Uniformity: base=%llu, d=%u ---\n",
           (unsigned long long)base, digit_class);

    bidder_ctx ctx;
    int rc = bidder_init(&ctx, base, digit_class, (const uint8_t *)"test", 4);
    CHECK(rc == 0, "bidder_init failed");

    uint64_t period = ctx.block_size;
    uint32_t alphabet = (uint32_t)(base - 1);
    uint64_t expected = period / alphabet;

    /* Count digit frequencies */
    uint64_t *counts = calloc(base, sizeof(uint64_t));
    CHECK(counts != NULL, "alloc failed");

    for (uint64_t i = 0; i < period; i++) {
        uint32_t d = bidder_next(&ctx);
        CHECK(d >= 1 && d < base, "output out of range");
        counts[d]++;
    }

    int exact = 1;
    for (uint32_t d = 1; d < base; d++) {
        if (counts[d] != expected) {
            printf("  digit %u: count %llu != expected %llu\n",
                   d, (unsigned long long)counts[d],
                   (unsigned long long)expected);
            exact = 0;
        }
    }
    CHECK(exact, "non-uniform distribution");
    printf("  period=%llu, %u symbols, %llu each: %s\n",
           (unsigned long long)period, alphabet,
           (unsigned long long)expected,
           exact ? "EXACT" : "FAIL");

    free(counts);
}


/* ================================================================
 * Test 3: Key sensitivity
 * ================================================================ */

static void test_key_sensitivity(void)
{
    printf("--- Key sensitivity ---\n");
    bidder_ctx a, b;
    bidder_init(&a, 10, 3, (const uint8_t *)"alpha", 5);
    bidder_init(&b, 10, 3, (const uint8_t *)"bravo", 5);

    int differ = 0;
    for (int i = 0; i < 50; i++) {
        if (bidder_next(&a) != bidder_next(&b))
            differ = 1;
    }
    CHECK(differ, "different keys produced identical output");
    printf("  OK\n\n");
}


/* ================================================================
 * Test 4: Determinism (reset)
 * ================================================================ */

static void test_reset(void)
{
    printf("--- Reset ---\n");
    bidder_ctx ctx;
    bidder_init(&ctx, 10, 3, (const uint8_t *)"reset", 5);

    uint32_t first[50];
    for (int i = 0; i < 50; i++)
        first[i] = bidder_next(&ctx);

    bidder_reset(&ctx);

    int match = 1;
    for (int i = 0; i < 50; i++) {
        if (bidder_next(&ctx) != first[i])
            match = 0;
    }
    CHECK(match, "reset did not reproduce output");
    printf("  OK\n\n");
}


/* ================================================================
 * Test 5: Cross-check (print first 20 for manual comparison with Python)
 * ================================================================ */

static void test_crosscheck(void)
{
    printf("--- Cross-check (compare with Python) ---\n");

    printf("  base=10 d=2 key='test':\n    C:  ");
    bidder_ctx ctx;
    bidder_init(&ctx, 10, 2, (const uint8_t *)"test", 4);
    for (int i = 0; i < 20; i++)
        printf("%u ", bidder_next(&ctx));
    printf("\n");

    printf("  base=10 d=3 key='test':\n    C:  ");
    bidder_init(&ctx, 10, 3, (const uint8_t *)"test", 4);
    for (int i = 0; i < 20; i++)
        printf("%u ", bidder_next(&ctx));
    printf("\n\n");
}


/* ================================================================
 * Test 6a: bidder_at — random access (parity work, see core/API-PLAN.md)
 * ================================================================ */

static void test_at_matches_next(void)
{
    printf("--- bidder_at matches bidder_next sequence ---\n");

    bidder_ctx ctx_seq, ctx_at;
    bidder_init(&ctx_seq, 10, 3, (const uint8_t *)"at-test", 7);
    bidder_init(&ctx_at,  10, 3, (const uint8_t *)"at-test", 7);

    int match = 1;
    uint64_t period = ctx_seq.block_size;
    for (uint64_t i = 0; i < period; i++) {
        uint32_t s = bidder_next(&ctx_seq);
        uint32_t r = bidder_at(&ctx_at, i);
        if (s != r) match = 0;
    }
    CHECK(match, "bidder_at sequence diverges from bidder_next");
    printf("  OK (period %llu)\n\n", (unsigned long long)period);
}

static void test_at_is_stateless(void)
{
    printf("--- bidder_at is stateless under interleaving ---\n");

    bidder_ctx ctx, ref;
    bidder_init(&ctx, 10, 3, (const uint8_t *)"stateless", 9);
    bidder_init(&ref, 10, 3, (const uint8_t *)"stateless", 9);

    /* Build the reference next() sequence first */
    uint32_t expected[20];
    for (int i = 0; i < 20; i++)
        expected[i] = bidder_next(&ref);

    /* Now interleave at() and next() on ctx; the next() outputs should
       still match the reference */
    int match = 1;
    for (int i = 0; i < 20; i++) {
        (void)bidder_at(&ctx, (uint64_t)(i * 7) % ctx.block_size);
        (void)bidder_at(&ctx, 0);
        uint32_t s = bidder_next(&ctx);
        if (s != expected[i]) match = 0;
    }
    CHECK(match, "bidder_at leaked state into bidder_next sequence");
    printf("  OK\n\n");
}

static void test_at_out_of_range(void)
{
    printf("--- bidder_at out-of-range returns 0 ---\n");

    bidder_ctx ctx;
    bidder_init(&ctx, 10, 2, (const uint8_t *)"oor", 3);
    /* period == block_size == 90 */
    CHECK(bidder_at(&ctx, ctx.block_size) == 0,
          "at(period) should return 0 sentinel");
    CHECK(bidder_at(&ctx, ctx.block_size + 1) == 0,
          "at(period+1) should return 0 sentinel");
    CHECK(bidder_at(&ctx, UINT64_MAX) == 0,
          "at(UINT64_MAX) should return 0 sentinel");
    printf("  OK\n\n");
}

static void test_at_crosscheck_feistel(void)
{
    printf("--- bidder_at cross-check (Python feistel) ---\n");

    bidder_ctx ctx;
    bidder_init(&ctx, 10, 2, (const uint8_t *)"test", 4);
    uint32_t expected[20] = {
        3, 8, 1, 2, 7, 1, 5, 4, 7, 4,
        2, 5, 8, 7, 8, 9, 2, 9, 6, 7
    };
    int match = 1;
    for (int i = 0; i < 20; i++) {
        if (bidder_at(&ctx, (uint64_t)i) != expected[i]) {
            match = 0;
            printf("  index %d: got %u, expected %u\n",
                   i, bidder_at(&ctx, (uint64_t)i), expected[i]);
        }
    }
    CHECK(match, "bidder_at feistel cross-check failed");
    printf("  OK\n\n");
}

static void test_at_crosscheck_speck(void)
{
    printf("--- bidder_at cross-check (Python speck) ---\n");

    /* Same fixture as test_at_cross_check_speck in tests/test_bidder.py:
       base=65536, d=2 lands in Speck32 mode (tight fit). */
    bidder_ctx ctx;
    bidder_init(&ctx, 65536, 2, (const uint8_t *)"speck parity", 12);
    CHECK(ctx.mode == 0, "expected Speck mode for base=65536 d=2");

    uint32_t expected[10] = {
        13270, 65198, 24145, 34590, 8655,
        22902, 22414, 22244, 30259, 20443
    };
    int match = 1;
    for (int i = 0; i < 10; i++) {
        uint32_t v = bidder_at(&ctx, (uint64_t)i);
        if (v != expected[i]) {
            match = 0;
            printf("  index %d: got %u, expected %u\n",
                   i, v, expected[i]);
        }
    }
    CHECK(match, "bidder_at speck cross-check failed");
    printf("  OK\n\n");
}


/* ================================================================
 * Test 6: Period wraparound
 * ================================================================ */

static void test_wraparound(void)
{
    printf("--- Period wraparound ---\n");
    bidder_ctx ctx;
    bidder_init(&ctx, 10, 2, (const uint8_t *)"wrap", 4);

    uint32_t first_period[90];
    for (int i = 0; i < 90; i++)
        first_period[i] = bidder_next(&ctx);

    /* Counter should have wrapped */
    int match = 1;
    for (int i = 0; i < 90; i++) {
        if (bidder_next(&ctx) != first_period[i])
            match = 0;
    }
    CHECK(match, "period wraparound failed");
    printf("  OK\n\n");
}


/* ================================================================
 * Main
 * ================================================================ */

int main(void)
{
    printf("=== BIDDER C implementation tests ===\n\n");

    test_speck_vector();

    test_uniformity(10, 2);    /* period 90 */
    test_uniformity(10, 3);    /* period 900 */
    test_uniformity(10, 4);    /* period 9000 */
    test_uniformity(16, 2);    /* period 240 */
    test_uniformity(7, 3);     /* period 294 */

    test_key_sensitivity();
    test_reset();
    test_wraparound();

    test_at_matches_next();
    test_at_is_stateless();
    test_at_out_of_range();
    test_at_crosscheck_feistel();
    test_at_crosscheck_speck();

    test_crosscheck();

    if (failures == 0)
        printf("\nAll C tests passed.\n");
    else
        printf("\n%d test(s) FAILED.\n", failures);

    return failures;
}
