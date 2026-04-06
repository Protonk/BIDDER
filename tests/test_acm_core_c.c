/*
 * test_acm_core_c.c — Tests for the C implementation of ACM core.
 *
 * Mirrors test_acm_core.py. The load-bearing tests (divisibility,
 * square boundary, leading digit preservation, block uniformity,
 * integer accuracy) are the contract both languages must satisfy.
 *
 * Build: gcc -O2 -o test_acm_core_c tests/test_acm_core_c.c acm_core.c -lm
 * Run:   ./test_acm_core_c
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <inttypes.h>
#include "../core/acm_core.h"

static int failures = 0;

#define CHECK(cond, msg) do { \
    if (!(cond)) { printf("  FAIL: %s\n", msg); failures++; } \
} while(0)

#define CHECK_FMT(cond, ...) do { \
    if (!(cond)) { printf("  FAIL: "); printf(__VA_ARGS__); printf("\n"); failures++; } \
} while(0)


/* Leading digit of a positive integer via decimal. */
static int leading_digit(int64_t n)
{
    if (n < 0) n = -n;
    while (n >= 10) n /= 10;
    return (int)n;
}

/* Decimal digit count of a positive integer. */
static int count_digits(int64_t x)
{
    if (x <= 0) return 1;
    int d = 0;
    while (x > 0) { d++; x /= 10; }
    return d;
}


/* ================================================================
 * n_primes — the definition is correct
 * ================================================================ */

static void test_n1_ordinary_primes(void)
{
    printf("--- n=1 ordinary primes ---\n");
    int64_t out[10];
    int64_t expected5[] = {2, 3, 5, 7, 11};
    int64_t expected10[] = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29};

    acm_n_primes(1, 5, out);
    CHECK(memcmp(out, expected5, 5 * sizeof(int64_t)) == 0,
          "n=1 first 5 primes mismatch");

    acm_n_primes(1, 10, out);
    CHECK(memcmp(out, expected10, 10 * sizeof(int64_t)) == 0,
          "n=1 first 10 primes mismatch");
    printf("  OK\n\n");
}

static void test_known_n_primes(void)
{
    printf("--- Known n-primes ---\n");
    int64_t out[5];

    int64_t e2[] = {2, 6, 10, 14, 18};
    acm_n_primes(2, 5, out);
    CHECK(memcmp(out, e2, sizeof(e2)) == 0, "n=2 mismatch");

    int64_t e3[] = {3, 6, 12, 15, 21};
    acm_n_primes(3, 5, out);
    CHECK(memcmp(out, e3, sizeof(e3)) == 0, "n=3 mismatch");

    int64_t e4[] = {4, 8, 12, 20, 24};
    acm_n_primes(4, 5, out);
    CHECK(memcmp(out, e4, sizeof(e4)) == 0, "n=4 mismatch");

    int64_t e5[] = {5, 10, 15, 20, 30};
    acm_n_primes(5, 5, out);
    CHECK(memcmp(out, e5, sizeof(e5)) == 0, "n=5 mismatch");

    int64_t e10[] = {10, 20, 30, 40, 50};
    acm_n_primes(10, 5, out);
    CHECK(memcmp(out, e10, sizeof(e10)) == 0, "n=10 mismatch");

    printf("  OK\n\n");
}

static void test_divisibility_contract(void)
{
    printf("--- Divisibility contract (n=2..20, count=20) ---\n");
    int64_t out[20];
    for (int64_t n = 2; n <= 20; n++) {
        acm_n_primes(n, 20, out);
        for (int i = 0; i < 20; i++) {
            CHECK_FMT(out[i] % n == 0,
                       "n=%" PRId64 ": %" PRId64 " not divisible by %" PRId64,
                       n, out[i], n);
            CHECK_FMT(out[i] % (n * n) != 0,
                       "n=%" PRId64 ": %" PRId64 " divisible by %" PRId64 "^2",
                       n, out[i], n);
        }
    }
    printf("  OK\n\n");
}

