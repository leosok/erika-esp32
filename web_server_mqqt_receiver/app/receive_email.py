# receiving Emails
from model import Typewriter

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
