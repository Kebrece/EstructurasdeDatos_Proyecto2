# Clase cuyo objetivo es parsear las lineas de texto del archivo .txt para
# mostrarlas en pantalla y utilizar el nombre del archivo unicamente en esta clase

class Parser:
    def __init__(self):
        self.filename = "incorrecto.txt"
        self.lista = []

    def imprimirArchivo(self):
        with open(self.filename) as file_object:
            lines = file_object.readlines()
            self.lista.append(lines)
            for line in lines:
                print(line)

    def getFileName(self):
        return self.filename