"""Streamlit interface for the frozen Project 2 analysis."""
from hashlib import sha256
from datetime import date
import json
import math
import os
from pathlib import Path

import streamlit as st

from analysis import AS_OF, OBJECTIVE, STOP_SHIFT, TICKERS, decision, run, shift, signal, stresses
from pilot_review import EVIDENCE, PROMPT, request_review, validate_review

st.set_page_config(page_title='ETF allocation readiness', layout='wide')
st.title('Capstone paper-pilot dashboard')
st.caption(f'Saved decision snapshot: {AS_OF}. Education only. Investment advice is outside its scope.')
st.write('The mandate minimizes estimated annual volatility on a 5-point grid. The portfolio is fully '
         'invested and long-only, with a 7% net return hurdle, at least 40% VOO, and at most 30% VB. '
         'The baseline EEM cap is 30%. VOO is the proposed comparison benchmark.')

last_36 = st.sidebar.checkbox('Use only the last 36 monthly returns')
cost_bps = st.sidebar.number_input('Annual portfolio cost (basis points)', 0, 2000, 0, step=5)
eem_cap = st.sidebar.number_input('EEM weight cap (%)', 0, 100, 30, step=5)
haircut = st.sidebar.number_input('VOO return haircut (percentage points)', 0.0, 30.0, 0.0, step=.25)
reference = run()['Constrained']
rows = run(last_36, cost_bps, eem_cap / 100, haircut / 100)
scenarios = stresses()
stress_changes = [shift(reference, result) for result in scenarios.values()]
worst_change = None if None in stress_changes else max(stress_changes)
st.header(f'Committee recommendation: {decision(worst_change)}')
if decision(worst_change) == 'Pilot on paper':
    feasible_weights = [reference['weights'], *(result['weights'] for result in scenarios.values())]
    ranges = [f'{ticker} {min(weights):.0%} to {max(weights):.0%}'
              for ticker, weights in zip(TICKERS, zip(*feasible_weights)) if max(weights) > 0]
    st.write('Authorize a paper pilot with 0% live capital. Paper allocation across the base and '
             f'reference stresses: {", ".join(ranges)}.')
st.caption('Monitor feasibility, sleeve movement and realized costs. Stop if a stress is infeasible '
           'or moves any sleeve by at least 15 percentage points.')

st.subheader('ADP valuation and paper-pilot eligibility')
adp_eligible = False
adp_price = st.sidebar.number_input('ADP scenario price (USD/share)', min_value=0.01,
                                    value=288.90, step=1.0)
try:
    valuation = json.loads(Path(__file__).with_name('ADP_project_DCF.json').read_text(encoding='utf-8'))
    base_value = float(valuation['values']['base']['per_share'])
    downside_value = float(valuation['values']['downside']['per_share'])
    if not (math.isfinite(base_value) and 0 < downside_value <= base_value):
        raise ValueError('Invalid DCF case values')
except (OSError, KeyError, TypeError, ValueError):
    st.error('ADP valuation evidence is unavailable or invalid. Hold ADP out of the paper pilot.')
else:
    # Carry the earlier 20% base-case margin of safety into the investment screen.
    entry_ceiling = min(0.80 * base_value, downside_value)
    st.write(f'October 16 ADP valuation: ${base_value:,.2f} base and ${downside_value:,.2f} downside per share. '
             f'Paper-candidate ceiling: ${entry_ceiling:,.2f}.')
    if adp_price <= entry_ceiling:
        adp_eligible = True
        st.success('ADP clears the valuation screen. Complete the evidence review before advancing.')
    else:
        st.info('ADP fails the valuation screen. Keep the paper pilot ETF-only at this price.')
    st.caption('The price control starts at the October 16 reference close. The screen requires a 20% '
               'discount to base value and a price at or below downside value. ADP is outside the ETF '
               'optimizer and needs its own portfolio-risk test before any paper weight is assigned.')

