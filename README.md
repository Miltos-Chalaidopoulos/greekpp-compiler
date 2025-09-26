# Greek++ Compiler

A simple **Python compiler** for fictional languege greek++ (grammar in EBNF format included in **grammar.txt** ) created for university cousrse "**Compilers**"

The compiler should : 

1. Read '.gr' a source file and break it down to tokens 
2. Perform sysntax analysis and spot syntax errors
3. Generate intermediate code 
4. Build symbol table 
5. Output final code in **Risk V assembly**

## Source Code stracture

- state.py : global variables
- lexer.py : Lexical analysis
- parser.py : Creation of syntax tree
- intermediate.py : Functions used for generating intermediate code quads
- symboltable.py : Functions used for generating the symbol table
- assembly.py : Risk V final code gneration
- main.py : Compiler entry point

## Additional files

- grammar.txt : grammar of greek++
- examples/ : example programms in greek++
- report.pdf : Final project report 

## Compiling a program

Using a '.gr' file 
``` bash
python3 main.py fileName
```
Produces: 
- .int file for intermediate code 
- .asm file for final code
- symbol table in terminal
