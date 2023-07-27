import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class RegexPasswordValidator:
    def validate(self, password, user=None):
        regex = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[^A-Za-z\d]).+$"
        if not re.match(regex, password):
            raise ValidationError(
                _(
                    "Your password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character."
                ),
                code="invalid_password_format",
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character."
        )
