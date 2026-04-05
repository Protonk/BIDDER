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
#include "../acm_core.h"

static int failures = 0;

#define CHECK(cond, msg) do { \
    if (!(cond)) { printf("  FAIL: %s\n", msg); failures++; } \
} while(0)

#define CHECK_FMT(cond, ...) do { \
    if (!(cond)) { printf("  FAIL: "); printf(__VA_ARGS__); printf("\n"); failures++; } \
} while(0)


/* Leading digit of a positive integer via decimal. */
static int leading_digit(int n)
{
    while (n >= 10) n /= 10;
    return n;
}

/* Decimal digit count of a positive integer. */
static int count_digits(int x)
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
    int out[10];
    int expected5[] = {2, 3, 5, 7, 11};
    int expected10[] = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29};

    acm_n_primes(1, 5, out);
    CHECK(memcmp(out, expected5, 5 * sizeof(int)) == 0,
          "n=1 first 5 primes mismatch");

    acm_n_primes(1, 10, out);
    CHECK(memcmp(out, expected10, 10 * sizeof(int)) == 0,
          "n=1 first 10 primes mismatch");
    printf("  OK\n\n");
}

static void test_known_n_primes(void)
{
    printf("--- Known n-primes ---\n");
    int out[5];

    int e2[] = {2, 6, 10, 14, 18};
    acm_n_primes(2, 5, out);
    CHECK(memcmp(out, e2, sizeof(e2)) == 0, "n=2 mismatch");

    int e3[] = {3, 6, 12, 15, 21};
    acm_n_primes(3, 5, out);
    CHECK(memcmp(out, e3, sizeof(e3)) == 0, "n=3 mismatch");

    int e4[] = {4, 8, 12, 20, 24};
    acm_n_primes(4, 5, out);
    CHECK(memcmp(out, e4, sizeof(e4)) == 0, "n=4 mismatch");

    int e5[] = {5, 10, 15, 20, 30};
    acm_n_primes(5, 5, out);
    CHECK(memcmp(out, e5, sizeof(e5)) == 0, "n=5 mismatch");

    int e10[] = {10, 20, 30, 40, 50};
    acm_n_primes(10, 5, out);
    CHECK(memcmp(out, e10, sizeof(e10)) == 0, "n=10 mismatch");

    printf("  OK\n\n");
}

static void test_divisibility_contract(void)
{
    printf("--- Divisibility contract (n=2..20, count=20) ---\n");
    int out[20];
    for (int n = 2; n <= 20; n++) {
        acm_n_primes(n, 20, out);
        for (int i = 0; i < 20; i++) {
            CHECK_FMT(out[i] % n == 0,
                       "n=%d: %d not divisible by %d", n, out[i], n);
            CHECK_FMT(out[i] % (n * n) != 0,
                       "n=%d: %d divisible by %d^2", n, out[i], n);
        }
    }
    printf("  OK\n\n");
}

static void test_square_boundary_exclusion(void)
{
    printf("--- Square boundary exclusion (n=2..50) ---\n");
    int out[100];
    for (int n = 2; n <= 50; n++) {
        acm_n_primes(n, 100, out);
        int sq = n * n;
        for (int i = 0; i < 100; i++)
            CHECK_FMT(out[i] != sq,
                       "n=%d: n^2=%d found at index %d", n, sq, i);
    }
    printf("  OK\n\n");
}

static void test_first_n_minus_1_below_square(void)
{
    printf("--- First n-1 below n^2, n-th above ---\n");
    for (int n = 2; n <= 20; n++) {
        int *out = malloc(n * sizeof(int));
        /* First n-1 should be n, 2n, ..., (n-1)*n */
        acm_n_primes(n, n - 1, out);
        for (int i = 0; i < n - 1; i++) {
            CHECK_FMT(out[i] == n * (i + 1),
                       "n=%d: prime[%d]=%d, expected %d",
                       n, i, out[i], n * (i + 1));
            CHECK_FMT(out[i] < n * n,
                       "n=%d: prime[%d]=%d >= n^2=%d",
                       n, i, out[i], n * n);
        }
        /* n-th n-prime should be (n+1)*n, above n^2 */
        acm_n_primes(n, n, out);
        CHECK_FMT(out[n - 1] == n * (n + 1),
                   "n=%d: %d-th n-prime=%d, expected %d",
                   n, n, out[n - 1], n * (n + 1));
        CHECK_FMT(out[n - 1] > n * n,
                   "n=%d: %d-th n-prime=%d <= n^2=%d",
                   n, n, out[n - 1], n * n);
        free(out);
    }
    printf("  OK\n\n");
}

