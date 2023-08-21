from django.urls.converters import StringConverter


class IntListConverter(StringConverter):
    regex = r"\d+(?:,\d+)*"

    def to_python(self, value):
        return [int(item) for item in value.split(",")]

    def to_url(self, value):
        return ",".join(str(item) for item in value)
