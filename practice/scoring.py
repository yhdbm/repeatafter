"""Word-level comparison of a target sentence against what the speech recognizer heard."""
import re
from difflib import SequenceMatcher

from .phonetics import ipa_for
from .tips import tip_for

CLOSE = 0.75  # similarity at which a word counts as "close" (accent/recognizer noise)


def tokenize(text):
    text = text.lower().replace('’', "'")
    return re.findall(r"[a-z0-9]+(?:'[a-z]+)?", text)


def _similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def score_attempt(target, heard):
    """Return (score 0-100, per-word results, extra words).

    Each result: {word, status: ok|close|wrong|missed, heard}.
    Display words keep the target's original punctuation/case.
    """
    display = target.split()
    target_tokens = [tokenize(w) for w in display]
    # one comparable token per display word (a word like "don't" stays one token)
    keys = [''.join(t) for t in target_tokens]
    heard_words = [''.join(tokenize(w)) for w in heard.split()]
    heard_words = [w for w in heard_words if w]

    results = [{'word': w, 'status': 'missed', 'heard': ''} for w in display]
    extra = []

    sm = SequenceMatcher(None, keys, heard_words, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            for k in range(i2 - i1):
                results[i1 + k].update(status='ok', heard=heard_words[j1 + k])
        elif tag == 'replace':
            # pair up words inside the block by best similarity, in order
            h = list(range(j1, j2))
            for i in range(i1, i2):
                if not h:
                    break
                best = max(h, key=lambda j: _similar(keys[i], heard_words[j]))
                ratio = _similar(keys[i], heard_words[best])
                if ratio >= 0.99:
                    status = 'ok'
                elif ratio >= CLOSE:
                    status = 'close'
                elif ratio >= 0.4 or (i2 - i1) == (j2 - j1):
                    status = 'wrong'
                else:
                    continue
                results[i].update(status=status, heard=heard_words[best])
                h.remove(best)
            extra.extend(heard_words[j] for j in h)
        elif tag == 'insert':
            extra.extend(heard_words[j1:j2])
        # 'delete' stays "missed"

    for r, key in zip(results, keys):
        # "worked" heard as "work": a swallowed ending is a real error, not a near-match
        if r['status'] == 'close' and key.endswith('ed') and key.startswith(r['heard']) and r['heard'] != key:
            r['status'] = 'wrong'
        if r['status'] in ('wrong', 'missed', 'close'):
            r['tip'] = tip_for(r['word'], r['heard'])
            r['ipa'] = ipa_for(r['word'])

    points = {'ok': 1.0, 'close': 0.75, 'wrong': 0.0, 'missed': 0.0}
    total = len(results) or 1
    gained = sum(points[r['status']] for r in results)
    gained -= min(0.1 * len(extra), 0.3 * total)  # light penalty for added words
    return max(0, round(100 * gained / total)), results, extra
