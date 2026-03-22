from pathlib import Path
from datetime import datetime
import shutil


class FileAccessError(RuntimeError):
    """ Ошибка доступа или работы с файлом спецификации RPM. """
    pass


class FileManager:

    BACKUP_SUFFIX = ".bak"

    def open_file(self, path: str):
        file_path = Path(path)

        if not file_path.exists():
            raise FileAccessError(f"Исключение: файл не существует: {file_path}.")

        if not file_path.is_file():
            raise FileAccessError(f"Исключение: указанный путь не является файлом: {file_path}.")

        if not file_path.suffix == ".spec":
            raise FileAccessError(f"Исключение: открывать только файлы с расширением \".spec\" {file_path}.")

        try:
            return file_path.read_text(encoding="utf-8")
        except PermissionError as exc:
            raise FileAccessError("Исключение: недостаточно прав для чтения файлов.") from exc
        except OSError as exc:
            raise FileAccessError("Исключение: ошибка чтения файла.") from exc


    def save_file(self, path: str, content: str) -> None:
        file_path = Path(path)

        if file_path.exists():
            self.create_backup(file_path)

        try:
            file_path.write_text(content, encoding="utf-8")
        except PermissionError as exc:
            raise FileAccessError("Исключение: недостаточно прав для записи файла.") from exc
        except OSError as exc:
            raise FileAccessError("Исключение: ошибка при сохранении файла.") from exc


    def create_backup(self, file_path: Path) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = file_path.with_suffix(
            f"{file_path.suffix}.{timestamp}{self.BACKUP_SUFFIX}"
        )

        try:
            shutil.copy2(file_path, backup_path)
        except PermissionError as exc:
            raise FileAccessError("Исключение: недостаточно прав для создания резервной копии.") from exc
        except OSError as exc:
            raise FileAccessError("Исключение: ошибка при создании резервной копии.") from exc

        return backup_path


    def restore_last_backup(self, path: str) -> None:
        file_path = Path(path)
        directory = file_path.parent

        backups = sorted(
            directory.glob(f"{file_path.name}.*{self.BACKUP_SUFFIX}"),
            reverse=True
        )

        if not backups:
            raise FileAccessError("Исключение: резервные копии не найдены.")

        last_backup = backups[0]

        try:
            shutil.copy2(last_backup, file_path)
        except PermissionError as exc:
            raise FileAccessError("Исключение: недостаточно прав для файла.") from exc
        except OSError as exc:
            raise FileAccessError("Исключение: ошбика при восстановлении файла.") from exc
