from django.db import models
from django.utils import timezone
from datetime import timedelta
 

def expiry_default():
    return timezone.localdate() + timedelta(days=3)


class Poll(models.Model):
    title = models.CharField(max_length=100, blank=False, null=False)
    created_at = models.DateField("created at", default=timezone.localdate)
    expiry = models.DateField("expiry", default=expiry_default)

    def __str__(self):
        return self.title
    
    def is_expired(self):
        return self.expiry < timezone.localdate()


class Question(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    text = models.CharField(max_length=300, blank=False, null=False)

    def __str__(self):
        return self.text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200, blank=False, null=False)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text
