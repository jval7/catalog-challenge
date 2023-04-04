from enum import Enum


class Roles(str, Enum):
    """Enum for user roles"""

    admin = "admin"
    super_admin = "super_admin"
    anonymous = "anonymous"
