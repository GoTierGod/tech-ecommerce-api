import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import pandas


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


def profanity_filter(value):
    bad_words_path = "api/datasets/bad_words.csv"

    df = pandas.read_csv(bad_words_path)

    input_text = str(value).lower()

    for index, row in df.iterrows():
        word = row["word"].lower()

        if word in input_text:
            raise ValidationError(
                _("Text was detected as inappropriate"), code="inappropriate_text"
            )
