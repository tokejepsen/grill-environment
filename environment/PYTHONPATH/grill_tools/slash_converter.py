import contextlib
import sys
import functools

import pyperclip
from Qt import QtWidgets


@contextlib.contextmanager
def application():
    app = QtWidgets.QApplication.instance()

    if not app:
        print("Starting new QApplication..")
        app = QtWidgets.QApplication(sys.argv)
        yield app
        app.exec_()
    else:
        print("Using existing QApplication..")
        yield app


class Window(QtWidgets.QWidget):

    def __init__(self):
        super(Window, self).__init__()

        path = pyperclip.paste()
        forward_slash = path.replace("\\", "/")
        backward_slash = path.replace("/", "\\")

        self.setWindowTitle("Slash Converter")
        self.resize(500, 100)

        layout = QtWidgets.QVBoxLayout(self)

        button = QtWidgets.QPushButton(backward_slash)
        layout.addWidget(button)
        button.clicked.connect(functools.partial(self.copy, backward_slash))

        button = QtWidgets.QPushButton(forward_slash)
        layout.addWidget(button)
        button.clicked.connect(functools.partial(self.copy, forward_slash))

    def copy(self, text):
        pyperclip.copy(text)
        self.close()


def show():
    with application():
        win = Window()
        win.show()


def _toggle():

    path = pyperclip.paste()

    if "\\" in path:
        return path.replace("\\", "/")

    if "/" in path:
        return path.replace("/", "\\")


def toggle():
    path = _toggle()
    print "\"{0}\" copied to clipboard.".format(path)
    pyperclip.copy(path)


if __name__ == "__main__":
    show()
