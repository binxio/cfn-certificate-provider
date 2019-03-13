"""
implements a schema validator which put the defaults in the object which is validated.abs
Copied straight from
https://python-jsonschema.readthedocs.io/en/latest/faq/#why-doesn-t-my-schema-that-has-a-default-property-actually-set-the-default-on-my-instance
"""
from jsonschema import Draft4Validator, validators


def extend_with_default(validator_class):
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        for prop, subschema in properties.items():
            if "default" in subschema:
                instance.setdefault(prop, subschema["default"])

        for error in validate_properties(validator, properties, instance, schema,):
            yield error

    return validators.extend(
        validator_class, {"properties": set_defaults},
    )


validator = extend_with_default(Draft4Validator)


def validate(obj, schema):
    """
    validates the object against the schema, inserting default values when required
    """
    validator(schema).validate(obj)
