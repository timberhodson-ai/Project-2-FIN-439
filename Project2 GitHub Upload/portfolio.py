"""Lab 14 risk engine. Training inputs; returns/volatilities use decimals."""

import math

# Editable course-authored inputs, in the order used by CORRELATIONS.
SLEEVES = {
    "Treasury bills": (0.035, 0.005),
    "Treasury 10-year note": (0.043, 0.070),
    "Investment-grade bond fund": (0.050, 0.060),
    "Global equity index fund": (0.080, 0.160),
}
CORRELATIONS = [
    [1.00, 0.10, 0.05, 0.00],
    [0.10, 1.00, 0.80, -0.10],
    [0.05, 0.80, 1.00, 0.25],
    [0.00, -0.10, 0.25, 1.00],
]
CPI_ESTIMATE = 0.025  # Labelled estimate, not a market observation.
OBJECTIVE_RETURN = 0.065  # CPI estimate + 4 percentage points.
RESERVE_ELIGIBLE = {"Treasury bills", "Treasury 10-year note"}


def validate_inputs(sleeves, correlations):
    n = len(sleeves)
    if not 3 <= n <= 6:
        raise ValueError("Use three to six assets.")
    if len(correlations) != n or any(len(row) != n for row in correlations):
        raise ValueError("Correlation table must have one row/column per sleeve.")
    for name, (expected, volatility) in sleeves.items():
        if not math.isfinite(expected) or not math.isfinite(volatility) or volatility <= 0:
            raise ValueError(f"{name}: return must be finite and volatility positive.")
    for i in range(n):
        for j in range(n):
            value = correlations[i][j]
            if not math.isfinite(value) or not -1 <= value <= 1:
                raise ValueError(f"Correlation [{i + 1}, {j + 1}] must be between -1 and 1.")
            if not math.isclose(value, correlations[j][i], rel_tol=0, abs_tol=1e-12):
                raise ValueError("Correlation table must be symmetric; change both cells.")
        if not math.isclose(correlations[i][i], 1, rel_tol=0, abs_tol=1e-12):
            raise ValueError("Each diagonal correlation must equal 1.")


def covariance_matrix(sleeves, correlations):
    validate_inputs(sleeves, correlations)
    vols = [values[1] for values in sleeves.values()]
    return [[correlations[i][j] * vols[i] * vols[j]
             for j in range(len(vols))] for i in range(len(vols))]


def inverse_volatility_weights(sleeves):
    inverse = [1 / values[1] for values in sleeves.values()]
    return [value / sum(inverse) for value in inverse]


def baseline_portfolios(sleeves):
    return {"Benchmark": [0, 0, 0.4, 0.6],
            "Equal weight": [1 / len(sleeves)] * len(sleeves),
            "Inverse volatility": inverse_volatility_weights(sleeves)}


def expected_return(weights, sleeves):
    return sum(weight * values[0] for weight, values in zip(weights, sleeves.values()))


def portfolio_volatility(weights, covariance):
    # Double sum includes both cross terms: w_i * w_j * rho_ij * sigma_i * sigma_j.
    variance = sum(weights[i] * weights[j] * covariance[i][j]
                   for i in range(len(weights)) for j in range(len(weights)))
    if variance < -1e-12:
        raise ValueError("Inputs produce negative portfolio variance.")
    return math.sqrt(max(0, variance))


def reserve_weight(weights, sleeves):
    return sum(weight for name, weight in zip(sleeves, weights) if name in RESERVE_ELIGIBLE)


def meets_objective(result, objective):
    return result >= objective


def evaluate_portfolio(weights, sleeves, covariance, objective):
    if (len(weights) != len(sleeves) or
            any(not math.isfinite(w) or w < 0 for w in weights) or
            not math.isclose(sum(weights), 1, abs_tol=1e-12)):
        raise ValueError("Weights must be finite, nonnegative, and sum to 1.")
    result = expected_return(weights, sleeves)
    return {"return": result, "volatility": portfolio_volatility(weights, covariance),
            "reserve": reserve_weight(weights, sleeves),
            "meets_objective": meets_objective(result, objective)}


