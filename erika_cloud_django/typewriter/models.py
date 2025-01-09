import logging
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
import locale
from .utils.mqtt_utils import send_print_message


class Typewriter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    erika_name = models.CharField(max_length=255, null=True, unique=True)
    uuid = models.CharField(max_length=255, unique=True)
    email = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.IntegerField(default=0)
    chat_active = models.BooleanField(default=True)
    last_seen = models.DateTimeField(default=timezone.now)

    @property
    def user_firstname(self):
        return self.user.first_name

    @property
    def user_lastname(self):
        return self.user.last_name

    @property
    def user_email(self):
        return self.user.email

    def __str__(self):
        return self.erika_name

    def format_mail_for_printing(self, message):
        locale.setlocale(locale.LC_TIME, "de_DE")
        print_date = message.received_at.strftime("%A, %d %b %Y %H:%M")

        if message.subject.lower() == 'print':
            print_template = ["\n\n", message.body]
        else:
            print_template = [
                "\n\n",
                "--------  EMAIL -------\n",
                f"{print_date}",
                f"Von: {message.sender}",
                f"Btr.: {message.subject}",
                " ",
                f"{message.body}"
            ]
        return '\n'.join(print_template)

    def print_mails(self):
        unprinted_messages = self.messages.filter(is_printed=False)
        logging.info(f"Printing {len(unprinted_messages)} messages on {self.erika_name}")
        for message in unprinted_messages:
            logging.info(f"Printing message {message.subject} from {message.sender} on {self.erika_name}")
            formatted_text = self.format_mail_for_printing(message)
            send_print_message(self.uuid, formatted_text)
            message.is_printed = True
            message.save()


class Textdata(models.Model):
    typewriter = models.ForeignKey(
        Typewriter,
        on_delete=models.CASCADE,
        null=True,  # Allow null values
        blank=True  # Allow blank in forms
    )
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    hashid = models.CharField(max_length=255)
    line_number = models.IntegerField()

    @classmethod
    def count_lines(cls, hashid):
        return cls.objects.filter(hashid=hashid).count()

    @classmethod
    def as_fulltext(cls, hashid, min_length=30):
        lines = cls.objects.filter(hashid=hashid).order_by('line_number')
        
        fulltext = ''
        for line in lines:
            if len(line.content) <= min_length:
                fulltext += line.content + '\n'
            else:
                fulltext += line.content + ' '
        return fulltext.strip()


class Message(models.Model):
    typewriter = models.ForeignKey(Typewriter, related_name='messages', on_delete=models.CASCADE)
    sender = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    received_at = models.DateTimeField(default=timezone.now)
    is_printed = models.BooleanField(default=False)