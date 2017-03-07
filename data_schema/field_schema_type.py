class FieldSchemaType(object):
    """
    Specifies all of the field schema types supported.
    """
    DATE = 'DATE'
    DATETIME = 'DATETIME'
    INT = 'INT'
    FLOAT = 'FLOAT'
    STRING = 'STRING'
    BOOLEAN = 'BOOLEAN'
    DURATION = 'DURATION'

    @classmethod
    def choices(cls):
        """
        An alphabetical list of the types. This must be alphabetical for the
        database default on the Field Schema model's field_type field
        """
        def is_internal(x):
            return x.startswith('__') and x.endswith('__')

        types = [(val, val) for val in cls.__dict__ if not is_internal(val) and val != 'choices']

        types.sort()
        return types


class FieldSchemaCase(object):
    LOWER = 'LOWER'
    UPPER = 'UPPER'
