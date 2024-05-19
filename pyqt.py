import sys
from PyQt5.QtWidgets import QApplication
from display.app_window import AppWindow

def main():
    app = QApplication(sys.argv)
    ex = AppWindow()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
