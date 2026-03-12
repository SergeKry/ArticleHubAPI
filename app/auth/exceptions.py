class UserAlreadyExistsError(Exception):
    pass


class PasswordMismatchError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class InvalidRefreshTokenError(Exception):
    pass