static void test_square_boundary_exclusion(void)
{
    printf("--- Square boundary exclusion (n=2..50) ---\n");
    int64_t out[100];
    for (int64_t n = 2; n <= 50; n++) {
        acm_n_primes(n, 100, out);
        int64_t sq = n * n;
        for (int i = 0; i < 100; i++)
            CHECK_FMT(out[i] != sq,
                       "n=%" PRId64 ": n^2=%" PRId64 " found at index %d",
                       n, sq, i);
    }
    printf("  OK\n\n");
}

static void test_first_n_minus_1_below_square(void)
{
    printf("--- First n-1 below n^2, n-th above ---\n");
    for (int64_t n = 2; n <= 20; n++) {
        int cnt = (int)n;
        int64_t *out = malloc(cnt * sizeof(int64_t));
        /* First n-1 should be n, 2n, ..., (n-1)*n */
        acm_n_primes(n, cnt - 1, out);
        for (int i = 0; i < cnt - 1; i++) {
            CHECK_FMT(out[i] == n * (i + 1),
                       "n=%" PRId64 ": prime[%d]=%" PRId64 ", expected %" PRId64,
                       n, i, out[i], n * (i + 1));
            CHECK_FMT(out[i] < n * n,
                       "n=%" PRId64 ": prime[%d]=%" PRId64 " >= n^2=%" PRId64,
                       n, i, out[i], n * n);
        }
        /* n-th n-prime should be (n+1)*n, above n^2 */
        acm_n_primes(n, cnt, out);
        CHECK_FMT(out[cnt - 1] == n * (n + 1),
                   "n=%" PRId64 ": %" PRId64 "-th n-prime=%" PRId64 ", expected %" PRId64,
                   n, n, out[cnt - 1], n * (n + 1));
        CHECK_FMT(out[cnt - 1] > n * n,
                   "n=%" PRId64 ": %" PRId64 "-th n-prime=%" PRId64 " <= n^2=%" PRId64,
                   n, n, out[cnt - 1], n * n);
        free(out);
    }
    printf("  OK\n\n");
}

static void test_monotonicity(void)
{
    printf("--- Monotonicity (n=1..20, count=30) ---\n");
    int64_t out[30];
    for (int64_t n = 1; n <= 20; n++) {
        acm_n_primes(n, 30, out);
        for (int i = 1; i < 30; i++)
            CHECK_FMT(out[i] > out[i - 1],
                       "n=%" PRId64 ": non-monotone at %d: %" PRId64 " >= %" PRId64,
                       n, i, out[i - 1], out[i]);
    }
    printf("  OK\n\n");
}


/* ================================================================
 * Large-n regression (former int overflow)
 * ================================================================ */

