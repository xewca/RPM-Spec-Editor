from PyQt5.QtCore import (
    QObject,
    pyqtSignal
)


class BuildWorker(QObject):
    finished = pyqtSignal(object)
    failed = pyqtSignal(str)

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    def run(self):
        try:
            result = (self.controller.build_current())
            self.finished.emit(result)

        except Exception as exc:
            self.failed.emit(str(exc))