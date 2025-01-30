from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Article, UserRecording, Feedback

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'edited_at', 'is_published')
    list_filter = ('is_published', 'author', 'created_at')
    search_fields = ('title', 'content')

    # Mark fields as read-only to avoid trying to edit them
    readonly_fields = ('created_at', 'edited_at')

    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'image', 'author', 'is_published')
        }),
        (_('Date Information'), {
            'fields': ('created_at', 'edited_at'),
            'classes': ('collapse',),
        }),
    )

class UserRecordingAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'pronunciation_score', 'submitted_at')
    list_filter = ('user', 'article', 'submitted_at')
    search_fields = ('user__username', 'article__title')
    readonly_fields = ('manual_feedback_link', 'transcript', 'pronunciation_score', 'feedback','highlighted_transcript','highlighted_article')

    # Add a link to the feedback creation page
    def manual_feedback_link(self, obj):
        try:
            # Check if feedback exists via the reverse relationship
            feedback = obj.feedback_recording  # Access the related Feedback object
            url = reverse('admin:articles_feedback_change', args=[feedback.id])
            link = format_html('<a href="{}">Edit Feedback</a>', url)
        except Feedback.DoesNotExist:
            # If feedback doesn't exist, link to the add feedback page
            url = reverse('admin:articles_feedback_add') + f'?recording={obj.id}'
            link = format_html('<a href="{}">Add Feedback</a>', url)

        # Add help text below the link
        help_text = format_html('<div style="color: gray; font-size: small;"><i>Click here to add or edit feedback for this recording.</i></div>')

        # Return the link with the help text
        return format_html('{}<br>{}', link, help_text)

    manual_feedback_link.short_description = "Manual Feedback"


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('recording', 'evaluator', 'pronunciation_score', 'intonation_score', 'fluency_score', 'overall_score', 'created_at')
    list_filter = ('evaluator', 'created_at', 'recording__article')
    search_fields = ('recording__user__username', 'recording__article__title')
    readonly_fields = ('overall_score',)  # Read-only fields

    # Prepopulate the recording field when creating feedback from the link
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'recording' and 'recording' in request.GET:
            kwargs['initial'] = request.GET.get('recording')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # Saving feedback with validation (if any)
    def save_model(self, request, obj, form, change):
        obj.save()  # Call to save, which can handle validation for fields
        super().save_model(request, obj, form, change)

admin.site.register(Article, ArticleAdmin)
admin.site.register(UserRecording, UserRecordingAdmin)
admin.site.register(Feedback, FeedbackAdmin)
