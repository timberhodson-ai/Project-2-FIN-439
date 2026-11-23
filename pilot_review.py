"""Guarded evidence review for ADP paper-position diligence."""
import json
import os
from urllib.request import Request, urlopen


EVIDENCE = {
    'terminal': 'About three quarters of ADP enterprise value comes from terminal value.',
    'shares': 'The DCF uses historical diluted shares as a proxy for the valuation date.',
    'risk': 'The ETF optimizer estimates risk for VOO, QQQ, VB and EEM only.',
}
PROMPT = (
    'Review the evidence below for a committee considering whether to start ADP paper-position '
    'diligence. Identify the single most material unresolved issue and propose a concrete check '
    'that could resolve it. Explain the link between the valuation evidence and the investment '
    'workflow. Use only these facts. Do not recommend a weight or claim that a check was run. '
    'Return JSON only with exactly two keys: evidence_id (one listed ID) and check (one '
    'actionable sentence under 400 characters). Evidence: ' + json.dumps(EVIDENCE)
)


def request_review():
    key = os.environ.get('GENAI_API_KEY')
    model = os.environ.get('GENAI_MODEL')
    if not key or not model:
        raise ValueError('Set GENAI_API_KEY and GENAI_MODEL before launching Streamlit.')
    request = Request(
        'https://genai.rcac.purdue.edu/api/chat/completions',
        data=json.dumps({'model': model, 'messages': [{'role': 'user', 'content': PROMPT}],
                         'stream': False}).encode('utf-8'),
        headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'},
        method='POST',
    )
    with urlopen(request, timeout=45) as response:
        return json.load(response)['choices'][0]['message']['content']


def validate_review(raw):
    review = json.loads(raw)
    if not isinstance(review, dict) or set(review) != {'evidence_id', 'check'}:
        raise ValueError('Expected exactly evidence_id and check.')
    evidence_id, check = review['evidence_id'], review['check']
    if not isinstance(evidence_id, str) or evidence_id not in EVIDENCE:
        raise ValueError('The evidence ID must exist in the supplied evidence.')
    if not isinstance(check, str) or not 1 <= len(check.strip()) <= 400:
        raise ValueError('Provide a check of 1 to 400 characters.')
    return review
