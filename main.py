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

#Referencias:
#Singh, Ravendra, Vivek Sharma, and Manish Varshney. Design and Implementation of Compiler. Daryaganj: New Age International, 2009. Web.
#Capítulo 5  (Este recurso lo consiguen en el catálogo del SIDUNA)

#Drozdek, A. (2013). Data Structures and algorithms in C++. Cengage Learning.
#Sección 12.5: Caso de Estudio (Dentro del folder de libros compartidos)
