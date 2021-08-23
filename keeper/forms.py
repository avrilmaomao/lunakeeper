from django.forms import CharField,SlugField,ChoiceField
from .consts import *

class NameField(SlugField):

    def __init__(self, **kwargs):
        super().__init__(**kwargs, max_length= 50, min_length=2)


class PasscodeField(CharField):

    def __init__(self, ** kwargs):
        super().__init__(**kwargs, min_length=3, max_length=50)


class NotifyChannelField(ChoiceField):
    def __init__(self, ** kwargs):
        super().__init__(choices= (
            (NOTIFY_CHANNEL_EMAIL,NOTIFY_CHANNEL_EMAIL), (NOTIFY_CHANNEL_SLACK,NOTIFY_CHANNEL_SLACK )
        )
        ,**kwargs,)