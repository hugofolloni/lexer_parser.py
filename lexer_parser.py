import re
import numpy as np
import sys

class Lexer:
    operadores = ["\(", "\)", ":", "\+", "-", "<", ">", "<=", ">=", "==", "*", "**"]
    keywords = ["print"]
    numeros = re.compile(r"[0-9]+")
    nomes = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*")
    caracteres = re.compile(r"[+\-*/=()\[\]{};,.:<>&]")
    comentarios = re.compile(r"#[^\n]*")

    aspas = re.compile(r"\"|'")

    lista = []


    def __init__(self, path):
        text = open(path)
        linha = 0
        lista = []
        for line in text:
            l = line.strip()

            # find_hashtag = re.search("#", l)
            # if find_hashtag is not None:
            #     l = l[0: find_hashtag.span()[0]]

            l = self.find_strings(line, lista, self.aspas, linha)
            # l = find_strings(line, lista, aspas_duplas, linha)
            l = self.find_comments(line, lista, self.comentarios, linha)

            self.matcher(l, self.comentarios, "COMENTARIO", lista, linha)
            self.matcher(l, self.nomes, "NOME", lista, linha)
            self.matcher(l, self.numeros, 'NUMERO', lista, linha)
            self.matcher(l, self.caracteres, "caracteres", lista, linha)
            linha += 1

        self.lista = lista

    def find_comments(self, line, lista, regex, linha):
        col = 0
        start, end = 0, 0

        while col < len(line):
            m_start = regex.match(line, col)
            if m_start is not None:
                start = col
                col += 1
                while col < len(line):
                    col += 1
                    if regex.match(line, col) is not None:
                        break
                end = col + 1
                #lista.append([linha, col, "COMENTARIO", line[start: end]])
                line = line[0 : start] + line[end + 1:len(line)]
                col = 0
            else:
                col += 1
        return line

    def find_strings(self, line, lista, regex, linha):
        col = 0
        start, end = 0, 0
        while col < len(line):
            m_start = regex.match(line, col)
            if m_start is not None:
                if not line[col - 1] == "\\":
                    start = col
                    col += 1
                    while col < len(line):
                        if line[col] == m_start.group(0) and not line[col - 1] == "\\":
                            break
                        col += 1
                    end = col + 1
                lista.append([linha + 1, col, "STRING", line[start: end]])
                line = line[0 : start] + line[end:len(line)]
                col = 0
            else:
                col += 1
        return line

    def matcher(self, line, regex, tipagem, lista, linha):
        col = 0
        while col < len(line):
            regex_m = regex.match(line, col)
            if regex_m is not None:
                if regex_m.group(0) in self.operadores:
                    if col + 1 < len(line):
                            if line[col + 1] == "=":
                                lista.append([linha + 1, col, regex_m.group(0) + "=", ""])
                                col = col + 2
                            else:
                                lista.append([linha + 1, col, regex_m.group(0), ""])
                                col = col + len(regex_m.group(0))
                    else:
                        lista.append([linha + 1, col, regex_m.group(0), ""])
                        col = col + len(regex_m.group(0))
                elif regex_m.group(0) in  self.keywords:
                    lista.append([linha + 1, col, regex_m.group(0), ""])
                    col = col + len(regex_m.group(0))
                else:
                    if tipagem == "caracteres":
                        lista.append([linha + 1, col, regex_m.group(0), ""])

                    else:
                        lista.append([linha + 1, col, tipagem, regex_m.group(0)])
                    col = col + len(regex_m.group(0))
            else:
                col += 1


    def print_tokens(self):
        print("{:^10} | {:^10} | {:^10} | {:^10}".format("LINHA", "COLUNA", "TIPO", "VALOR"))
        print("{:^10} | {:^10} | {:^10} | {:^10}".format("----------", "---------", "---------", "---------"))
        for item in self.lista:
            print("{:^10} | {:^10} | {:^10} | {:^10}".format(item[0], item[1], item[2], item[3]))

class ExpNum:
    def __init__(self, n):
        self.tag = "exp_num"
        self.n = n
        
class ExpParenteses:
    def __init__(self, exp):
        self.tag = "exp_parenteses"
        self.exp = exp

class ExpUnario:
    def __init__(self, op, exp):
        self.tag = "exp_unario"
        self.op = op
        self.exp = exp

class ExpBin:
    def __init__(self, op, elEsq, elDir):
        self.tag = "exp_bin"
        self.op = op
        self.elEsq = elEsq
        self.elDir = elDir

class CmdPrint:
    def __init__(self, exp):
        self.tag = "PRINT"
        self.exp = exp

class CmdAtribui:
    def __init__(self, nome, exp):
      self.tag = "atribui"
      self.nome = nome
      self.exp = exp

class ExpNome:
    def __init__(self, token):
        self.tag = "NOME"
        self.token = token

class Programa:
    def __init__(self, comando):
        self.tag = "programa"
        self.comando = comando

