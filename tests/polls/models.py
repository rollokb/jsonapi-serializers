from django.db import models


class Poll(models.Model):
    question = models.CharField(max_length=200)


class Choice(models.Model):
    poll = models.ForeignKey(Poll)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField()
