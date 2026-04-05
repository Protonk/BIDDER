/*
 * acm_core.h — ACM-Champernowne core definitions (C implementation)
 *
 * n-prime generation, Champernowne real construction, first-digit
 * extraction, and Benford reference. No external dependencies beyond
 * the C standard library.
 *
 * Usage:
 *     int primes[5];
 *     acm_n_primes(2, 5, primes);
 *     // primes = {2, 6, 10, 14, 18}
 *
 *     double c = acm_champernowne_real(2, 5);
 *     // c = 1.26101418
 *
 *     int d = acm_first_digit(1234.5);
 *     // d = 1
 */

#ifndef ACM_CORE_H
#define ACM_CORE_H

/*
 * Write the first `count` n-primes into `out`.
 *
 * For n = 1: ordinary primes (trial division).
 * For n >= 2: elements n*k where k is not divisible by n.
 *
 * Caller must ensure out has room for `count` elements.
 * Returns 0 on success, -1 on invalid input (n < 1 or count < 1).
 */
int acm_n_primes(int n, int count, int *out);

/*
 * Construct the n-Champernowne real from the first `count` n-primes.
 *
 * Concatenates decimal representations after "1." and returns the
 * result as a double. Subject to IEEE 754 truncation for long
 * concatenations.
 *
 * Returns 0.0 on invalid input.
 */
double acm_champernowne_real(int n, int count);

/*
 * Total decimal digits used by the first `count` n-primes.
 * Returns -1 on invalid input.
 */
int acm_digit_count(int n, int count);

/*
 * Extract the leading significant digit (1-9) of a positive number.
 * Returns 0 for non-positive input.
 */
int acm_first_digit(double x);

/*
 * Benford's law probability for digit d (1-9).
 * Returns log10(1 + 1/d).
 * Returns 0.0 for d outside [1, 9].
 */
double acm_benford(int d);

#endif /* ACM_CORE_H */
