# Data card — lagged VOO monthly momentum

The bundled `prices.csv` contains 61 aligned month-end adjusted closes for VOO, QQQ, VB and EEM from September 2021 through September 2026. Each row represents the last trading day's close, labeled with its calendar month-end. Lab 15 saved the Yahoo Finance extracts on October 22, 2026. [Source metadata and hashes](../source-estimates.json)

`signal()` sets the availability boundary at October 22, 2026, the saved extract date. It excludes the September month-end from the **signal** under the one-full-calendar-month lag convention, so the newest eligible signal month is August. It divides the August VOO adjusted close by July's and subtracts one. The portfolio estimation window uses the September close, which was already in the extract when this snapshot was assembled.

The signal is available for the documented October 22 decision and is displayed as a timing diagnostic. It has no weight-setting role. The snapshot contains adjusted closes as downloaded on October 22. Earlier historical decision dates would require archived vintages to verify what was actually available then. The package makes no historical trading or performance claim from the signal.
