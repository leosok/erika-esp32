import locale
from email.utils import parsedate_to_datetime
mail_date = parsedate_to_datetime("Thu, 20 May 2021 00:46:25 +0200")
locale.setlocale(locale.LC_TIME, "de_DE")
putput = mail_date.strftime("%A, %d %b %Y %H:%M")
print(putput)