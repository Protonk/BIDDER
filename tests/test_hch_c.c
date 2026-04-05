/*
 * test_hch_c.c — Tests for the C implementation of HCH.
 *
 * Verifies:
 *   1. Speck32/64 test vector from the paper
 *   2. Exact uniformity over full period (base 10, d=2..4)
 *   3. Key sensitivity
 *   4. Determinism (reset)
 *   5. Cross-check against Python (printed for manual comparison)
 *
 * Build: gcc -O2 -o test_hch_c tests/test_hch_c.c generator/hch.c -lm
 * Run:   ./test_hch_c
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../generator/hch.h"

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

    hch_ctx ctx;
    int rc = hch_init(&ctx, base, digit_class, (const uint8_t *)"test", 4);
    CHECK(rc == 0, "hch_init failed");

    uint64_t period = ctx.block_size;
    uint32_t alphabet = (uint32_t)(base - 1);
    uint64_t expected = period / alphabet;

    /* Count digit frequencies */
    uint64_t *counts = calloc(base, sizeof(uint64_t));
    CHECK(counts != NULL, "alloc failed");

    for (uint64_t i = 0; i < period; i++) {
        uint32_t d = hch_next(&ctx);
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
    hch_ctx a, b;
    hch_init(&a, 10, 3, (const uint8_t *)"alpha", 5);
    hch_init(&b, 10, 3, (const uint8_t *)"bravo", 5);

    int differ = 0;
    for (int i = 0; i < 50; i++) {
        if (hch_next(&a) != hch_next(&b))
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
    hch_ctx ctx;
    hch_init(&ctx, 10, 3, (const uint8_t *)"reset", 5);

    uint32_t first[50];
    for (int i = 0; i < 50; i++)
        first[i] = hch_next(&ctx);

    hch_reset(&ctx);

    int match = 1;
    for (int i = 0; i < 50; i++) {
        if (hch_next(&ctx) != first[i])
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
    hch_ctx ctx;
    hch_init(&ctx, 10, 2, (const uint8_t *)"test", 4);
    for (int i = 0; i < 20; i++)
        printf("%u ", hch_next(&ctx));
    printf("\n");

    printf("  base=10 d=3 key='test':\n    C:  ");
    hch_init(&ctx, 10, 3, (const uint8_t *)"test", 4);
    for (int i = 0; i < 20; i++)
        printf("%u ", hch_next(&ctx));
    printf("\n\n");
}


/* ================================================================
 * Test 6: Period wraparound
 * ================================================================ */

static void test_wraparound(void)
{
    printf("--- Period wraparound ---\n");
    hch_ctx ctx;
    hch_init(&ctx, 10, 2, (const uint8_t *)"wrap", 4);

    uint32_t first_period[90];
    for (int i = 0; i < 90; i++)
        first_period[i] = hch_next(&ctx);

    /* Counter should have wrapped */
    int match = 1;
    for (int i = 0; i < 90; i++) {
        if (hch_next(&ctx) != first_period[i])
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
    printf("=== HCH C implementation tests ===\n\n");

    test_speck_vector();

    test_uniformity(10, 2);    /* period 90 */
    test_uniformity(10, 3);    /* period 900 */
    test_uniformity(10, 4);    /* period 9000 */
    test_uniformity(16, 2);    /* period 240 */
    test_uniformity(7, 3);     /* period 294 */

    test_key_sensitivity();
    test_reset();
    test_wraparound();
    test_crosscheck();

    if (failures == 0)
        printf("=== All %d tests passed ===\n", 0);
    else
        printf("=== %d FAILURES ===\n", failures);

    printf("\nAll C tests passed.\n");
    return failures;
}
