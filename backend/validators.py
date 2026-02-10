import re

def validate_ngo_request(data):
    errors = {}

    if not data.get("org_name") or len(data["org_name"]) < 3:
        errors["org_name"] = "Organization name must be at least 3 characters"

    if not data.get("contact_person") or len(data["contact_person"]) < 3:
        errors["contact_person"] = "Contact person name is too short"

    if not data.get("phone"):
        errors["phone"] = "Contact number is required"
    elif not data["phone"].isdigit() or len(data["phone"]) != 10:
        errors["phone"] = "Contact number must be exactly 10 digits"

    if not data.get("email"):
        errors["email"] = "Email is required"
    elif not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", data["email"]):
        errors["email"] = "Invalid email format"

    if not data.get("purpose") or len(data["purpose"]) < 5:
        errors["purpose"] = "Purpose must be at least 5 characters"

    if not data.get("city") or not data["city"].replace(" ", "").isalpha():
        errors["city"] = "City name is invalid"

    if not data.get("description") or len(data["description"]) < 10:
        errors["description"] = "Description must be at least 10 characters"

    return errors
