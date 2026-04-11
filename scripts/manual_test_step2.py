from pydantic import ValidationError

from app.core.models.message import MessageEnvelope
from app.core.validation.business import validate_business_rules
from app.core.validation.exceptions import BusinessValidationError


valid_data = {
    "source": "client_1",
    "payload": {
        "operation": "set_value",
        "resource_id": "sensor_01",
        "value": 42
    }
}

invalid_structural_data = {
    "source": "client_1",
    "payload": {
        "operation": "set_value",
        "resource_id": "",
        "value": 42
    }
}

invalid_business_data = {
    "source": "client_1",
    "payload": {
        "operation": "set_value",
        "resource_id": "readonly_sensor",
        "value": 42
    }
}


def run_case(name: str, data: dict) -> None:
    print(f"\n--- {name} ---")
    try:
        message = MessageEnvelope.model_validate(data)
        print("Strukturalna walidacja: OK")
        validate_business_rules(message)
        print("Biznesowa walidacja: OK")
        print("Wynik końcowy: komunikat poprawny")
    except ValidationError as e:
        print("Strukturalna walidacja: BŁĄD")
        print(e)
    except BusinessValidationError as e:
        print("Biznesowa walidacja: BŁĄD")
        print(e)


run_case("Przypadek poprawny", valid_data)
run_case("Błąd strukturalny", invalid_structural_data)
run_case("Błąd biznesowy", invalid_business_data)