import jsl
import jsonschema
__author__ = 'Michal Kononenko'


class JSONSchema(jsl.Document):

    def validate(self, dict_to_validate):
        try:
            jsonschema.validate(dict_to_validate, self.get_schema())
            return True, 'success'
        except jsonschema.ValidationError as val_error:
            return False, str(val_error)
