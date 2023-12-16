# Parser para Python
Nesse programa, implementamos uma calculadora simples para Python usando a seguinte gramática:

```
P -> CP | ε
C -> NOME = E | print(E)
E -> +EE | -EE | *EE | /EE | NOME | NUM | (E)

```

Matéria: Linguagens Formais e Autômatos

Professor 👨🏻‍🏫: Hugo M.G

Alunos 👨🏾‍🎓👨🏻‍🎓: Gabriel Vieira do Amaral e Hugo Folloni Guarilha

### Como executar o programa
```
python lexer_parser.py <arquivo>.txt
```

### Exemplo de arquivo
```
y = 25 - 5 * (10 - 2); 
x = 2 - 1; 
x = 2  + 3; 
print(4 + x);

# Cálculo do determinante de Bhaskara
a = 5; b = 20; c = 15;
print(b*b - 4*a*c);
# E uma conta com os outros operadores
d = a + b + c;
print(-1/d);
```
Note que é necessário o uso da ";". Por favor não se esqueça disso!
```
amaral@DESKTOP-FAILL34:~/lexer_parser.py$ python3 lexer_parser.py arquivo.txt
9
100
-0.025
```


