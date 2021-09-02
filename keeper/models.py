from django.db import models

# Create your models here.


class Pony(models.Model):

    STATUS_INIT = 0
    STATUS_NORMAL = 1
    STATUS_MISSING = 2

    name = models.CharField(max_length=255, db_index= True)
    passcode = models.CharField(max_length=255)
    dark_minute = models.IntegerField()
    last_hi_time = models.DateTimeField(null=True)
    status = models.IntegerField(default=0, db_index= True)
    notify_channel = models.CharField(max_length=10)
    notify_url = models.CharField(max_length=255)
    create_time = models.DateTimeField()


class History(models.Model):
    pony_id = models.IntegerField(db_index= True)
    create_time = models.DateTimeField()
    previous_status = models.IntegerField()
    current_status = models.IntegerField()

