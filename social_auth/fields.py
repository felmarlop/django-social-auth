
import simplejson

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import smart_text


class JSONField(models.TextField):
    """Simple JSON field that stores python structures as JSON strings
    on database.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('default', dict)
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, *args, **kwargs):
        return self.to_python(value)

    def to_python(self, value):
        """
        Convert the input JSON value into python structures, raises
        django.core.exceptions.ValidationError if the data can't be converted.
        """
        if self.blank and not value:
            return {}
        value = value or '{}'
        if isinstance(value, bytes):
            value = str(value, 'utf-8')
        if isinstance(value, str):
            try:
                return simplejson.loads(value)
            except Exception as err:
                raise ValidationError(str(err))
        else:
            return value

    def validate(self, value, model_instance):
        """Check value is a valid JSON string, raise ValidationError on
        error."""
        if isinstance(value, str):
            super().validate(value, model_instance)
            try:
                simplejson.loads(value)
            except Exception as err:
                raise ValidationError(str(err))

    def get_prep_value(self, value):
        """Convert value to JSON string before save"""
        try:
            return simplejson.dumps(value)
        except Exception as err:
            raise ValidationError(str(err))

    def value_to_string(self, obj):
        """Return value from object converted to string properly"""
        return force_str(self.value_from_object(obj))

    def value_from_object(self, obj):
        """Return value dumped to string."""
        orig_val = super().value_from_object(obj)
        return self.get_prep_value(orig_val)


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^social_auth\.fields\.JSONField"])
except:
    pass
