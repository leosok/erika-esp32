from email.message import EmailMessage
# Import smtplib for the actual sending function
import smtplib
from secrets import SMTP_PASSWORD, SMTP_SERVER, SMTP_USER

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