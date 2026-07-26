from enum import Enum


class AccessRole(str, Enum):
    ADMIN = "admin"
    SALES = "sales"
    MANAGER = "manager"


ACCESS_ROLES = tuple(role.value for role in AccessRole)