class Parser:
  def __init__(self, tokens, calculadora):
    self.tok = tokens[0]
    self.tokens = tokens
    self.pos_prox_token = 0
    self.calculadora = calculadora
    self.atribuicoes = calculadora.atribuicoes

  def syntax_error(self, message):
      raise SyntaxError(message)

  def avanca(self):
      self.pos_prox_token += 1
      self.tok = self.tokens[self.pos_prox_token]

  def come(self, tag, tipo='p'):
      if self.tok.tag == tag:
          valor = self.tok.valor
          self.avanca()
          if tipo == 'o':
              return tag
          elif tipo == 'n':
              return ExpNum(int(valor))
          elif tipo == 'v':
              return ExpNome(valor)
          return valor
      else:
          return self.syntax_error(f"A tag {tag} não era a esperada")
    
  def monta(self):
    if self.tok.tag in ['NONE','print']:
        return self.parseCmd()
    elif self.tok.tag == '$':
        return
    else:
        return self.parseE()

  def parseCmd(self):
    if self.tok.tag == "atribui":
        x = self.come("atribui")
        self.come("=")
        exp = self.parseExp()
        return CmdAtribui
    elif self.tok.tag == "print":
        self.come("print")
        self.come("(")
        exp = self.parseE()
        self.come(")")
        return self.CmdPrint(exp)
    else:
        return self.syntax_error(f"O parseCmd não esperava a tag {self.tok.tag}")
    
  def CmdPrint(self, exp):
    return print(self.calculadora.calcula(exp))
   
  def parseE(self):
    exp = self.parseTermo()
    while True:
        if self.tok.tag == '+' or self.tok.tag == '-':
            operacao = self.come(self.tok.tag, tipo='o')
            e2 = self.parseTermo()
            exp = ExpBin(operacao, exp, e2)
        elif self.tok.tag == '$' or self.tok.tag == ')' or self.tok.tag == ';':
            return exp
        else:
            return self.syntax_error(f'O parseE não esperava a tag {self.tok.tag}')

  def parseF(self):
    if self.tok.tag == '(':
        self.come('(')
        e = self.parseE()
        self.come(')')
        return ExpParenteses(e)
    elif self.tok.tag == '-':
        self.come('-')
        f = self.parseF()
        return ExpUnario('-', f)
    else:
        if self.tok.tag == "NOME": 
            return self.come(self.tok.tag, tipo = 'v')
        elif self.tok.tag == 'NUMERO':
            return self.come(self.tok.tag, tipo = 'n')

        else:
            return self.syntax_error(f'O parseF não esperava a tag {self.tok.tag}')

  def parseTermo(self):
    t = self.parseF()
    while True:
        if self.tok.tag == '*' or self.tok.tag == '/':
            operacao = self.come(self.tok.tag, tipo='o')
            e2 = self.parseF()
            t = ExpBin(operacao, t, e2)
        elif self.tok.tag == '$' or self.tok.tag == ')' or self.tok.tag == '+' or self.tok.tag == '-' or self.tok.tag == ';':
            return t
        elif self.tok.tag == '=':
           return self.parseAtribui(t)
        else:
            return self.syntax_error(f'O parseTermo não esperava a tag {self.tok.tag}')
        
  def parseAtribui(self, t):
    while True:
        if self.tok.tag == '=':
            self.come('=')
            e = self.parseE()
            at = CmdAtribui(t, e)
        elif self.tok.tag == ';':
            self.come(';')
            self.atribuicoes.append(at)
            return self.monta()
        else:
            return self.syntax_error(f'O parseAtribui não esperava a tag {self.tok.tag}')
    
class Calculadora:
  def __init__(self):
    self.tag = "calculadora"
    self.atribuicoes = []
  
  def calcula(self, exp):
    if exp.tag == "exp_num":
        return exp.n
    elif exp.tag == "exp_unario":
        if exp.op == "-":
            return -self.calcula(exp.exp)
    elif exp.tag == "NOME":
        for i in range(len(self.atribuicoes) - 1, -1, -1):
            if self.atribuicoes[i].nome.token == exp.token:
                return self.calcula(self.atribuicoes[i].exp)
    elif exp.tag == "exp_bin":
        if exp.op == "+":
            return self.calcula(exp.elEsq) + self.calcula(exp.elDir)
        elif exp.op == "-":
            return self.calcula(exp.elEsq) - self.calcula(exp.elDir)
        elif exp.op == "*":
            return self.calcula(exp.elEsq) * self.calcula(exp.elDir)
        elif exp.op == "/":
            return self.calcula(exp.elEsq) / self.calcula(exp.elDir)
        else:
            return self.syntax_error(f"Erro no cálculo, a operação {exp.op} é inválida")
    else:
        return self.syntax_error(f"Erro no cálculo, a tag {exp.tag} é inválida")

class Token:
  def __init__(self, linha, coluna, tag, valor):
    self.linha = linha
    self.coluna = coluna
    self.tag = tag
    self.valor = valor

class Resolve:
    def __init__(self):
        tokens = []
        lexer = Lexer(sys.argv[1])
        # lexer.print_tokens()

        for item in lexer.lista:
            tokens.append(Token(item[0], item[1], item[2], item[3]))

        # print(tokens)
        tokens.sort(key=lambda x: (x.linha, x.coluna))
        tokens.append(Token(np.inf, np.inf, "$", ''))

        calculadora = Calculadora()
        parser = Parser(tokens, calculadora)
        parser.monta()

Resolve()
