def validate_extra_fileds(cls, values):
    required_fields = {field.alias for field in cls.__fields__.values() if field.alias != "extra"}

    extra_fields = {}
    for field_name, value in values.items():
        if field_name not in required_fields:
            extra_fields[field_name] = value

    values["extra"] = extra_fields
    assert len(values["extra"]) == 0, f"Extra fileds are not permitted. {values['extra']}"
    return values
