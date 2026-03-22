from src.rpm_spec_editor.storage.file_manager import FileManager

fm = FileManager()
print("FileManager загружен:", fm)

content = fm.open_file("./test.spec")
fm.save_file("test.spec", content + "\n# test")
fm.restore_last_backup("test.spec")