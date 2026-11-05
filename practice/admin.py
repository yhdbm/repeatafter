from django.contrib import admin

from .models import Attempt, SavedWord, Sentence

admin.site.register(Sentence)
admin.site.register(SavedWord)


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ('sentence', 'score', 'created')