static void test_large_n(void)
{
    printf("--- Large n (int64 overflow regression) ---\n");

    /* GPT-5.4 found this: n=1500000000, count=2 overflowed 32-bit int.
     * Python gives [1500000000, 3000000000]. */
    int64_t out[2];
    int64_t n = 1500000000LL;
    acm_n_primes(n, 2, out);
    CHECK_FMT(out[0] == 1500000000LL,
              "first prime: %" PRId64, out[0]);
    CHECK_FMT(out[1] == 3000000000LL,
              "second prime: %" PRId64, out[1]);

    /* Verify champernowne_real and digit_count also work. */
    double c = acm_champernowne_real(n, 2);
    CHECK_FMT(fabs(c - 1.15000000003) < 1e-10,
              "C(1500000000, 2) = %.15f", c);

    int dc = acm_digit_count(n, 2);
    CHECK_FMT(dc == 20,
              "digit_count(1500000000, 2) = %d", dc);

    /* Also check a value where n*k > INT32_MAX for k > 2. */
    int64_t out5[5];
    acm_n_primes(1000000000LL, 5, out5);
    for (int i = 0; i < 5; i++) {
        CHECK_FMT(out5[i] > 0,
                   "n=1e9: prime[%d]=%" PRId64 " is non-positive", i, out5[i]);
        CHECK_FMT(out5[i] % 1000000000LL == 0,
                   "n=1e9: %" PRId64 " not divisible by n", out5[i]);
    }

    /* int64 overflow guard: n near INT64_MAX should fail cleanly
     * through the entire API, not just acm_n_primes. */
    int64_t big_out[2];
    int64_t big_n = INT64_MAX / 2 + 10;
    int rc = acm_n_primes(big_n, 2, big_out);
    CHECK_FMT(rc == -1,
              "acm_n_primes(overflow) should return -1, got %d", rc);

    double big_c = acm_champernowne_real(big_n, 2);
    CHECK_FMT(big_c == 0.0,
              "acm_champernowne_real(overflow) should return 0.0, got %.15f", big_c);

    int big_dc = acm_digit_count(big_n, 2);
    CHECK_FMT(big_dc == -1,
              "acm_digit_count(overflow) should return -1, got %d", big_dc);

    double dec_out[3];
    int dec_rc = acm_decompose(big_n, 2, dec_out);
    CHECK_FMT(dec_rc == -1,
              "acm_decompose(overflow) should return -1, got %d", dec_rc);

    printf("  OK\n\n");
}


/* ================================================================
 * Buffer safety: champernowne_real with large count
 * ================================================================ */

static void test_champernowne_large_count(void)
{
    printf("--- Champernowne large count (buffer safety) ---\n");

    /* count=1000 would produce ~3000+ chars of concatenated primes,
     * well past the 2048-byte buffer. This must not crash. The
     * returned double will be truncated but must be a valid number
     * in [1, 2). */
    double c = acm_champernowne_real(1, 1000);
    CHECK_FMT(c >= 1.0 && c < 2.0,
              "C(1, 1000) = %.15f, expected in [1, 2)", c);

    /* Same with a larger n. */
    c = acm_champernowne_real(50, 500);
    CHECK_FMT(c >= 1.0 && c < 2.0,
              "C(50, 500) = %.15f, expected in [1, 2)", c);

    printf("  OK\n\n");
}


/* ================================================================
 * champernowne_real — the encoding is faithful
 * ================================================================ */

static void test_known_champernowne(void)
{
    printf("--- Known Champernowne real ---\n");
    double c = acm_champernowne_real(2, 5);
    CHECK_FMT(fabs(c - 1.26101418) < 1e-10,
              "C(2,5) = %.10f, expected 1.26101418", c);
    printf("  OK\n\n");
}

static void test_first_n_prime_is_n(void)
{
    printf("--- First n-prime is n (n=2..999) ---\n");
    int64_t out[1];
    for (int64_t n = 2; n <= 999; n++) {
        acm_n_primes(n, 1, out);
        CHECK_FMT(out[0] == n,
                   "n=%" PRId64 ": first n-prime=%" PRId64, n, out[0]);
    }
    printf("  OK\n\n");
}

static void test_leading_digit_preservation(void)
{
    printf("--- Leading digit preservation (n=2..9999) ---\n");
    int64_t out[1];
    for (int64_t n = 2; n <= 9999; n++) {
        acm_n_primes(n, 1, out);
        int fd_prime = leading_digit(out[0]);
        int fd_n = leading_digit(n);
        CHECK_FMT(fd_prime == fd_n,
                   "n=%" PRId64 ": leading digit of first n-prime (%" PRId64 ") is %d, expected %d",
                   n, out[0], fd_prime, fd_n);
    }
    printf("  OK\n\n");
}

static void test_range(void)
{
    printf("--- Range [1.1, 2.0) for n >= 10 ---\n");
    for (int64_t n = 10; n < 1000; n++) {
        double c = acm_champernowne_real(n, 5);
        CHECK_FMT(c >= 1.1 && c < 2.0,
                   "n=%" PRId64 ": C(n)=%.10f out of range", n, c);
    }
    printf("  OK\n\n");
}


