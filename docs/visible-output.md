# Capstone executed output

October 16, 2026 ADP snapshot. Base value: $178.24 per share. Downside value: $157.12 per share. Paper diligence ceiling: $142.60. At the $288.90 reference price, ADP stays outside the paper pilot. Direct ADP paper and live weights are 0%.

## ETF pilot results

**Decision as of 2026-10-22** — Pilot on paper with 0% live capital. Pause if any stress yields no feasible mix or moves any sleeve by at least 15 percentage points.

Frozen prices: September 2021–September 2026. Base inputs: 60 monthly returns, 0 bp annual cost, 7% net hurdle, 40% VOO floor, 30% VB cap, 30% EEM cap.

Lagged VOO signal: +2.66% (2026-07-31 to 2026-08-31); available in the saved extract on 2026-10-22. Diagnostic only.

| Portfolio | VOO / QQQ / VB / EEM | Net return estimate | Estimated volatility | Mandate |
|---|---|---:|---:|---|
| Equal weight | 25.00% / 25.00% / 25.00% / 25.00% | 12.40% | 16.36% | FAIL: VOO below floor |
| Inverse volatility | 28.91% / 21.71% / 23.76% / 25.62% | 12.34% | 16.20% | FAIL: VOO below floor |
| Benchmark (VOO) | 100.00% / 0.00% / 0.00% / 0.00% | 14.18% | 15.67% | PASS |
| Constrained | 70.00% / 0.00% / 0.00% / 30.00% | 12.78% | 14.99% | PASS |

| One-at-a-time stress | VOO / QQQ / VB / EEM | Net return estimate | Estimated volatility | Max shift (pp) | Decision |
|---|---|---:|---:|---:|---|
| VOO return estimate down 1 pp | 70% / 0% / 0% / 30% | 12.08% | 14.99% | 0.00 | Pilot on paper |
| 36-month window | 80% / 0% / 0% / 20% | 21.70% | 12.17% | 10.00 | Pilot on paper |
| 50 bp annual cost | 70% / 0% / 0% / 30% | 12.28% | 14.99% | 0.00 | Pilot on paper |
| EEM cap at 20% | 80% / 0% / 0% / 20% | 13.25% | 15.09% | 10.00 | Pilot on paper |
