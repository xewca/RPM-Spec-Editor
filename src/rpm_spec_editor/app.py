import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from rpm_spec_editor.gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)

    icon = QIcon.fromTheme("rpm-spec-editor")
    if icon.isNull():
        base_dir = Path(__file__).resolve().parent
        local_icon = base_dir / "assets" / "rpm-spec-editor.png"

        if local_icon.exists():
            icon = QIcon(str(local_icon))
    app.setWindowIcon(icon)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()