with st.expander('AI evidence review for ADP diligence', expanded=adp_eligible):
    st.caption('The model proposes a diligence check. An analyst must verify the evidence and accept '
               'or correct the check before ADP can advance. The screen and ETF rules still apply.')
    route = st.radio('Review route', ('Purdue GenAI Studio API', 'Manual fallback after an API failure'))
    if route == 'Purdue GenAI Studio API':
        if st.button('Request evidence review'):
            st.session_state.pop('review_response', None)
            try:
                st.session_state['review_response'] = request_review()
            except (OSError, ValueError, KeyError, IndexError, TypeError):
                st.error('GenAI review unavailable. Check API access and model settings or use the documented fallback.')
        raw_review = st.session_state.get('review_response', '')
        if raw_review:
            st.code(raw_review, language='json')
    else:
        st.code(PROMPT, language=None)
        raw_review = st.text_area('Paste the exact model response')
    if raw_review:
        try:
            review = validate_review(raw_review)
        except (TypeError, ValueError):
            st.error('Review held: response must match the requested JSON fields and cite a supplied evidence ID.')
        else:
            st.write(EVIDENCE[review['evidence_id']])
            st.text(review['check'])
            with st.form(key='analyst_review_' + sha256(raw_review.encode()).hexdigest()):
                analyst_check = st.text_area('Verified or corrected check and your reason')
                reviewed = st.form_submit_button('Record analyst review')
            if reviewed and analyst_check.strip():
                st.write('Analyst record')
                st.text(analyst_check.strip())
                model = os.environ.get('GENAI_MODEL', '')
                st.download_button('Download review evidence', json.dumps({
                    'recorded_date': date.today().isoformat(), 'route': route,
                    'api_model': model if route == 'Purdue GenAI Studio API' else None,
                    'prompt': PROMPT, 'raw_response': raw_review,
                    'analyst_validation': analyst_check.strip(),
                }, indent=2), file_name='ai-review-evidence.json', mime='application/json')
                if adp_eligible and decision(worst_change) == 'Pilot on paper':
                    st.success('Advance ADP to paper-position risk testing. Paper and live ADP weights remain 0%.')
                else:
                    st.info('ADP remains on hold under the valuation or ETF reference stress rules.')

st.subheader('Portfolio comparison under selected inputs')
st.caption('Equal weight assigns 25% to each ETF. Inverse volatility gives more weight to ETFs '
           'with lower estimated volatility, in proportion to 1 / volatility.')
window = 36 if last_36 else 60
st.caption(f'{window} monthly returns · {cost_bps} bp annual cost · {eem_cap}% EEM cap · '
           f'{haircut:g} percentage point VOO return haircut')
table = []
for name, result in rows.items():
    row = {'Portfolio': name, 'Mandate': result['verdict']}
    if 'weights' in result:
        row.update({ticker: f'{weight:.2%}' for ticker, weight in zip(TICKERS, result['weights'])})
        row['Net return estimate'] = f"{result['return']:.2%}"
        row['Estimated volatility'] = f"{result['volatility']:.2%}"
    table.append(row)
st.dataframe(table, hide_index=True)

comparison = [
    {'Portfolio': name, 'Return': result['return'], 'Volatility': result['volatility'],
     'Verdict': result['verdict'], 'Status': result['verdict'].split(':', 1)[0]}
    for name, result in rows.items() if 'weights' in result
]
st.vega_lite_chart({
    'height': 270,
    'layer': [
        {'data': {'values': [{'Return': OBJECTIVE}]},
         'mark': {'type': 'rule', 'color': '#9a671a', 'strokeDash': [6, 4]},
         'encoding': {'y': {'field': 'Return', 'type': 'quantitative'}}},
        {'data': {'values': comparison},
         'mark': {'type': 'point', 'filled': True, 'size': 185},
         'encoding': {
             'x': {'field': 'Volatility', 'type': 'quantitative', 'title': 'Estimated annual volatility',
                   'axis': {'format': '.1%'}, 'scale': {'zero': False}},
             'y': {'field': 'Return', 'type': 'quantitative', 'title': 'Estimated net annual return',
                   'axis': {'format': '.1%'}, 'scale': {'zero': False}},
             'color': {'field': 'Status', 'type': 'nominal', 'title': 'Mandate',
                       'scale': {'domain': ['PASS', 'FAIL'], 'range': ['#11766e', '#b45337']}},
             'shape': {'field': 'Portfolio', 'type': 'nominal'},
             'tooltip': [{'field': 'Portfolio'}, {'field': 'Verdict'},
                         {'field': 'Volatility', 'type': 'quantitative', 'format': '.2%'},
                         {'field': 'Return', 'type': 'quantitative', 'format': '.2%'}],
         }},
    ],
})
st.caption('The dashed line marks the return hurdle. A portfolio can clear it and still fail a weight limit.')

