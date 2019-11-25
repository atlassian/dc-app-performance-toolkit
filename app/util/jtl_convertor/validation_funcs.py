from util.jtl_convertor.validation_exception import ValidationException


def is_not_none(value: str) -> None:
    if value is None:
        raise ValidationException("Value is empty")


def is_number(value: str) -> None:
    if not value.isdigit():
        raise ValidationException(f"Value [{value}] is not a digit")


def is_not_blank(value: str) -> None:
    if (value is None) or (not value.strip()):
        raise ValidationException("Value is blank")