def search_mix(sleeves, correlations, objective, reserve_minimum=0.03,
               reserve_eligible=None, minimum_weights=None, maximum_weights=None):
    """Exhaust every fully invested long-only mix on the 5 percentage point grid.

    Return a result dictionary or None. Ties retain the first enumerated mix.
    All numeric inputs and outputs use decimals, not percentage points.
    """
    covariance = covariance_matrix(sleeves, correlations)
    if not math.isfinite(objective) or not 0 <= reserve_minimum <= 1:
        raise ValueError("Objective must be finite; reserve minimum must be in [0, 1].")
    eligible = RESERVE_ELIGIBLE if reserve_eligible is None else set(reserve_eligible)
    if not eligible <= set(sleeves):
        raise ValueError("Reserve assets must belong to the universe.")
    minimum_weights = {} if minimum_weights is None else minimum_weights
    maximum_weights = {} if maximum_weights is None else maximum_weights
    if not (set(minimum_weights) | set(maximum_weights)) <= set(sleeves):
        raise ValueError("Weight limits must refer to assets in the universe.")
    for name in sleeves:
        low = minimum_weights.get(name, 0)
        high = maximum_weights.get(name, 1)
        if not (math.isfinite(low) and math.isfinite(high) and 0 <= low <= high <= 1):
            raise ValueError("Each asset needs 0 <= minimum <= maximum <= 1.")

    def allocations(remaining, count):
        if count == 1:
            yield [remaining / 20]
        else:
            for units in range(remaining + 1):
                for tail in allocations(remaining - units, count - 1):
                    yield [units / 20] + tail

    best = None
    for weights in allocations(20, len(sleeves)):
        if any(w + 1e-12 < minimum_weights.get(name, 0)
               or w - 1e-12 > maximum_weights.get(name, 1)
               for name, w in zip(sleeves, weights)):
            continue
        result_return = expected_return(weights, sleeves)
        reserve = sum(w for name, w in zip(sleeves, weights) if name in eligible)
        if result_return + 1e-12 < objective or reserve + 1e-12 < reserve_minimum:
            continue
        volatility = portfolio_volatility(weights, covariance)
        if best is None or volatility < best["volatility"] - 1e-12:
            best = {"weights": weights, "return": result_return,
                    "volatility": volatility, "reserve": reserve}
    return best


def estimate_from_csv(source, last_36=False):
    """Historical arithmetic return estimate, sample risk, pairwise correlations.

    Require a complete, positive monthly panel; never fill missing prices.
    Last 36 means 36 monthly returns (requiring 37 prices).
    """
    import pandas as pd
    import numpy as np

    frame = pd.read_csv(source)
    if not 4 <= len(frame.columns) <= 7 or frame.columns.duplicated().any():
        raise ValueError("CSV must have date first and three to six unique ticker columns.")
    dates = pd.to_datetime(frame.iloc[:, 0], errors="raise")
    months = dates.dt.to_period("M")
    if dates.isna().any() or months.duplicated().any() or not dates.is_monotonic_increasing:
        raise ValueError("Dates must be valid, oldest first, with one price per month.")
    if len(months) < 37 or any(b.ordinal - a.ordinal != 1 for a, b in zip(months, months[1:])):
        raise ValueError("Supply at least 37 consecutive monthly prices; five years is required for submission.")
    prices = frame.iloc[:, 1:].apply(pd.to_numeric, errors="raise")
    if not np.isfinite(prices.to_numpy()).all() or (prices <= 0).any().any():
        raise ValueError("Every price must be finite and positive; no blanks.")
    returns = prices.pct_change(fill_method=None).iloc[1:]
    if last_36:
        returns = returns.tail(36)
    means = returns.mean() * 12
    vols = returns.std(ddof=1) * math.sqrt(12)
    sleeves = {name: (float(means[name]), float(vols[name])) for name in prices}
    correlations = returns.corr().to_numpy().tolist()
    validate_inputs(sleeves, correlations)
    return sleeves, correlations


def main():
    try:
        covariance = covariance_matrix(SLEEVES, CORRELATIONS)
        print(f"Objective: {OBJECTIVE_RETURN:.2%} (CPI estimate {CPI_ESTIMATE:.1%} + 4%)")
        print("Weights: " + " / ".join(SLEEVES))
        for name, weights in baseline_portfolios(SLEEVES).items():
            result = evaluate_portfolio(weights, SLEEVES, covariance, OBJECTIVE_RETURN)
            print(f"\n{name}: " + " / ".join(f"{w * 100:.1f}" for w in weights))
            print(f"Return {result['return']:.2%} | Volatility {result['volatility']:.2%} | "
                  f"Reserve-eligible {result['reserve']:.1%} | "
                  f"Meets objective: {'yes' if result['meets_objective'] else 'no'}")
    except ValueError as error:
        raise SystemExit(f"Cannot run portfolio engine: {error}")


if __name__ == "__main__":
    main()