/* ================================================================
 * Block boundary uniformity — the theorem
 * ================================================================ */

static void test_block_boundary(int n_max)
{
    printf("--- Block boundary n=1..%d ---\n", n_max);
    int counts[10] = {0};
    for (int n = 1; n <= n_max; n++)
        counts[leading_digit(n)]++;

    int expected = n_max / 9;
    for (int d = 1; d <= 9; d++)
        CHECK_FMT(counts[d] == expected,
                   "digit %d: count %d != %d", d, counts[d], expected);
    printf("  exact %d each: OK\n\n", expected);
}


/* ================================================================
 * first_digit — the extraction works
 * ================================================================ */

static void test_first_digit_powers_of_10(void)
{
    printf("--- first_digit powers of 10 ---\n");
    double p = 1.0;
    for (int i = 0; i < 6; i++) {
        CHECK_FMT(acm_first_digit(p) == 1,
                   "first_digit(10^%d) = %d, expected 1", i, acm_first_digit(p));
        p *= 10.0;
    }
    printf("  OK\n\n");
}

static void test_first_digit_boundaries(void)
{
    printf("--- first_digit boundaries ---\n");
    CHECK(acm_first_digit(1.999) == 1, "1.999 -> 1");
    CHECK(acm_first_digit(2.001) == 2, "2.001 -> 2");
    CHECK(acm_first_digit(9.001) == 9, "9.001 -> 9");
    CHECK(acm_first_digit(9.999) == 9, "9.999 -> 9");
    CHECK(acm_first_digit(0.0051) == 5, "0.0051 -> 5");
    CHECK(acm_first_digit(123456.7) == 1, "123456.7 -> 1");
    printf("  OK\n\n");
}

static void test_first_digit_integer_accuracy(void)
{
    printf("--- first_digit integer accuracy (n=1..9999) ---\n");
    int mismatches = 0;
    for (int n = 1; n <= 9999; n++) {
        int fd = acm_first_digit((double)n);
        int expected = leading_digit(n);
        if (fd != expected) {
            if (mismatches < 5)
                printf("  n=%d: first_digit=%d, expected=%d\n",
                       n, fd, expected);
            mismatches++;
        }
    }
    CHECK_FMT(mismatches == 0,
              "%d mismatches in 1..9999", mismatches);
    printf("  OK\n\n");
}

static void test_first_digit_champernowne(void)
{
    printf("--- first_digit on Champernowne reals ---\n");
    for (int64_t n = 1; n <= 1000; n++) {
        double c = acm_champernowne_real(n, 5);
        int fd = acm_first_digit(c);
        CHECK_FMT(fd == 1,
                   "n=%" PRId64 ": first_digit(C(n))=%d, expected 1 (C(n)=%.10f)",
                   n, fd, c);
    }
    printf("  OK\n\n");
}


/* ================================================================
 * Benford reference
 * ================================================================ */

static void test_benford_sums_to_one(void)
{
    printf("--- Benford sums to 1 ---\n");
    double sum = 0.0;
    for (int d = 1; d <= 9; d++)
        sum += acm_benford(d);
    CHECK_FMT(fabs(sum - 1.0) < 1e-12,
              "Benford sum = %.15f", sum);
    printf("  OK\n\n");
}

static void test_benford_known_value(void)
{
    printf("--- Benford P(1) = log10(2) ---\n");
    double b1 = acm_benford(1);
    CHECK_FMT(fabs(b1 - log10(2.0)) < 1e-15,
              "Benford P(1) = %.15f", b1);
    printf("  OK\n\n");
}

