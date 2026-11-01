import pytest
from pydantic import ValidationError

from app.schemas.crm import LeadCreate
from app.services.crm import transition_lead


def test_public_lead_requires_a_contact_channel_and_normalizes_email():
    lead = LeadCreate(name="  Customer  ", email=" PERSON@Example.com ", preferred_locale="tg")
    assert lead.name == "Customer"
    assert lead.email == "person@example.com"
    assert lead.preferred_locale == "tg"
    with pytest.raises(ValidationError):
        LeadCreate(name="Customer")


def test_lead_workflow_records_contact_and_terminal_outcomes():
    assert transition_lead("new", "contacted") == "contacted"
    assert transition_lead("contacted", "converted") == "converted"
    with pytest.raises(ValueError):
        transition_lead("converted", "new")
    with pytest.raises(ValueError):
        transition_lead("unknown", "new")
