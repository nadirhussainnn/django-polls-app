from django.contrib import admin
import nested_admin
from .models import Poll, Question, Choice


class ChoiceInline(nested_admin.NestedTabularInline):
    model = Choice
    extra = 2
    min_num = 2
    validate_min = True
    max_num = 3
    validate_max = False


class QuestionInline(nested_admin.NestedStackedInline):
    model = Question
    extra = 1
    min_num = 1
    max_num = 1
    validate_min = True
    validate_max = True
    inlines = [ChoiceInline]
    

class PollAdmin(nested_admin.NestedModelAdmin):
    fieldsets = [
        (None, {'fields': ['title']}),
        ('Date Information', {'fields': ['created_at', 'expiry'], 'classes': ['collapse']}),
    ]
    
    list_display = ('title', 'created_at', 'expiry')
    list_filter = ['created_at', 'expiry']
    search_fields = ['title']

    inlines = [QuestionInline]


admin.site.register(Poll, PollAdmin)