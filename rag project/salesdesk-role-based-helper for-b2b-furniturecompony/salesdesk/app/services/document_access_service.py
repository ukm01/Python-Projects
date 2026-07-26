from app.security.roles import ACCESS_ROLES
from app.services.ingestion.upload_exceptions import InvalidDocumentRolesError


def parse_allowed_roles(raw_roles: str) -> list[str]:
    requested_roles = {
        role.strip().lower()
        for role in raw_roles.split(",")
        if role.strip()
    }

    if not requested_roles:
        raise InvalidDocumentRolesError(
            "Select at least one role that can access the document."
        )

    invalid_roles = requested_roles.difference(ACCESS_ROLES)
    if invalid_roles:
        invalid_list = ", ".join(sorted(invalid_roles))
        raise InvalidDocumentRolesError(
            f"Unsupported document access role(s): {invalid_list}."
        )

    return [
        role
        for role in ACCESS_ROLES
        if role in requested_roles
    ]


def serialize_allowed_roles(roles: list[str]) -> str:
    return ",".join(roles)
