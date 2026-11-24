"""Reproduce the FIN 439 allocation decision from the frozen Lab 15 snapshot."""
from pathlib import Path

import pandas as pd

import portfolio

PRICES = Path(__file__).with_name('prices.csv')
TICKERS = ('VOO', 'QQQ', 'VB', 'EEM')
AS_OF = '2026-10-22'
OBJECTIVE = .07
VOO_MIN = .40
EEM_MAX = .30
VB_MAX = .30
STOP_SHIFT = .15


def run(last_36=False, cost_bps=0, eem_max=EEM_MAX, voo_haircut=0):
    sleeves, corr = portfolio.estimate_from_csv(PRICES, last_36)
    if tuple(sleeves) != TICKERS:
        raise ValueError('Unexpected asset order in the saved prices.')
    cost = cost_bps / 10_000
    net = {ticker: (gross - cost, vol) for ticker, (gross, vol) in sleeves.items()}
    voo_return, voo_vol = net['VOO']
    net['VOO'] = (voo_return - voo_haircut, voo_vol)
    cov = portfolio.covariance_matrix(net, corr)
    candidates = portfolio.baseline_portfolios(net)
    candidates['Benchmark (VOO)'] = [1, 0, 0, 0]
    del candidates['Benchmark']  # The shared engine's benchmark belongs to Meridian.
    mix = portfolio.search_mix(net, corr, OBJECTIVE, 0, set(),
                               {'VOO': VOO_MIN}, {'VB': VB_MAX, 'EEM': eem_max})
    candidates['Constrained'] = mix['weights'] if mix else None
    rows = {}
    for name, weights in candidates.items():
        if weights is None:
            rows[name] = {'verdict': 'FAIL: no feasible mix'}
            continue
        metrics = portfolio.evaluate_portfolio(weights, net, cov, OBJECTIVE)
        checks = [
            (weights[0] < VOO_MIN - 1e-12, 'VOO below floor'),
            (weights[2] > VB_MAX + 1e-12, 'VB above cap'),
            (weights[3] > eem_max + 1e-12, 'EEM above cap'),
            (metrics['return'] < OBJECTIVE - 1e-12, 'net estimate below 7%'),
        ]
        failures = [label for failed, label in checks if failed]
        rows[name] = {**metrics, 'weights': weights,
                      'verdict': 'FAIL: ' + ', '.join(failures) if failures else 'PASS'}
    return rows


def shift(reference, candidate):
    if 'weights' not in candidate:
        return None
    return max(abs(a - b) for a, b in zip(reference['weights'], candidate['weights']))


def decision(change):
    return 'Reject the process under this stress' if change is None or change >= STOP_SHIFT - 1e-12 else 'Pilot on paper'


def signal():
    """Compute VOO momentum only after both prices were available in this saved extract."""
    prices = pd.read_csv(PRICES, parse_dates=['date']).set_index('date')
    cutoff = (pd.Timestamp(AS_OF).to_period('M') - 2).end_time
    observations = prices.loc[:cutoff, 'VOO'].tail(2)
    return observations.index[0].date(), observations.index[1].date(), observations.iloc[-1] / observations.iloc[0] - 1


def stresses():
    return {
        'VOO return estimate down 1 pp': run(voo_haircut=.01)['Constrained'],
        '36-month window': run(last_36=True)['Constrained'],
        '50 bp annual cost': run(cost_bps=50)['Constrained'],
        'EEM cap at 20%': run(eem_max=.20)['Constrained'],
    }


def visible_output():
    baseline = run()
    reference = baseline['Constrained']
    scenarios = stresses()
    worst = max((shift(reference, row) for row in scenarios.values()),
                key=lambda value: float('inf') if value is None else value)
    start, end, momentum = signal()
    lines = [
        '# Executed output', '',
        f'**Decision as of {AS_OF}** — {decision(worst)} with 0% live capital. Pause if '
        'any stress yields no feasible mix or moves any sleeve by at least 15 percentage points.', '',
        'Frozen prices: September 2021–September 2026. Base inputs: 60 monthly returns, '
        '0 bp annual cost, 7% net hurdle, 40% VOO floor, 30% VB cap, 30% EEM cap.', '',
        f'Lagged VOO signal: {momentum:+.2%} ({start} to {end}); available in the saved '
        f'extract on {AS_OF}. Diagnostic only.', '',
        '| Portfolio | VOO / QQQ / VB / EEM | Net return estimate | Estimated volatility | Mandate |',
        '|---|---|---:|---:|---|',
    ]
    for label, row in baseline.items():
        weights = ' / '.join(f'{w:.2%}' for w in row['weights'])
        lines.append(f"| {label} | {weights} | {row['return']:.2%} | {row['volatility']:.2%} | {row['verdict']} |")
    lines += ['', '| One-at-a-time stress | VOO / QQQ / VB / EEM | Net return estimate | Estimated volatility | Max shift (pp) | Decision |',
              '|---|---|---:|---:|---:|---|']
    for label, row in scenarios.items():
        change = shift(reference, row)
        if change is None:
            lines.append(f'| {label} | Infeasible | — | — | — | {decision(change)} |')
            continue
        weights = ' / '.join(f'{w:.0%}' for w in row['weights'])
        lines.append(f"| {label} | {weights} | {row['return']:.2%} | {row['volatility']:.2%} | {change * 100:.2f} | {decision(change)} |")
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    print(visible_output(), end='')
