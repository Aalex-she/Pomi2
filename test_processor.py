"""
Тестовый комплекс для проверки AudioProcessor и перехвата исключений.
Генерирует временные тестовые аудиофайлы прямо в процессе выполнения.
"""

import os
import struct
import wave
from media_exceptions import (
    MediaError,
    FileLoadError,
    InvalidDataError,
    AudioDecodeError,
    InvalidSampleRateError,
)
from media_processor import AudioProcessor, safe_process_media


def create_mock_wav(filename: str, sample_rate: int = 44100, duration_sec: float = 0.5):
    """Генерирует корректный WAV-файл с синусоидальным звуком."""
    n_frames = int(sample_rate * duration_sec)
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)       # Моно
        wf.setsampwidth(2)       # 16 бит (2 байта)
        wf.setframerate(sample_rate)
        # Записываем тишину/сэмплы нулевой амплитуды
        data = struct.pack(f"<{n_frames}h", *([0] * n_frames))
        wf.writeframes(data)


def test_successful_processing():
    """Тест 1: Успешная загрузка и извлечение информации из WAV и MP3."""
    wav_file = "test_valid.wav"
    mp3_file = "test_valid.mp3"
    try:
        create_mock_wav(wav_file, sample_rate=48000, duration_sec=1.0)
        with open(mp3_file, "wb") as f:
            f.write(b"ID3\x03\x00\x00\x00\x00\x00#\xff\xfb\x90d" + b"\x00" * 200)

        processor = AudioProcessor()
        info_wav = processor.get_audio_info(wav_file)
        assert "48000 Гц" in info_wav
        assert "WAV" in info_wav

        res = processor.process(wav_file)
        assert res["status"] == "Success"

        info_mp3 = processor.get_audio_info(mp3_file)
        assert "MP3" in info_mp3
        print("Тест 1 (Успешная обработка WAV/MP3): УСПЕШНО")
    finally:
        for f in (wav_file, mp3_file):
            if os.path.exists(f):
                os.remove(f)


def test_file_load_error():
    """Тест 2: Попытка открыть несуществующий файл должна вызывать FileLoadError."""
    processor = AudioProcessor()
    try:
        processor.load_audio("phantom_sound.wav")
    except FileLoadError:
        print("Тест 2 (Перехват FileLoadError - несуществующий файл): УСПЕШНО")
    else:
        raise AssertionError("Ожидался FileLoadError")


def test_invalid_data_error_empty_file():
    """Тест 3: Пустой файл (0 байт) должен вызывать InvalidDataError."""
    empty_file = "empty_track.wav"
    try:
        with open(empty_file, "wb") as f:
            pass  # Пустой файл
        processor = AudioProcessor()
        processor.load_audio(empty_file)
    except InvalidDataError:
        print("Тест 3 (Перехват InvalidDataError - пустой файл): УСПЕШНО")
    else:
        raise AssertionError("Ожидался InvalidDataError")
    finally:
        if os.path.exists(empty_file):
            os.remove(empty_file)


def test_audio_decode_error_corrupted():
    """Тест 4: Файл с неверным заголовком/битыми данными вызывает AudioDecodeError."""
    corrupted_file = "broken.wav"
    try:
        with open(corrupted_file, "wb") as f:
            f.write(b"RIFF----NOT_A_REAL_WAV_BODY----")
        processor = AudioProcessor()
        processor.load_audio(corrupted_file)
    except AudioDecodeError:
        print("Тест 4 (Перехват AudioDecodeError - повреждённый заголовок): УСПЕШНО")
    else:
        raise AssertionError("Ожидался AudioDecodeError")
    finally:
        if os.path.exists(corrupted_file):
            os.remove(corrupted_file)


def test_invalid_sample_rate_error():
    """Тест 5: Нестандартная частота (например, 1234 Гц) вызывает InvalidSampleRateError."""
    bad_rate_file = "bad_rate.wav"
    try:
        # Создаём WAV с некорректной частотой
        create_mock_wav(bad_rate_file, sample_rate=1234, duration_sec=0.2)
        processor = AudioProcessor()
        processor.load_audio(bad_rate_file)
    except InvalidSampleRateError as e:
        assert e.sample_rate == 1234
        print(f"Тест 5 (Перехват InvalidSampleRateError: {e.sample_rate} Гц): УСПЕШНО")
    else:
        raise AssertionError("Ожидался InvalidSampleRateError")
    finally:
        if os.path.exists(bad_rate_file):
            os.remove(bad_rate_file)


def test_safe_pipeline():
    """Тест 6: Демонстрация безопасного конвейера safe_process_media."""
    print("\n--- Демонстрация работы safe_process_media ---")
    proc = AudioProcessor()
    safe_process_media(proc, "non_existing_file.mp3")
    print("------------------------------------------------\n")


if __name__ == "__main__":
    test_successful_processing()
    test_file_load_error()
    test_invalid_data_error_empty_file()
    test_audio_decode_error_corrupted()
    test_invalid_sample_rate_error()
    test_safe_pipeline()
    print("Все тесты лабораторной работы №2 выполнены без ошибок!")