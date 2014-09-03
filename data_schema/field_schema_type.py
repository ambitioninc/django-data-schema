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

    @classmethod
    def choices(cls):
        def is_internal(x):
            return x.startswith('__') and x.endswith('__')

        return [(val, val) for val in cls.__dict__ if not is_internal(val) and val != 'choices']
