class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundException(AppException):
    def __init__(self, entity: str, id: int | str | None = None):
        detail = f"{entity} not found" if not id else f"{entity} with id={id} not found"
        super().__init__(detail, status_code=404)


class AlreadyExistsException(AppException):
    def __init__(self, entity: str, field: str, value: str):
        super().__init__(f"{entity} with {field}={value} already exists", status_code=409)


class ForbiddenException(AppException):
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, status_code=403)
