from django.db import models


class Sentence(models.Model):
    text = models.CharField(max_length=250, unique=True)

    def __str__(self):
        return self.text


class Attempt(models.Model):
    sentence = models.ForeignKey(Sentence, on_delete=models.CASCADE, related_name='attempts')
    transcript = models.CharField(max_length=500, blank=True)
    score = models.PositiveSmallIntegerField()
    missed_words = models.JSONField(default=list)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'{self.score}% - {self.sentence}'


class SavedWord(models.Model):
    """A word (and its pronunciation tip) the learner chose to keep for review."""
    word = models.CharField(max_length=60, unique=True)
    tip = models.CharField(max_length=400)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.word