change = shift(reference, rows['Constrained'])
if change is None:
    st.error('Selected inputs: no feasible allocation. Reject the process under this stress.')
elif decision(change) == 'Pilot on paper':
    st.success(f'Selected inputs: pilot on paper. Largest sleeve move: {change * 100:.2f} pp.')
else:
    st.error(f'Selected inputs: reject under this stress. Largest sleeve move: {change * 100:.2f} pp.')

st.subheader('Reference stress tests')
st.caption('Each test changes one input from the frozen base. Sidebar changes affect the comparison above.')
stress_table = []
for (name, result), movement in zip(scenarios.items(), stress_changes):
    weights = result.get('weights')
    stress_table.append({
        'Test': name,
        'VOO / QQQ / VB / EEM': ' / '.join(f'{weight:.0%}' for weight in weights) if weights is not None else 'Infeasible',
        'Net return': f"{result['return']:.2%}" if weights is not None else '—',
        'Volatility': f"{result['volatility']:.2%}" if weights is not None else '—',
        'Largest move': f'{movement * 100:.2f} pp' if movement is not None else '—',
        'Mandate': result['verdict'],
        'Decision': decision(movement),
    })
st.dataframe(stress_table, hide_index=True)

stop_pp = STOP_SHIFT * 100
movements = [*zip(scenarios, stress_changes), ('Selected inputs', change)]
st.vega_lite_chart({
    'height': 200,
    'layer': [
        {'data': {'values': [
            {'Scenario': name, 'Move': movement * 100, 'Decision': decision(movement)}
            for name, movement in movements if movement is not None
        ]},
         'mark': {'type': 'point', 'filled': True, 'size': 135},
         'encoding': {
             'x': {'field': 'Move', 'type': 'quantitative', 'title': 'Largest sleeve move (percentage points)',
                   'scale': {'domainMin': 0}},
             'y': {'field': 'Scenario', 'type': 'nominal', 'title': None, 'sort': [name for name, _ in movements]},
             'color': {'field': 'Decision', 'type': 'nominal', 'legend': None,
                       'scale': {'domain': [decision(0), decision(STOP_SHIFT)], 'range': ['#11766e', '#b45337']}},
             'tooltip': [{'field': 'Scenario'}, {'field': 'Move', 'type': 'quantitative', 'format': '.2f'},
                         {'field': 'Decision'}],
         }},
        {'data': {'values': [{'Move': stop_pp}]},
         'mark': {'type': 'rule', 'color': '#b45337', 'strokeDash': [6, 4]},
         'encoding': {'x': {'field': 'Move', 'type': 'quantitative'}}},
    ],
})
infeasible = [name for name, movement in movements if movement is None]
st.caption(f'The dashed line marks the {stop_pp:g}-point stop. Infeasibility also stops the pilot.')
if infeasible:
    st.warning(f'Stopped without a feasible allocation: {", ".join(infeasible)}.')

st.subheader('Point-in-time signal')
start, end, momentum = signal()
st.write(f'Lagged VOO momentum: {momentum:+.2%} ({start} to {end}). '
         f'Availability is verified as of the saved extract on {AS_OF}. The optimizer does not use this diagnostic.')
with st.expander('Signal data card'):
    data_card = (Path(__file__).parent / 'docs' / 'data-card.md').read_text(encoding='utf-8')
    st.markdown(data_card.replace('[Source metadata and hashes](../source-estimates.json)',
                                  'See `source-estimates.json` for source metadata and hashes.'))
