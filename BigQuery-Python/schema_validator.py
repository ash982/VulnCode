# schema_validator.py
import xmlschema

class SchemaValidator:
    def __init__(self, schema_path):
        self.schema = xmlschema.XMLSchema(schema_path)

    def validate(self, data):
        try:
            self.schema.validate(data)
        except xmlschema.exceptions.XMLSchemaValidationError as e:
            raise ValueError(f"Validation failed: {e}")
