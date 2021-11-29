import queue
from queue import LifoQueue
import re

#Clase que guarda los elementos de cada declaracion (tipo, nombre, valor)
class Statement:

    def __init__(self, types, scope, value):
        self.types = types
        self.scope = scope
        self.value = value
        #En caso de que la funcion evaluada contenga parametros
        self.pharameters = []

#Clase Hashtable que guarda palabras reservadas, declaraciones
class HashTable:

    def __init__(self):
        self.stopWords = ["if", "while", "void", "string", "int", "float", "=", "==", ">", "<", "return", "{", "}"]
        self.symbolTable = {}
        self.lastFunction = []
        self.brackets = queue.Queue()
        self.errors = 0

    #Metodo que nos ayuda a leer el codigo desde los archivos .txt
    def readCode(self, codeName):
        lines = queue.Queue()
        with open(codeName, "r") as code:
            for line in code:
                lines.put(line.strip('\n'))
        line = 1
        while not lines.empty():
            self.checkStatement(lines.get(), line)
            line = line + 1
        if self.errors == 0:
            print("Código sin errores")
        else:
            print("Total de errores: ", self.errors)

    #Este metodo nos ayuda a comprobar el tipo de declaracion que se esta evaluando
    def checkStatement(self, line, num):
        if line == "":
            return True

        queue2 = queue.Queue()
        words = line.split(" ")
        self.checkSpaces(words)
        aux = ""
        for word in words:
            queue2.put(word)

        typeStatement = queue2.get()
        if self.checkStopWords(typeStatement):
            if typeStatement == "if" or typeStatement == "while":
                return self.checkConditional(typeStatement, queue2, num)
            if typeStatement == "return":
                return self.checkReturn(typeStatement, queue2, num)
            if (typeStatement == "}"):
                self.brackets.get()
                self.removeLastFunction()
                return True
            nameStatement = queue2.get()
            if not self.checkParenthesis(nameStatement):
                aux = queue2.get()
            if aux == "=":
                if len(self.lastFunction) == 0:
                    scope = "global"
                else:
                    scope = self.lastFunction.__getitem__(len(self.lastFunction) - 1)
                return self.checkVariable(nameStatement, typeStatement, scope, queue2, num)
            else:
                if self.brackets.empty():
                    return self.checkFunction(typeStatement, nameStatement, queue2, num)
                else:
                    self.errors += 1
                    print("Error en la linea: ", num, ": se espraba '}'")
                    return False

        else:
            #comprueba si hay nombre en la tabla de simbolos
            #Primero, comprueba si el nombre es correcto
            validation = False
            for letter in typeStatement:
                if letter == "(":
                    validation = True
                    break
            if validation:
                functionName = typeStatement.split(sep='(')
                nextword = functionName.pop()
                typeStatement = functionName.pop()
                return self.checkPharameters(typeStatement, nextword, queue2, num)

            if self.symbolTable.get(typeStatement) != None:
                statement = self.symbolTable[typeStatement]
                aux = queue2.get()
                if aux == "=":
                    return self.getType(statement.types) == self.getType(queue2.get())
                return True
            else:
                self.errors += 1
                print("Error en la linea: ", num, ": función no declarada")
                return False

    #Este metodo nos ayuda a detectar los caracteres que sirven como palabras reservadas
    def checkStopWords(self, word):
        for stopword in self.stopWords:
            if stopword == word:
                return True
        return False

    #Metodo que nos ayuda a detectar si una variable ha sido declarada correctamente
    def checkVariable(self, name, types, scope, queue2, num):
        if self.checkStopWords(types):
            value = queue2.get()
            if types == self.getType(value):
                self.symbolTable[name] = Statement(types, scope, value)
                validation = False
                for letter in value:
                    if letter == "(":
                        validation = True
                        break
                if validation:
                    value = value.split(sep='(')
                    possibleVariable = value.pop()
                    possibleFunction = value.pop()
                    if possibleVariable.endswith(")"):
                        possibleVariable = possibleVariable[0:len(possibleVariable) - 1]
                        if self.symbolTable.get(possibleVariable) != None and self.symbolTable.get(
                                possibleFunction) != None:
                            return True
                        else:
                            self.errors += 1
                            print("Error en la linea: ", num, ": variable no declarada")
                        return False
                    else:
                        self.errors += 1
                        print("Error en la linea: ", num, ": se esperaba ')'")
                        return False
            else:
                self.errors += 1
                print("Error en la linea: ", num, ": tipos de variables incompatibles")
                return False

        #La ultima palabra debe ser el valor
        if queue2.empty():
            return True
        #Si no, es incorrecto
        else:
            self.errors += 1
            print("Error en la linea: ", num, ": valores incorrectos")
            return False

    #Este metodo nos ayuda a detectar los parentesis
    def checkFunction(self, typeStatement, name, queue2, num):

        validation = False
        for letter in name:
            if letter == "(":
                validation = True
                break
        if validation:
            functionName = name.split(sep='(')
            variableType = functionName.pop()
            if self.checkStopWords(variableType):
                #Aca podemos cambiar de lista a string
                functionName = functionName.pop()
                # Guardamos la funcion
                functionStatement = Statement(typeStatement, "global", None)
                self.brackets.put(num)
                # Asignamos la ultima funcion
                self.lastFunction.append(functionName)
                variableName = queue2.get()
                validation = False

                if re.search(".,$", variableName):
                    variableName = variableName[:len(variableName) - 1]
                    self.symbolTable[variableName] = Statement(variableType, self.lastFunction.__getitem__(
                        len(self.lastFunction) - 1), None)
                    functionStatement.pharameters.append(variableType)
                    # Por si existen mas variables
                    flag = True
                    while flag:
                        auxTypeStatement = queue2.get()
                        if self.checkStopWords(auxTypeStatement):
                            auxNameVariable = queue2.get()
                            if re.search(".,$", auxNameVariable):
                                auxNameVariable = auxNameVariable - len(auxNameVariable - 1)
                                self.symbolTable[auxNameVariable] = Statement(auxTypeStatement,
                                                                              self.lastFunction.__getitem__(
                                                                                  len(self.lastFunction) - 1), None)
                                #Agrega el parametro al parametro de la funcion
                                functionStatement.pharameters.append(auxTypeStatement)
                            elif auxNameVariable.endswith("){"):
                                for letter in auxNameVariable:
                                    if letter == ")":
                                        validation = True
                                        break
                                if validation:
                                    auxNameVariable = auxNameVariable.split(sep=')')
                                    auxNameVariable.pop()
                                    auxNameVariable = auxNameVariable.pop()
                                    self.symbolTable[auxNameVariable] = Statement(auxTypeStatement,
                                                                                  self.lastFunction.__getitem__(
                                                                                      len(self.lastFunction) - 1), None)
                                    #Agrega el parametro al parametro de la funcion
                                    functionStatement.pharameters.append(auxTypeStatement)
                                    self.symbolTable[functionName] = functionStatement
                                    flag = False
                            else:
                                self.errors += 1
                                print("Error en la linea: ", num, ": declaración inválida")
                                return False

                elif variableName.endswith("){"):
                    for letter in variableName:
                        if letter == ")":
                            validation = True
                            break
                    if validation:
                        variableName = variableName.split(sep=')')
                        variableName.pop()
                        variableName = variableName.pop()
                        self.symbolTable[variableName] = Statement(variableType, functionName, None)
                        #Agrega el parametro al parametro de la funcion
                        functionStatement.pharameters.append(variableType)
                    self.symbolTable[functionName] = functionStatement
                    return True
                else:
                    self.errors += 1
                    print("Error en la linea: ", num, ": declaración inválida")
                    return False


            else:
                self.errors += 1
                print("Error en la linea: ", num, ": declaración inválida")
                return False

    #Detecta Parentesis abiertos o cerrados
    def checkParenthesis(self, word):
        for letter in word:
            if letter == "(" or letter == ")":
                return True
        return False

    #Detecta Espacios
    def checkSpaces(self, words):
        while True:
            if words.__getitem__(0).__eq__(""):
                words.pop(0)
            else:
                break

    #Detecta if
    def checkConditional(self, typeStatement, queue2, num):
        #Aca obtenemos los valores
        value1 = queue2.get()
        value1 = value1.split(sep='(')
        value1 = value1.pop()
        operator = queue2.get()
        value2 = queue2.get()
        value2 = value2.split(sep=')')
        value2.pop()
        value2 = value2.pop()

        # Verifica si se encuentra en la tabla de simbolos
        if self.getType(value1) == self.getType(value2):
            self.lastFunction.append("if")
            self.brackets.put(num)
            return True
        else:
            self.errors += 1
            print("Error en la linea: ", num, ": los tipos de valores no coinciden")
            return False

    #Detecta return
    def checkReturn(self, typeStatement, queue2, num):
        functionStatement = self.lastFunction.__getitem__(0)
        functionStatement = self.symbolTable[functionStatement]
        value = queue2.get()
        if self.symbolTable.get(value) != None:
            statement = self.symbolTable[value]
            if statement.types == functionStatement.types:
                return True
            else:
                self.errors += 1
                print("Error en la linea: ", num, ": valor de retorno inválido")
                return False
        else:
            return self.getType(value) == functionStatement.types
        self.errors += 1
        print("Error en la linea: ", num, ": valor de retorno inválido")
        return False

    #Detecta parametros
    def checkPharameters(self, typeStatement, nextword, queue2, num):
        statement = self.symbolTable[typeStatement]
        if len(statement.pharameters) == 0:
            if nextword == ")":
                return True
            else:
                self.errors += 1
                print("Error en la linea: ", num, ":  se esperaba ')'")
                return False
        else:
            if nextword == ")":
                self.errors += 1
                print("Error en la linea: ", num, ": se esperaba ')'")
                return False
            else:
                iterator = 0
                for value in statement.pharameters:
                    if re.search(".,$", nextword):
                        nextword = nextword[:len(nextword) - 1]
                        if self.getType(nextword) != value:
                            self.errors += 1
                            print("Error en la linea: ", num, ": los valores no coinciden")
                            return False
                        nextword = queue2.get()
                        iterator += 1
                    if nextword.endswith(")"):
                        value = statement.pharameters.__getitem__(iterator)
                        nextword = nextword[:len(nextword) - 1]
                        if self.getType(nextword) != value:
                            self.errors += 1
                            print("Error en la linea: ", num, ": los valores no coinciden")
                            return False
                return True
    #Retorna tipo de dato
    def getType(self, value):
        if self.symbolTable.get(value) != None:
            statement = self.symbolTable[value]
            return statement.types
            # encontrado
        else:
            # comprueba si es un string, int o float
            if self.isInt(value) or value == "int":
                return "int"
            elif self.isFloat(value) or value == "float":
                return "float"
            else:
                return "string"

    #Comprueba si el tipo de dato es integer
    def isInt(self, possibleInt):
        return isinstance(possibleInt, int) or possibleInt.isdigit()

    # Comprueba si el tipo de dato es float
    def isFloat(self, possibleFloat):
        try:
            if float(possibleFloat):
                return True
        except:
            return False

    # Comprueba si el tipo de dato es string
    def isString(self, possibleString):
        return type(possibleString) == str

    def removeLastFunction(self):
        if self.lastFunction.__getitem__(len(self.lastFunction) - 1) == "if" or self.lastFunction.__getitem__(
                len(self.lastFunction) - 1) == "while":
            self.lastFunction.pop()
        else:
            keys = list(self.symbolTable.keys())
            statements = list(self.symbolTable.values())
            iterator = 0

            for i in statements:
                if i.scope == self.lastFunction.__getitem__(0):
                    del self.symbolTable[keys.__getitem__(iterator)]
                iterator += 1
            self.lastFunction.pop()