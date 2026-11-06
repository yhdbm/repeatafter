import asyncio
import hashlib
import json
import random
import re

import edge_tts
from django.conf import settings
from django.db.models import Avg
from django.http import FileResponse, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .models import Attempt, SavedWord, Sentence
from .phonetics import ipa_for
from .scoring import score_attempt


@ensure_csrf_cookie
def index(request):
    return render(request, 'practice/index.html')


@require_GET
def next_sentence(request):
    """Random sentence; sentences you score poorly on come up more often."""
    exclude = request.GET.get('exclude')
    qs = Sentence.objects.exclude(pk=exclude) if exclude and exclude.isdigit() else Sentence.objects.all()
    pool = list(qs)
    if not pool:
        return JsonResponse({'error': 'No sentences. Run: python manage.py seed_sentences'}, status=404)
    avg = {r['sentence']: r['a'] for r in
           Attempt.objects.values('sentence').annotate(a=Avg('score'))}
    # unseen -> weight 2, otherwise weight grows as the average score drops
    weights = [2.0 if s.pk not in avg else 0.5 + (100 - avg[s.pk]) / 50 for s in pool]
    s = random.choices(pool, weights=weights, k=1)[0]
    return JsonResponse({'id': s.pk, 'text': s.text})


@require_POST
def score(request):
    try:
        data = json.loads(request.body)
        sentence = Sentence.objects.get(pk=data['id'])
    except (ValueError, KeyError, TypeError, Sentence.DoesNotExist):
        return JsonResponse({'error': 'bad request'}, status=400)
    heard = str(data.get('transcript', ''))[:500]
    pct, words, extra = score_attempt(sentence.text, heard)
    Attempt.objects.create(
        sentence=sentence, transcript=heard, score=pct,
        missed_words=[w['word'] for w in words if w['status'] in ('wrong', 'missed')],
    )
    return JsonResponse({'score': pct, 'words': words, 'extra': extra, 'heard': heard})


TTS_VOICES = {  # neural US male voices
    'andrew': 'en-US-AndrewNeural',
    'guy': 'en-US-GuyNeural',
    'christopher': 'en-US-ChristopherNeural',
    'eric': 'en-US-EricNeural',
    'roger': 'en-US-RogerNeural',
}
TTS_DIR = settings.TTS_DIR


@require_GET
def tts(request):
    """Natural-sounding speech (Microsoft neural voices via edge-tts), cached on disk."""
    text = request.GET.get('text', '').strip()
    if not text or len(text) > 250:
        return HttpResponseBadRequest('text required (max 250 chars)')
    voice_key = request.GET.get('voice', 'andrew')
    voice = TTS_VOICES.get(voice_key, TTS_VOICES['andrew'])
    rate = '-35%' if request.GET.get('slow') == '1' else '-5%'
    name = hashlib.sha1(f'{voice}|{rate}|{text}'.encode()).hexdigest() + '.mp3'
    path = TTS_DIR / name
    if not path.exists():
        TTS_DIR.mkdir(exist_ok=True)
        tmp = path.with_suffix('.part')
        try:
            asyncio.run(edge_tts.Communicate(text, voice, rate=rate).save(str(tmp)))
            tmp.replace(path)
        except Exception:
            tmp.unlink(missing_ok=True)
            return HttpResponse('tts unavailable', status=503)
    resp = FileResponse(open(path, 'rb'), content_type='audio/mpeg')
    resp['Cache-Control'] = 'public, max-age=86400'
    return resp


@require_GET
def ipa(request):
    """IPA for a single word (used by the tap-a-word popup)."""
    word = _clean_word(request.GET.get('word', ''))
    if not word:
        return JsonResponse({'error': 'bad request'}, status=400)
    return JsonResponse({'word': word, 'ipa': ipa_for(word)})


@require_GET
def stats(request):
    qs = Attempt.objects.all()
    return JsonResponse({
        'attempts': qs.count(),
        'average': round(qs.aggregate(a=Avg('score'))['a'] or 0),
    })


def _clean_word(w):
    return re.sub(r"[^a-z']", '', str(w).lower())[:60]


@require_http_methods(['GET', 'POST', 'DELETE'])
def saved(request):
    """GET list, POST {word, tip} to save, DELETE {word} to remove."""
    if request.method == 'GET':
        return JsonResponse({'words': [{**r, 'ipa': ipa_for(r['word'])} for r in SavedWord.objects.values('word', 'tip')]})
    try:
        data = json.loads(request.body)
        word = _clean_word(data['word'])
    except (ValueError, KeyError, TypeError):
        return JsonResponse({'error': 'bad request'}, status=400)
    if not word:
        return JsonResponse({'error': 'bad request'}, status=400)
    if request.method == 'POST':
        SavedWord.objects.update_or_create(word=word, defaults={'tip': str(data.get('tip', ''))[:400]})
    else:
        SavedWord.objects.filter(word=word).delete()
    return JsonResponse({'ok': True})
