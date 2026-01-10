import json
import logging
import os
from email.utils import parseaddr
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.handlers.wsgi import WSGIRequest
from django.core.mail import send_mail
from django.db import IntegrityError
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from ninja import NinjaAPI, Router, Body
from django.shortcuts import get_object_or_404

# from utils.mail_utils import print_on_erika
from .models import Textdata, Typewriter, Message
from .schemas import TextdataSchema, TypewriterSchema, MessageSchema, TypewriterCreateSchema, EmailWebhookSchema, WebhookResponseSchema
from typing import List, Dict, Any

from erika_cloud.utils.dj_mail_utils import send_password_reset

from .utils.mqtt_utils import send_print_message, send_print_message_to_all

typewriter_router = Router(tags=["Typewriter"])

@typewriter_router.get("/pages", response=List[TextdataSchema])
def list_pages(request):
    pages = Textdata.objects.order_by('timestamp').distinct('hashid')
    return pages

@typewriter_router.get("/pages/{hashid}", response=TextdataSchema)
def single_page(request, hashid: str):
    action = request.query_params.get('action')
    if action == "delete":
        Textdata.objects.filter(hashid=hashid).delete()
        return {"detail": "Page deleted"}
    else:
        lines = Textdata.objects.filter(hashid=hashid).order_by('line_number')
        return {"lines": lines, "fulltext": Textdata.as_fulltext(hashid)}

@typewriter_router.get("/keycast/{uuid}", response=dict)
def keycast_receiver(request, uuid: str):
    MQQT_SERVER = os.getenv('MQQT_SERVER')
    MQQT_USERNAME = os.getenv('MQQT_USERNAME')
    MQQT_PASSWORD = os.getenv('MQQT_PASSWORD')
    topic_keycast = f"erika/keystrokes/{uuid}"
    topic_status = f"erika/status/{uuid}"
    return {
        "config": {
            "MQQT_SERVER": MQQT_SERVER,
            "MQQT_USERNAME": MQQT_USERNAME,
            "MQQT_PASSWORD": MQQT_PASSWORD,
            "erika_uuid": uuid,
            "topic_keycast": topic_keycast,
            "topic_status": topic_status
        }
    }

@typewriter_router.get("/erika/{uuid}/emails", response=List[MessageSchema])
def erika_single(request, uuid: str):
    typewriter = get_object_or_404(Typewriter, uuid=uuid)
    emails = typewriter.messages.all()
    return emails

@typewriter_router.get("/erika/{erika_name}", response=List[MessageSchema])
def erika_sender(request, erika_name: str):
    try:
        typewriter = Typewriter.objects.get(erika_name=erika_name.lower())
        emails = typewriter.messages.all()
        if emails.exists():
            return emails
        else:
            return {"detail": f"No messages for typewriter `{erika_name.capitalize()}`"}, 404
    except Typewriter.DoesNotExist:
        return {"detail": f"No typewriter found with name `{erika_name.capitalize()}`"}, 404

@typewriter_router.post("/incoming", response={200: WebhookResponseSchema, 404: WebhookResponseSchema})
@typewriter_router.post("/incoming_email", response={200: WebhookResponseSchema, 404: WebhookResponseSchema})
def incoming_webhook(request, data: EmailWebhookSchema):
    try:
        _, receiver_email = parseaddr(data.headers.get('to', ''))
        _, sender_email = parseaddr(data.headers.get('from', ''))
        subject = data.headers.get('subject', '(No Subject)')
        
        if not receiver_email:
            return 404, {"detail": "Missing 'To' header in email webhook"}

        erika = Typewriter.objects.get(email=receiver_email.lower())
    except Typewriter.DoesNotExist:
        return 404, {"detail": f"No Typewriter found for address {receiver_email}"}
    except Exception as e:
        logging.error(f"Error processing webhook: {e}")
        return 404, {"detail": f"Error processing webhook: {str(e)}"}

    Message.objects.create(
        typewriter=erika,
        sender=sender_email,
        subject=subject,
        body=data.plain
    )

    return 200, {"detail": "Message created"}