static void test_benford_decreasing(void)
{
    printf("--- Benford strictly decreasing ---\n");
    for (int d = 2; d <= 9; d++)
        CHECK_FMT(acm_benford(d) < acm_benford(d - 1),
                   "Benford not decreasing at d=%d", d);
    printf("  OK\n\n");
}


/* ================================================================
 * digit_count
 * ================================================================ */

static void test_digit_count_known(void)
{
    printf("--- digit_count known value ---\n");
    int dc = acm_digit_count(2, 5);
    CHECK_FMT(dc == 8, "digit_count(2,5) = %d, expected 8", dc);
    printf("  OK\n\n");
}

static void test_digit_count_consistency(void)
{
    printf("--- digit_count consistency (n=1..49) ---\n");
    for (int64_t n = 1; n < 50; n++) {
        int counts[] = {1, 5, 10};
        for (int ci = 0; ci < 3; ci++) {
            int count = counts[ci];
            int64_t *primes = malloc(count * sizeof(int64_t));
            acm_n_primes(n, count, primes);
            int expected = 0;
            for (int i = 0; i < count; i++)
                expected += count_digits(primes[i]);
            int actual = acm_digit_count(n, count);
            CHECK_FMT(actual == expected,
                       "n=%" PRId64 ", count=%d: digit_count=%d != %d",
                       n, count, actual, expected);
            free(primes);
        }
    }
    printf("  OK\n\n");
}


/* ================================================================
 * Decompose
 * ================================================================ */

static void test_decompose(void)
{
    printf("--- Decompose ---\n");
    double out[3];

    /* n=2, count=5: C(2,5) = 1.26101418, digit_count = 8 */
    acm_decompose(2, 5, out);
    double c = acm_champernowne_real(2, 5);
    CHECK_FMT(fabs(out[0] - log(c)) < 1e-15,
              "ln(champernowne): %.15f != %.15f", out[0], log(c));
    CHECK_FMT(fabs(out[1] - log(2.0)) < 1e-15,
              "ln(primality): %.15f != %.15f", out[1], log(2.0));
    CHECK_FMT(fabs(out[2] - log(8.0 / 5.0)) < 1e-15,
              "ln(digitfrac): %.15f != %.15f", out[2], log(8.0 / 5.0));

    /* n=10, count=5: C(10,5) = 1.102030405, digit_count = 10 */
    acm_decompose(10, 5, out);
    c = acm_champernowne_real(10, 5);
    CHECK_FMT(fabs(out[0] - log(c)) < 1e-15,
              "ln(champernowne): %.15f != %.15f", out[0], log(c));
    CHECK_FMT(fabs(out[1] - log(10.0)) < 1e-15,
              "ln(primality): %.15f != %.15f", out[1], log(10.0));
    CHECK_FMT(fabs(out[2] - log(10.0 / 5.0)) < 1e-15,
              "ln(digitfrac): %.15f != %.15f", out[2], log(10.0 / 5.0));

    /* Invalid input */
    CHECK(acm_decompose(0, 5, out) == -1, "decompose(0,5) should fail");
    CHECK(acm_decompose(2, 0, out) == -1, "decompose(2,0) should fail");

    printf("  OK\n\n");
}


/* ================================================================
 * Cross-language checks (hardcoded Python output)
 * ================================================================ */

