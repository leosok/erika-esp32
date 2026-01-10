import pytest
from ninja.testing import TestClient
from typewriter.api import typewriter_router
from typewriter.models import Typewriter, Message
from django.contrib.auth.models import User

@pytest.fixture
def api_client():
    return TestClient(typewriter_router)

@pytest.fixture
def typewriter_user(db):
    user = User.objects.create(username="testuser", email="test@example.com")
    return Typewriter.objects.create(
        user=user,
        uuid="test-uuid",
        erika_name="test-erika",
        email="test-erika@erika-cloud.de"
    )

@pytest.mark.django_db
def test_incoming_webhook_success(api_client, typewriter_user):
    payload = {
        "headers": {
            "to": "test-erika@erika-cloud.de",
            "from": "sender@example.com",
            "subject": "Hello Erika!"
        },
        "plain": "This is a message for the typewriter."
    }
    
    response = api_client.post("/incoming", json=payload)
    
    assert response.status_code == 200
    assert response.json() == {"detail": "Message created"}
    
    assert Message.objects.count() == 1
    msg = Message.objects.first()
    assert msg.typewriter == typewriter_user
    assert msg.sender == "sender@example.com"
    assert msg.subject == "Hello Erika!"
    assert msg.body == "This is a message for the typewriter."

@pytest.mark.django_db
def test_incoming_webhook_list_in_headers(api_client, typewriter_user):
    # This simulates the user's data where 'received' is a list
    payload = {
        "headers": {
            "to": "test-erika@erika-cloud.de",
            "from": "sender@example.com",
            "subject": "Complex Headers",
            "received": [
                "from A by B...",
                "from C by A..."
            ]
        },
        "plain": "Testing list in headers."
    }
    
    response = api_client.post("/incoming", json=payload)
    
    assert response.status_code == 200
    assert response.json() == {"detail": "Message created"}

@pytest.mark.django_db
def test_incoming_webhook_no_typewriter(api_client):
    payload = {
        "headers": {
            "to": "nonexistent@erika-cloud.de",
            "from": "sender@example.com",
            "subject": "Hello?"
        },
        "plain": "Is anyone there?"
    }
    
    response = api_client.post("/incoming", json=payload)
    
    assert response.status_code == 404
    assert "No Typewriter found" in response.json()["detail"]

@pytest.mark.django_db
def test_incoming_webhook_missing_to_header(api_client):
    payload = {
        "headers": {
            "from": "sender@example.com",
            "subject": "Missing To"
        },
        "plain": "Where is this going?"
    }
    
    response = api_client.post("/incoming", json=payload)
    
    assert response.status_code == 404
    assert "Missing 'To' header" in response.json()["detail"]

@pytest.mark.django_db
def test_incoming_webhook_secondary_url(api_client, typewriter_user):
    payload = {
        "headers": {
            "to": "test-erika@erika-cloud.de",
            "from": "sender@example.com",
            "subject": "Secondary URL"
        },
        "plain": "Testing the other endpoint."
    }
    
    response = api_client.post("/incoming_email", json=payload)
    
    assert response.status_code == 200
    assert response.json() == {"detail": "Message created"}
