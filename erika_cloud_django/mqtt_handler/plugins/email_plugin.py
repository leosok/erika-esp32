from django.core.mail import send_mail
import datetime
from typewriter.models import Textdata
from .base import MQTTPlugin

class EmailPlugin(MQTTPlugin):
    async def handle_message(self, typewriter_id: str, payload: dict) -> bool:
        try:
            full_text = Textdata.as_fulltext(payload['hashid'])
            subject = f'Erika Text {datetime.datetime.now().strftime("%d.%m.%Y")}'
            
            send_mail(
                subject=subject,
                message=full_text,
                from_email=payload['from'],
                recipient_list=[payload['to']],
                fail_silently=False,
            )
            self.logger.info(f"Sent email from {payload['from']} to {payload['to']}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False