@typewriter_router.post("/new")
def register_typewriter(request, data: TypewriterCreateSchema) -> TypewriterSchema:
    # Create the user
    user, was_just_created = User.objects.get_or_create(
        username=data.email.lower(),
        first_name=data.firstname,
        last_name=data.lastname,
        email=data.email.lower(),
        is_active=True  # User is inactive until they set their password
    )

    # check if a typewriter with the same name already exists, if yes change the name to xxx1
    i = 1
    while Typewriter.objects.filter(erika_name=data.erika_name.lower()).exists():
        i += 1
        data.erika_name = f"{data.erika_name}{i}"

    # Create the typewriter and associate with the user
    typewriter = Typewriter.objects.create(
        user=user,
        uuid=data.uuid,
        erika_name=data.erika_name.lower(),
        email=f"{data.erika_name.lower()}@{os.getenv('APP_HOST')}",
        chat_active=data.chat_active
    )

    # Generate password reset link
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    try:
        send_password_reset(user)
    except Exception as e:
        logging.info( {"detail": f"Error sending email to {user.email}: {e}"})
    # # Send email with the reset link
    # subject = 'Set your password'
    # message = render_to_string('registration/set_password_email.html', {
    #     'user': user,
    #     'reset_link': reset_link,
    # })
    # send_mail(subject, message, 'admin@erika-cloud.de', [user.email])

    return_typewriter = TypewriterSchema(
        id=typewriter.pk,
        uuid=typewriter.uuid,
        user_firstname=user.first_name,
        user_lastname=user.last_name,
        user_email=user.email,
        chat_active=typewriter.chat_active,
        erika_name=typewriter.erika_name,
        email=typewriter.email,
        status=typewriter.status
    )

    return return_typewriter


def register_typewriter(request, data: TypewriterCreateSchema):
    typewriter, created = Typewriter.objects.get_or_create(uuid=data.uuid)

    typewriter.user_firstname = data.firstname
    typewriter.user_lastname = data.lastname
    typewriter.user_email = data.email.lower()
    typewriter.chat_active = data.chat_active
    typewriter.erika_name = data.erika_name.lower()

    saved = False
    i = 1
    while not saved:
        try:
            typewriter.save()
            saved = True
        except IntegrityError:
            i += 1
            typewriter.erika_name = f"{data.erika_name}{i}"

    typewriter.email = f"{typewriter.erika_name.lower()}@{os.getenv('APP_HOST')}"
    typewriter.save()

    typewriter_return = TypewriterSchema.from_orm(typewriter)

    return typewriter_return

@typewriter_router.post("/{uuid}/print", response=dict)
def typewriter_print(request:WSGIRequest, uuid: str):
    requestbody = json.loads(request.body.decode('utf-8'))
    print_text = requestbody['body']
    print(f"Printing on {uuid}: {print_text}")
    typewriter = get_object_or_404(Typewriter, uuid=uuid)
    send_print_message(uuid, print_text)
    #print_on_erika(typewriter, data['body'])
    return {"detail": f"Printing on `{typewriter.erika_name.capitalize()}`"}

@typewriter_router.post("/print/all", response=dict)
def typewriter_print_all(request: WSGIRequest):
    requestbody = json.loads(request.body.decode('utf-8'))
    print_text = requestbody['body']
    print(f"Broadcasting print message to all typewriters: {print_text}")
    send_print_message_to_all(print_text)
    return {"detail": "Broadcasting print message to all online typewriters"}

@typewriter_router.get("/online", response=List[TypewriterSchema])
def typewriters_online(request):
    typewriters = Typewriter.objects.filter(status=1).select_related('user')
    typewriter_schema_response = [TypewriterSchema.from_orm(typewriter) for typewriter in typewriters]
    return typewriter_schema_response
