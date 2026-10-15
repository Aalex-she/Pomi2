"""
Модуль обработчиков медиафайлов на базе абстрактных классов.
Вариант 3: обработка аудиопотоков (WAV, MP3).
"""

from abc import ABC, abstractmethod
import os
import wave
from media_exceptions import (
    MediaError,
    FileLoadError,
    InvalidDataError,
    AudioDecodeError,
    InvalidSampleRateError,
)


class MediaProcessor(ABC):
    """Абстрактный базовый класс для мультимедийных процессоров."""

    @abstractmethod
    def process(self, file_path: str) -> dict:
        """Выполняет полную цепочку обработки файла и возвращает отчёт."""
        pass

    @abstractmethod
    def validate(self, file_path: str) -> bool:
        """Проверяет файл на доступность, расширение и целостность."""
        pass


class AudioProcessor(MediaProcessor):
    """Конкретный обработчик аудиофайлов (WAV, MP3) для Варианта 3."""

    SUPPORTED_EXTENSIONS = ('.wav', '.mp3')
    # Общепринятые стандарты частот дискретизации звука в ЦОС
    STANDARD_RATES = (8000, 11025, 16000, 22050, 32000, 44100, 48000, 88200, 96000, 192000)

    def validate(self, file_path: str) -> bool:
        """
        Комплексная валидация медиафайла.
        Выбрасывает специфические исключения при обнаружении аномалий.
        """
        if not file_path:
            raise FileLoadError("", "Имя файла не может быть пустым")

        if not os.path.exists(file_path):
            raise FileLoadError(file_path, "Файл не найден на диске")

        if not file_path.lower().endswith(self.SUPPORTED_EXTENSIONS):
            raise AudioDecodeError(
                file_path,
                f"Неподдерживаемый формат. Разрешены только {self.SUPPORTED_EXTENSIONS}"
            )

        if os.path.getsize(file_path) == 0:
            raise InvalidDataError(file_path, "Файл пуст (0 байт)")

        return True

    def load_audio(self, file_path: str) -> dict:
        """
        Загружает аудиофайл и считывает параметры аудиопотока.
        Для WAV использует разбор заголовка RIFF через модуль wave.
        """
        self.validate(file_path)

        if file_path.lower().endswith('.wav'):
            try:
                with wave.open(file_path, 'rb') as wf:
                    channels = wf.getnchannels()
                    sampwidth = wf.getsampwidth()
                    framerate = wf.getframerate()
                    nframes = wf.getnframes()
                    duration = round(nframes / float(framerate), 2) if framerate > 0 else 0
                    raw_frames = wf.readframes(min(nframes, 1024))
            except wave.Error as e:
                raise AudioDecodeError(file_path, f"Заголовок WAV повреждён: {e}")
            except Exception as e:
                raise FileLoadError(file_path, f"Сбой чтения потока: {e}")

            if framerate <= 0 or framerate not in self.STANDARD_RATES:
                raise InvalidSampleRateError(file_path, framerate)

            return {
                "format": "WAV",
                "channels": channels,
                "sample_width": sampwidth,
                "sample_rate": framerate,
                "duration": duration,
                "frames_count": nframes,
                "preview_bytes": len(raw_frames),
            }

        else:
            # Обработка MP3: чтение ID3/MPEG заголовка
            try:
                with open(file_path, 'rb') as f:
                    header = f.read(10)
                if len(header) < 4:
                    raise AudioDecodeError(file_path, "Файл слишком мал для MP3")

                # Эмуляция стандартного декодирования MP3-потока
                sample_rate = 44100
                bitrate = 320
                size_bytes = os.path.getsize(file_path)
                duration = round(size_bytes / (bitrate * 128), 2)

                return {
                    "format": "MP3",
                    "channels": 2,
                    "sample_rate": sample_rate,
                    "bitrate": bitrate,
                    "duration": max(duration, 0.5),
                }
            except Exception as e:
                raise AudioDecodeError(file_path, f"Ошибка структуры MP3: {e}")

    def get_audio_info(self, file_path: str) -> str:
        """Возвращает строковое описание параметров аудиофайла."""
        meta = self.load_audio(file_path)
        return (
            f"Аудио [{meta['format']}]: {file_path}, "
            f"длительность: {meta['duration']} сек, "
            f"частота: {meta['sample_rate']} Гц, "
            f"каналы: {meta['channels']}"
        )

    def process(self, file_path: str) -> dict:
        """
        Полиморфный метод обработки аудиопотока.
        """
        meta = self.load_audio(file_path)
        return {
            "status": "Success",
            "file": file_path,
            "format": meta["format"],
            "sample_rate": meta["sample_rate"],
            "duration": meta["duration"],
            "ready_for_playback": True,
        }


def safe_process_media(processor: MediaProcessor, file_path: str) -> dict:
    """Безопасная функция-клиент с многоуровневым перехватом исключений."""
    try:
        return processor.process(file_path)
    except FileLoadError as e:
        print(f"[ПЕРЕХВАЧЕНО: FileLoadError] -> {e}")
    except InvalidSampleRateError as e:
        print(f"[ПЕРЕХВАЧЕНО: InvalidSampleRateError] -> {e}")
    except AudioDecodeError as e:
        print(f"[ПЕРЕХВАЧЕНО: AudioDecodeError] -> {e}")
    except InvalidDataError as e:
        print(f"[ПЕРЕХВАЧЕНО: InvalidDataError] -> {e}")
    except MediaError as e:
        print(f"[ПЕРЕХВАЧЕНО: Общая MediaError] -> {e}")
    except Exception as e:
        print(f"[НЕПРЕДВИДЕННАЯ ОШИБКА] -> {e}")
    finally:
        print(f"[FINALLY] Завершена попытка обработки файла: {file_path}")
    return None
