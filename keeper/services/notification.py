from django.core.mail import send_mail


def send_email(address : str, title: str, content: str):
    send_mail(title, content, recipient_list= [address])