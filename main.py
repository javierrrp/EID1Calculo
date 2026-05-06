import sys  
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from view.vista_principal import VistaPrincipal


app = QApplication(sys.argv) 
main_window = VistaPrincipal()
main_window.show()
sys.exit(app.exec())  