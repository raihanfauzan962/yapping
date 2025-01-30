from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class Article(models.Model):
    title = models.CharField(
        max_length=255, 
        verbose_name="Article Title", 
        help_text="Enter the title of the article."
    )
    content = models.TextField(
        verbose_name="Content", 
        help_text="Write the main content of the article."
    )
    image = models.ImageField(
        upload_to='articles/', 
        blank=True, 
        null=True, 
        verbose_name="Image",
        help_text="Upload an optional image for the article."
    )
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name="Author",
        help_text="The author of this article."
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Created At",
        help_text="The date and time when the article was created."
    )
    edited_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="Last Edited At",
        help_text="The date and time when the article was last edited."
    )
    is_published = models.BooleanField(
        default=False, 
        verbose_name="Published",
        help_text="Check this box to make the article visible to users."
    )

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class UserRecording(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name="User", 
        help_text="The user who uploaded the recording.",
        related_name="user_recordings"
    )
    article = models.ForeignKey(
        Article, 
        on_delete=models.CASCADE, 
        verbose_name="Article", 
        help_text="The article associated with this recording.",
        related_name="user_recordings" 
    )
    audio_file = models.FileField(
        upload_to='recordings/', 
        verbose_name="Audio File", 
        help_text="Upload the audio file for evaluation."
    )
    transcript = models.TextField(
        null=True,
        blank=True,
        verbose_name="Transcript",
        help_text="The text transcribed from the audio recording."
    )
    pronunciation_score = models.FloatField(
        null=True, 
        blank=True, 
        verbose_name="Pronunciation Score", 
        help_text="The calculated pronunciation score for the recording."
    )
    feedback = models.TextField(
        null=True, 
        blank=True, 
        verbose_name="Feedback", 
        help_text="The feedback provided for the recording."
    )
    highlighted_transcript = models.TextField(
        null=True,
        blank=True,
        verbose_name="Highlighted Transcript",
        help_text="The HTML content of the highlighted transcript."
    )
    highlighted_article = models.TextField(
        null=True,
        blank=True,
        verbose_name="Highlighted Article",
        help_text="The HTML content of the highlighted article."
    )
    submitted_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Submitted At", 
        help_text="The date and time when the recording was submitted."
    )

    def __str__(self):
        return f"Recording by {self.user} for {self.article}"


class Feedback(models.Model):
    recording = models.OneToOneField(
        'UserRecording',
        on_delete=models.CASCADE,
        related_name="feedback_recording",
        verbose_name="Recording",
        help_text="The recording associated with this feedback."
    )
    evaluator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='feedbacks',
        verbose_name="Evaluator",
        help_text="The evaluator providing this feedback."
    )
    pronunciation_score = models.FloatField(
        null=True, 
        blank=True, 
        verbose_name="Pronunciation Score", 
        help_text="Score for pronunciation (0-10)."
    )
    intonation_score = models.FloatField(
        null=True, 
        blank=True, 
        verbose_name="Intonation Score", 
        help_text="Score for intonation (0-10)."
    )
    fluency_score = models.FloatField(
        null=True, 
        blank=True, 
        verbose_name="Fluency Score", 
        help_text="Score for fluency (0-10)."
    )
    overall_score = models.FloatField(
        null=True, 
        blank=True, 
        verbose_name="Overall Score", 
        help_text="Automatically calculated as the average of other scores."
    )
    comments = models.TextField(
        verbose_name="Comments",
        help_text="Evaluator's comments for the feedback."
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Created At", 
        help_text="The date and time when the feedback was created."
    )
    modified_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="Last Modified At", 
        help_text="The date and time when the feedback was last modified."
    )

    def __str__(self):
        return f"Feedback by {self.evaluator or 'Unknown'} for {self.recording}"

    def save(self, *args, **kwargs):
        for field in ['pronunciation_score', 'intonation_score', 'fluency_score']:
            score = getattr(self, field)
            if score is not None and (score < 0 or score > 10):
                raise ValidationError(f"{field.replace('_', ' ').capitalize()} must be between 0 and 10.")

        scores = [
            self.pronunciation_score,
            self.intonation_score,
            self.fluency_score,
        ]
        valid_scores = [score for score in scores if score is not None]

        if valid_scores:
            self.overall_score = int(sum(valid_scores) / len(valid_scores))
        else:
            self.overall_score = None

        super().save(*args, **kwargs)

    def clean(self):
        if not self.comments:
            raise ValidationError("Comments cannot be empty.")
        if len(self.comments) < 10:
            raise ValidationError("Comments must be at least 10 characters long.")

    class Meta:
        verbose_name = "Feedback"
        verbose_name_plural = "Feedbacks"