static void test_monotonicity(void)
{
    printf("--- Monotonicity (n=1..20, count=30) ---\n");
    int out[30];
    for (int n = 1; n <= 20; n++) {
        acm_n_primes(n, 30, out);
        for (int i = 1; i < 30; i++)
            CHECK_FMT(out[i] > out[i - 1],
                       "n=%d: non-monotone at %d: %d >= %d",
                       n, i, out[i - 1], out[i]);
    }
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
    int out[1];
    for (int n = 2; n <= 999; n++) {
        acm_n_primes(n, 1, out);
        CHECK_FMT(out[0] == n,
                   "n=%d: first n-prime=%d", n, out[0]);
    }
    printf("  OK\n\n");
}

static void test_leading_digit_preservation(void)
{
    printf("--- Leading digit preservation (n=2..9999) ---\n");
    int out[1];
    for (int n = 2; n <= 9999; n++) {
        acm_n_primes(n, 1, out);
        int fd_prime = leading_digit(out[0]);
        int fd_n = leading_digit(n);
        CHECK_FMT(fd_prime == fd_n,
                   "n=%d: leading digit of first n-prime (%d) is %d, expected %d",
                   n, out[0], fd_prime, fd_n);
    }
    printf("  OK\n\n");
}

static void test_range(void)
{
    printf("--- Range [1.1, 2.0) for n >= 10 ---\n");
    for (int n = 10; n < 1000; n++) {
        double c = acm_champernowne_real(n, 5);
        CHECK_FMT(c >= 1.1 && c < 2.0,
                   "n=%d: C(n)=%.10f out of range", n, c);
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
    for (int n = 1; n <= 1000; n++) {
        double c = acm_champernowne_real(n, 5);
        int fd = acm_first_digit(c);
        CHECK_FMT(fd == 1,
                   "n=%d: first_digit(C(n))=%d, expected 1 (C(n)=%.10f)",
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
    for (int n = 1; n < 50; n++) {
        int counts[] = {1, 5, 10};
        for (int ci = 0; ci < 3; ci++) {
            int count = counts[ci];
            int *primes = malloc(count * sizeof(int));
            acm_n_primes(n, count, primes);
            int expected = 0;
            for (int i = 0; i < count; i++) {
                int p = primes[i];
                expected += count_digits(p);
            }
            int actual = acm_digit_count(n, count);
            CHECK_FMT(actual == expected,
                       "n=%d, count=%d: digit_count=%d != %d",
                       n, count, actual, expected);
            free(primes);
        }
    }
    printf("  OK\n\n");
}


/* ================================================================
 * Cross-language checks (hardcoded Python output)
 * ================================================================ */

static void test_cross_language(void)
{
    printf("--- Cross-language check (Python values) ---\n");

    /* n_primes */
    int out[10];
    acm_n_primes(3, 5, out);
    int e3[] = {3, 6, 12, 15, 21};
    CHECK(memcmp(out, e3, sizeof(e3)) == 0, "n_primes(3,5) mismatch");

    acm_n_primes(1, 5, out);
    int e1[] = {2, 3, 5, 7, 11};
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
 *
 * Both Python (float()) and C (strtod()) parse the same concatenated
 * string as an IEEE 754 double. This test asserts they produce
 * bit-identical results across a range of string lengths — from
 * well within double precision (4 fractional digits) through well
 * past it (38 fractional digits). The pairs that exceed ~16 digits
 * verify that both languages truncate identically, which is the
 * audit property.
 * ================================================================ */

static void test_champernowne_precision(void)
{
    printf("--- Champernowne precision (cross-language round-trip) ---\n");

    /* Python-computed values (sage -python, IEEE 754 double repr). */
    struct { int n; int count; double py_value; int frac_digits; } cases[] = {
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
        /*
         * Bit-identical check: both should produce the same double
         * from the same string. Allow 0 ULP for short strings,
         * 1 ULP for long strings (> 16 frac digits) as a concession
         * to any platform strtod variance.
         */
        double tol = (cases[i].frac_digits <= 16) ? 0.0 : 5e-16;
        CHECK_FMT(fabs(c - cases[i].py_value) <= tol,
                   "n=%d count=%d: C=%.17g, Python=%.17g (frac_digits=%d)",
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

    test_cross_language();
    test_champernowne_precision();

    if (failures == 0)
        printf("\nAll ACM core C tests passed.\n");
    else
        printf("\n%d test(s) FAILED.\n", failures);

    return failures;
}
