from django.db import models

# Create your models here.

poll_status = [
    ("open", "open"),
    ("closed", "closed")
]


class Poll(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    created_at = models.DateField("created at")
    expiry = models.DateField("expiry")
    
    status = models.CharField(
        choices=poll_status,
        default="open"
    )

    def __str__(self):
        return self.title
    
    def is_open(self):
        return self.status == "open"


class Question(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)

    def __str__(self):
        return self.text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text