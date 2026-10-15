"""
Модуль пользовательских исключений для обработки мультимедийных данных.
Вариант 3: Аудиофайлы (AudioDecodeError, InvalidSampleRateError).
"""


class MediaError(Exception):
    """Базовое исключение для всех мультимедийных ошибок приложения."""

    def __init__(self, message: str, file_path: str = None):
        self.file_path = file_path
        self.raw_message = message
        full_message = f"[{file_path}] {message}" if file_path else message
        super().__init__(full_message)


class FileLoadError(MediaError):
    """Ошибка при поиске, чтении или загрузке медиафайла."""

    def __init__(self, file_path: str, reason: str = "Не удалось открыть файл"):
        super().__init__(f"Ошибка загрузки: {reason}", file_path)


class InvalidDataError(MediaError):
    """Ошибка повреждения структуры или формата медиаданных."""

    def __init__(self, file_path: str, data_type: str = "аудиоданные"):
        super().__init__(f"Некорректная структура данных ({data_type})", file_path)


class AudioDecodeError(MediaError):
    """Ошибка декодирования аудиопотока или повреждённых заголовков контейнера."""

    def __init__(self, file_path: str, reason: str = "Не удалось декодировать аудиопоток"):
        super().__init__(f"Сбой декодирования аудио: {reason}", file_path)


class InvalidSampleRateError(InvalidDataError):
    """Ошибка некорректной или неподдерживаемой частоты дискретизации звука."""

    def __init__(self, file_path: str, sample_rate: int):
        self.sample_rate = sample_rate
        super().__init__(file_path, data_type=f"недопустимая частота {sample_rate} Гц")