static void test_cross_language(void)
{
    printf("--- Cross-language check (Python values) ---\n");

    /* n_primes */
    int64_t out[10];
    acm_n_primes(3, 5, out);
    int64_t e3[] = {3, 6, 12, 15, 21};
    CHECK(memcmp(out, e3, sizeof(e3)) == 0, "n_primes(3,5) mismatch");

    acm_n_primes(1, 5, out);
    int64_t e1[] = {2, 3, 5, 7, 11};
    CHECK(memcmp(out, e1, sizeof(e1)) == 0, "n_primes(1,5) mismatch");

    /* champernowne_real */
    double c2 = acm_champernowne_real(2, 5);
    CHECK_FMT(fabs(c2 - 1.26101418) < 1e-10,
              "C(2,5) = %.10f", c2);

    double c10 = acm_champernowne_real(10, 5);
    CHECK_FMT(fabs(c10 - 1.1020304050) < 1e-10,
              "C(10,5) = %.10f", c10);

    /* digit_count */
    CHECK_FMT(acm_digit_count(2, 5) == 8,
              "digit_count(2,5) = %d", acm_digit_count(2, 5));
    CHECK_FMT(acm_digit_count(10, 5) == 10,
              "digit_count(10,5) = %d", acm_digit_count(10, 5));

    /* first_digit */
    CHECK_FMT(acm_first_digit(1.26101418) == 1,
              "first_digit(1.26101418) = %d", acm_first_digit(1.26101418));
    CHECK_FMT(acm_first_digit(42.0) == 4,
              "first_digit(42.0) = %d", acm_first_digit(42.0));

    /* benford */
    CHECK_FMT(fabs(acm_benford(1) - 0.30103) < 1e-4,
              "benford(1) = %.6f", acm_benford(1));

    printf("  OK\n\n");
}


/* ================================================================
 * Champernowne precision: cross-language round-trip
 * ================================================================ */

static void test_champernowne_precision(void)
{
    printf("--- Champernowne precision (cross-language round-trip) ---\n");

    struct { int64_t n; int count; double py_value; int frac_digits; } cases[] = {
        {    2,  3,  1.261,                4 },
        {    2,  5,  1.26101418,           8 },
        {    5,  5,  1.51015203,           9 },
        {   10,  5,  1.102030405,         10 },
        {    1,  5,  1.235711,             6 },
        {    1, 10,  1.2357111317192329,  16 },
        {    7, 10,  1.7142128354256636,  19 },
        {    3, 10,  1.3612152124303338,  18 },
        {   99,  5,  1.99198297396495,    14 },
        {  100,  5,  1.1002003004005,     15 },
        {    2, 20,  1.2610141822263035,  38 },
        { 1000,  5,  1.1000200030004001, 20 },
        {   50, 10,  1.501001502002503,  29 },
    };
    int n_cases = sizeof(cases) / sizeof(cases[0]);

    for (int i = 0; i < n_cases; i++) {
        double c = acm_champernowne_real(cases[i].n, cases[i].count);
        double tol = (cases[i].frac_digits <= 16) ? 0.0 : 5e-16;
        CHECK_FMT(fabs(c - cases[i].py_value) <= tol,
                   "n=%" PRId64 " count=%d: C=%.17g, Python=%.17g (frac_digits=%d)",
                   cases[i].n, cases[i].count, c, cases[i].py_value,
                   cases[i].frac_digits);
    }
    printf("  %d cases checked: OK\n\n", n_cases);
}


/* ================================================================
 * Main
 * ================================================================ */

int main(void)
{
    printf("=== ACM core C tests ===\n\n");

    test_n1_ordinary_primes();
    test_known_n_primes();
    test_divisibility_contract();
    test_square_boundary_exclusion();
    test_first_n_minus_1_below_square();
    test_monotonicity();
    test_large_n();
    test_champernowne_large_count();

    test_known_champernowne();
    test_first_n_prime_is_n();
    test_leading_digit_preservation();
    test_range();

    test_block_boundary(99);
    test_block_boundary(999);
    test_block_boundary(9999);

    test_first_digit_powers_of_10();
    test_first_digit_boundaries();
    test_first_digit_integer_accuracy();
    test_first_digit_champernowne();

    test_benford_sums_to_one();
    test_benford_known_value();
    test_benford_decreasing();

    test_digit_count_known();
    test_digit_count_consistency();

    test_decompose();
    test_cross_language();
    test_champernowne_precision();

    if (failures == 0)
        printf("\nAll ACM core C tests passed.\n");
    else
        printf("\n%d test(s) FAILED.\n", failures);

    return failures;
}
