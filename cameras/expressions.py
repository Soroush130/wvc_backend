from django.db.models import DateTimeField, Func


class ConvertToTimezone(Func):
    output_field = DateTimeField()

    def __init__(self, datetime_field, timezone_field, **extra):
        expressions = datetime_field, timezone_field
        super(ConvertToTimezone, self).__init__(*expressions, **extra)

    def as_sql(self, compiler, connection, fn=None, template=None, arg_joiner=None, **extra_context):
        params = []
        sql_parts = []
        for arg in self.source_expressions:
            arg_sql, arg_params = compiler.compile(arg)
            sql_parts.append(arg_sql)
            params.extend(arg_params)
        return "%s AT TIME ZONE %s" % tuple(sql_parts), params