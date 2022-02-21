# receiving Emails
# For relative imports to work in Python 3.6
import sys;

sys.path.append("..")

from models import Typewriter, Message
from email.message import EmailMessage
import smtplib
from secrets import SMTP_PASSWORD, SMTP_SERVER, SMTP_USER
from utils.mqqt import ErikaMqqt


def print_mail_on_erika(message: Message):
    # Create a german date to print
    import locale
    from email.utils import parsedate_to_datetime
    typewriter = message.typewriter
    mail_date = message.received_at
    locale.setlocale(locale.LC_TIME, "de_DE")
    print_date = mail_date.strftime("%A, %d %b %Y %H:%M")

    if message.subject.lower() == 'print':
        print_template = ["\n\n", message.body]
    else:
        print_template = [
            "\n\n",
            "--------  EMAIL -------\n",
            "{}".format(print_date),
            "Von: {}".format(message.sender),
            "Btr.: {}".format(message.subject),
            " ",
            "{}".format(message.body)
        ]

    message.is_printed = True
    message.save()
    print_str = '\n'.join(print_template)
    print_on_erika(typewriter, print_str)


def print_on_erika(typewriter: Typewriter, text: str):
    erika_mqqt = ErikaMqqt()
    erika_mqqt.mqttc.publish(f'erika/print/{typewriter.uuid}', text)
    return True


def send_email(mail_from, mail_to, mail_subject, mail_content):
    msg = EmailMessage()
    msg['from'] = mail_from
    msg['to'] = mail_to
    msg['subject'] = mail_subject
    msg.set_content(mail_content)

    # Ports 465 and 587 are intended for email client to email server communication - sending email
    server = smtplib.SMTP(SMTP_SERVER, 587)

    # starttls() is a way to take an existing insecure connection and upgrade it to a secure connection using SSL/TLS.
    server.starttls()

    # Next, log in to the server
    server.login(SMTP_USER, SMTP_PASSWORD)

    # Send the mail
    resp = server.sendmail(mail_from, mail_to, msg.as_string())
    print(f"server.sendmail resp: {resp}")
    return resp
