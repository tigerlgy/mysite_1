import threading
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.html import strip_tags
from django.shortcuts import render
from notifications.signals import notify
from .models import Comment
from django.core.mail import send_mail
from django.conf import settings

@receiver(post_save, sender=Comment)
def send_notification(sender, instance, **kwargs):
    # Send Web notifications
    if instance.reply_to is None:
        # comment
        recipient = instance.content_object.get_user()
        if instance.content_type.model == 'blog':
            blog = instance.content_object
            verb = '{0} has commented on your blog ({1})'.format(instance.user.get_nickname_or_username(), blog.title)
        else:
            raise Exception('unkown comment object')
    else: 
        # reply
        recipient = instance.reply_to
        verb = '{0} has replied to your comment "{1}"'.format(instance.user.get_nickname_or_username(), strip_tags(instance.parent.text))
    url = instance.content_object.get_url() + "#comment_" + str(instance.pk)
    notify.send(instance.user, recipient=recipient, verb=verb, action_object=instance, url=url)

class SendMail(threading.Thread):
    def __init__(self, subject, text, email, fail_silently=False):
        self.subject = subject
        self.text = text
        self.email = email
        self.fail_silently = fail_silently
        threading.Thread.__init__(self)

    def run(self):
        send_mail(
            self.subject,
            '',
            settings.EMAIL_HOST_USER,
            [self.email],
            fail_silently=self.fail_silently,
            html_message=self.text)


@receiver(post_save, sender=Comment)
def send_email(sender, instance, **kwargs):
    # Send Email notification to writer of the blog.
    if instance.parent is None:
        # Reply to the Blog
        subject = 'Someone has commented on your blog'
        email = instance.content_object.get_email()
    else:
        # Reply to the Comment
        subject = 'Someone has repled to your comment'
        email = instance.reply_to.email
    if email !='':
        # text = '%s\n<a href="%s">%s</a>' % (self.text, self.content_object.get_url(), 'Click here to check.')
        context = {}
        context['comment_text'] = instance.text
        context['url'] = instance.content_object.get_url()
        text = render(None,'comment/send_mail.html',context).content.decode('utf-8')
        send_mail = SendMail(subject, text, email)
        send_mail.start()

