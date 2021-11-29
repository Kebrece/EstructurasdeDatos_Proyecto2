#Integrantes:
#Diego Quiros Brenes
#Kevin Brenes Cerdas
#Jairo Ulloa Rodriguez
import hashTable
import Parser

parser = Parser.Parser()
parser.imprimirArchivo()
table = hashTable.HashTable()
table.readCode(parser.getFileName())


