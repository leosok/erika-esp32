# receiving Emails
from erika_cloud.models import Typewriter
from email.message import EmailMessage
import smtplib
from secrets import SMTP_PASSWORD, SMTP_SERVER, SMTP_USER

def print_mail_on_erika(erika:Typewriter):
    # Create a german date to print
    import locale
    from email.utils import parsedate_to_datetime
    mail_date = parsedate_to_datetime(request.json['headers']['date'])
    locale.setlocale(locale.LC_TIME, "de_DE")
    print_date = mail_date.strftime("%A, %d %b %Y %H:%M")

    print_template = [
        "\n\n",
        "--------  EMAIL -------\n",
        "{}".format(print_date),
        "Von: {}".format(request.json['headers']['from']),
        "Btr.: {}".format(request.json['headers']['subject']),
        " ",
        "{}".format(request.json['plain'])
    ]

    print_str = '\n'.join(print_template)
    erika_mqqt.mqttc.publish('erika/1/print', print_str)


def send_email(mail_from, mail_to, mail_subject, mail_content):
    msg = EmailMessage()
    msg['from'] = mail_from
    msg['to'] = mail_to
    msg['subject'] = mail_subject
    msg.set_content(mail_content)

    #Ports 465 and 587 are intended for email client to email server communication - sending email
    server = smtplib.SMTP(SMTP_SERVER, 587)

    #starttls() is a way to take an existing insecure connection and upgrade it to a secure connection using SSL/TLS.
    server.starttls()

    #Next, log in to the server
    server.login(SMTP_USER, SMTP_PASSWORD)

    #Send the mail
    resp = server.sendmail(mail_from, mail_to, msg.as_string())
    print(f"server.sendmail resp: {resp}")
    return resp