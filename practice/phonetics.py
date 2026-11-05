"""American English IPA for a word, built from the CMU Pronouncing Dictionary."""
import re
from functools import lru_cache

import cmudict

_CMU = None

VOWELS = {
    'AA': 'ɑ', 'AE': 'æ', 'AH': 'ʌ', 'AO': 'ɔ', 'AW': 'aʊ', 'AY': 'aɪ', 'EH': 'ɛ',
    'ER': 'ɝ', 'EY': 'eɪ', 'IH': 'ɪ', 'IY': 'i', 'OW': 'oʊ', 'OY': 'ɔɪ', 'UH': 'ʊ', 'UW': 'u',
}
CONSONANTS = {
    'B': 'b', 'CH': 'tʃ', 'D': 'd', 'DH': 'ð', 'F': 'f', 'G': 'ɡ', 'HH': 'h', 'JH': 'dʒ',
    'K': 'k', 'L': 'l', 'M': 'm', 'N': 'n', 'NG': 'ŋ', 'P': 'p', 'R': 'ɹ', 'S': 's',
    'SH': 'ʃ', 'T': 't', 'TH': 'θ', 'V': 'v', 'W': 'w', 'Y': 'j', 'Z': 'z', 'ZH': 'ʒ',
}


def _vowel(base, stress):
    if base == 'AH' and stress == '0':
        return 'ə'
    if base == 'ER' and stress == '0':
        return 'ɚ'
    return VOWELS[base]


def _to_ipa(phones):
    parts = []   # (kind, ipa, stress)
    for p in phones:
        base, stress = re.match(r'([A-Z]+)(\d?)', p).groups()
        if base in VOWELS:
            parts.append(('v', _vowel(base, stress), stress))
        else:
            parts.append(('c', CONSONANTS[base], ''))
    out = []
    for i, (kind, ipa, stress) in enumerate(parts):
        if kind == 'v' and stress in ('1', '2'):
            # put the stress mark before the syllable onset (at most two consonants back)
            j = len(out)
            back = 0
            while j > 0 and back < 2 and parts[i - back - 1][0] == 'c' and i - back - 1 >= 0:
                back += 1
                j -= 1
            out.insert(j, 'ˈ' if stress == '1' else 'ˌ')
        out.append(ipa)
    return ''.join(out)


@lru_cache(maxsize=2048)
def ipa_for(word):
    """'/wɝkt/'-style string for `word`, or '' if it isn't in the dictionary."""
    global _CMU
    if _CMU is None:
        _CMU = cmudict.dict()
    w = re.sub(r"[^a-z']", '', word.lower())
    prons = _CMU.get(w)
    return f'/{_to_ipa(prons[0])}/' if prons else ''
