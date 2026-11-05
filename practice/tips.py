"""Pronunciation recommendations for words the learner got wrong or missed."""
import re

# word -> (respelling, tip). CAPITALS mark the stressed syllable.
WORD_TIPS = {
    'comfortable': ('KUMF-ter-bul', 'Three syllables, not four: the "or" nearly disappears.'),
    'schedule': ('SKED-jool', 'American English starts with "sk", and the "d" sounds like "j".'),
    'thorough': ('THUR-oh', 'Ends in "oh". The "ough" is not "uff" or "ow".'),
    'particularly': ('per-TIK-yuh-ler-lee', 'Stress the second syllable. Keep every syllable light and even.'),
    'february': ('FEB-yoo-air-ee', 'Say the first "r" too: Feb-ru-ary, not Feb-u-ary.'),
    'sixth': ('siksth', 'Glide k-s-th together. Touch your tongue to your teeth at the very end.'),
    'world': ('wurld', 'The "r" and "l" are two separate sounds. Curl the tongue for "r", then tap up for "l".'),
    'clothes': ('klohz', 'Say it like "close": the "th" is silent in everyday speech.'),
    'months': ('munths', 'Teeth on tongue for "th", then finish with "s".'),
    'probably': ('PRAH-blee', 'Fast speech drops the middle: PROB-lee.'),
    'vegetable': ('VEJ-tuh-bul', 'Three syllables. The "e" after "g" is skipped.'),
    'interesting': ('IN-tris-ting', 'Three beats, stress on the first. Do not say "in-ter-EST-ing".'),
    'especially': ('es-PESH-uh-lee', 'The "ci" makes a "sh" sound.'),
    'enough': ('ih-NUFF', 'Stress the second syllable. "ough" is "uff".'),
    'through': ('throo', 'Tongue between the teeth for "th", then a long "oo". No "gh" sound.'),
    'though': ('thoh', 'Voiced "th" (buzz your voice), then "oh".'),
    'thought': ('thawt', 'Voiceless "th" (air only), "aw" vowel, hard "t" at the end.'),
    'might': ('mite', 'The "gh" is silent.'),
    'right': ('rite', 'The "gh" is silent. Start with the American "r".'),
    'would': ('wud', 'The "l" is silent.'),
    'could': ('kud', 'The "l" is silent.'),
    'should': ('shud', 'The "l" is silent.'),
    'listen': ('LIS-un', 'The "t" is silent.'),
    'often': ('AW-fun', 'The "t" is usually silent.'),
    'wednesday': ('WENZ-day', 'The first "d" is silent.'),
    'receipt': ('rih-SEET', 'The "p" is silent.'),
    'chocolate': ('CHAWK-lit', 'Two or three syllables at most, never "choc-o-late".'),
    'different': ('DIF-rent', 'Two syllables is natural: DIF-rent.'),
    'beautiful': ('BYOO-tuh-ful', 'Start with "byoo", not "boo".'),
    'library': ('LY-brer-ee', 'Say the first "r": li-BRAR-y, not li-BERRY.'),
    'recipe': ('RES-uh-pee', 'Three syllables. The final "e" is pronounced "ee".'),
    'island': ('EYE-lund', 'The "s" is silent.'),
    'police': ('puh-LEESE', 'Stress the second syllable.'),
    'develop': ('dih-VEL-up', 'Stress the second syllable.'),
    'comfort': ('KUM-fert', 'First syllable sounds like "come".'),
    'pronunciation': ('pruh-nun-see-AY-shun', 'Not "pro-NOUN": the first vowel is "uh".'),
    'rural': ('ROOR-ul', 'Two quick "r" sounds with "oo" between.'),
    'squirrel': ('SKWUR-ul', 'Hard for many speakers: say "skwur", then a quick "ul".'),
    'anxious': ('ANK-shus', 'The "x" is "k-sh".'),
    'suggest': ('sug-JEST', 'Both "g"s are different: hard first, "j" second (American: sug-JEST).'),
    'receive': ('rih-SEEV', 'Stress the second syllable.'),
    'clothing': ('KLOH-thing', 'Voiced "th" in the middle.'),
    'breathe': ('breeth', 'Final "th" is voiced: buzz your voice with your tongue between your teeth.'),
    'walk': ('wawk', 'The "l" is silent. Rhymes with "talk".'),
    'talk': ('tawk', 'The "l" is silent.'),
    'answer': ('AN-ser', 'The "w" is silent.'),
    'knew': ('noo', 'The "k" is silent.'),
    'know': ('noh', 'The "k" is silent.'),
}

# -ed words whose ending is NOT what the spelling-based rule guesses
ED_SOUND = {
    'closed': 'd', 'used': 'd', 'raised': 'd', 'surprised': 'd', 'promised': 'd',
    'confused': 'd', 'refused': 'd', 'pleased': 'd', 'based': 't', 'laughed': 't',
    'passed': 't', 'missed': 't', 'asked': 't', 'finished': 't',
}
VOICELESS_END = ('p', 'k', 'f', 's', 'x', 'ch', 'sh', 'c', 'ss')


def ed_sound(word):
    """Return ('t'|'d'|'id', respelling) for a regular past-tense word, else None."""
    if not word.endswith('ed') or len(word) < 4:
        return None
    stem = word[:-2]
    if word in ED_SOUND:
        kind = ED_SOUND[word]
    elif stem.endswith(('t', 'd')):
        kind = 'id'
    elif stem.endswith(VOICELESS_END):
        kind = 't'
    else:
        kind = 'd'
    if kind == 'id':
        return kind, f'{stem}-id'
    return kind, stem + kind


def tip_for(target, heard=''):
    """Recommendation for one target word. `target` may include punctuation."""
    word = re.sub(r"[^a-z']", '', target.lower())
    heard = re.sub(r"[^a-z']", '', heard.lower())
    ed = ed_sound(word)

    if ed:
        kind, spelled = ed
        how = {
            't': f'The "-ed" is just a quick T sound, no extra syllable. Say "{spelled}".',
            'd': f'The "-ed" is just a D sound, no extra syllable. Say "{spelled}".',
            'id': f'After T or D, "-ed" adds a whole new syllable: "{spelled}" ("id").',
        }[kind]
        if heard and word.startswith(heard) and len(heard) >= len(word) - 3:
            return f'You dropped the ending. {how}'
        if not heard:
            return f'The ending is easy to swallow. {how}'
        return how
    if word in WORD_TIPS:
        spelled, tip = WORD_TIPS[word]
        return f'Say "{spelled}". {tip}'
    if heard and word.startswith(heard) and len(word) - len(heard) <= 2:
        return f'You stopped short. Finish the last sound of "{word}" clearly.'
    if 'th' in word:
        return 'Put the tip of your tongue lightly between your teeth for "th", then release air.'
    if word.startswith('wh') or word.startswith('w'):
        return 'Round your lips for "w". For "v", the top teeth touch the bottom lip.'
    if re.search(r'[aeiou]r', word) or word.startswith('r'):
        return 'American "r": curl the tongue back without touching the roof of your mouth.'
    if word.endswith(('s', 'es')) and heard and heard == word.rstrip('es'):
        return 'Add the final "s" sound; it marks plural or present tense.'
    return 'Say it slowly, one syllable at a time, then speed up. Tap the speaker to hear it.'
