# main.py
import sys
from PyQt6.QtWidgets import QApplication
from controllers.controlador_principal import ControladorPrincipal

if __name__ == "__main__": 
    app = QApplication(sys.argv)
    
    # Instanciamos el controlador que orquesta todo
    iniciador = ControladorPrincipal()
    
    sys.exit(app.exec())