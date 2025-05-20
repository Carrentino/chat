class ChatError(Exception):  # noqa
    """Базовая ошибка домена чата."""


class RoomNotFound(ChatError):  # noqa
    """Комната не найдена."""


class PermissionDenied(ChatError):  # noqa
    """У пользователя нет доступа к комнате."""  # noqa


class InvalidMessage(ChatError):  # noqa
    """Некорректное сообщение (пустой контент и без вложений)."""  # noqa
