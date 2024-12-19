from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, Any


@dataclass
class Person:
    first_name: str = field(default="")
    last_name: str = field(default="")
    birthdate: str = field(default=None)
    gender: str = field(default=None)
    company_code: str = field(default="")
    street: str = field(default="")
    house_number: str = field(default="")
    postcode: str = field(default="")
    city: str = field(default="")
    family_status: str = field(default="")
    nationality: str = field(default="")
    phone_number: str = field(default="")
    email: str = field(default="")

    @classmethod
    def from_dict(cls, data: dict):
        input_date = data.get("birthdate", "")
        dt = datetime.strptime(input_date, "%Y-%m-%d")  # Parse the input string
        formatted_date = dt.strftime("%d.%m.%Y")
        return cls(
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            birthdate=formatted_date,
            gender=data.get("gender", ""),
            company_code=data.get("company_code", ""),
            street=data.get("street", ""),
            house_number=data.get("house_number", ""),
            postcode=data.get("postcode", ""),
            city=data.get("city", ""),
            family_status=data.get("family_status", ""),
            nationality=data.get("nationality", ""),
            phone_number=data.get("phone_number", ""),
            email=data.get("email", "")
        )

    def dict(self) -> Dict[str, Any]:
        return asdict(self)
