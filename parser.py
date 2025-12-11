#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Projet TL : parser - requires Python version >= 3.10
"""

import sys
from math import factorial
assert sys.version_info >= (3, 10), "Use Python 3.10 or newer !"

import lexer
from definitions import V_T, str_attr_token

#####
# Variables internes (à ne pas utiliser directement)

_current_token = V_T.END
_value = None  # attribut du token renvoyé par le lexer

#####
# Fonctions génériques

class ParserError(Exception):
    pass

def unexpected_token(expected):
    return ParserError("Found token '" + str_attr_token(_current_token, _value) + "' but expected " + expected)

def get_current():
    return _current_token

def init_parser(stream):
    global _current_token, _value
    lexer.reinit(stream)
    _current_token, _value = lexer.next_token()
    # print("@ init parser on",  repr(str_attr_token(_current, _value)))  # for DEBUGGING

def consume_token(tok):
    # Vérifie que le prochain token est tok ;
    # si oui, le consomme et renvoie son attribut ; si non, lève une exception
    global _current_token, _value
    if _current_token != tok:
        raise unexpected_token(tok.name)
    if _current_token != V_T.END:
        old = _value
        _current_token, _value = lexer.next_token()
        return old

#########################
## Parsing de input et exp

# exp0 -> NUM | CALC | OPAR exp5 CPAR
def parse_exp0():
    if get_current() == V_T.NUM:
        consume_token(V_T.NUM)
    elif get_current() == V_T.CALC:
        consume_token(V_T.CALC)
    else:
        consume_token(V_T.OPAR)
        parse_exp5()
        consume_token(V_T.CPAR)

# exp1 -> exp0 exp1'
def parse_exp1():
    parse_exp0()
    parse_exp1p()

# exp1' -> POW exp1 | e
def parse_exp1p():
    if get_current() == V_T.POW:
        consume_token(V_T.POW)
        parse_exp1()

# exp2 -> exp1 Y1
def parse_exp2():
    parse_exp1()
    parse_Y1()

# Y1 -> FACT Y1 | e
def parse_Y1():
    if get_current() == V_T.FACT:
        consume_token(V_T.FACT)
        parse_Y1()

# exp3 -> SUB exp3 | exp2
def parse_exp3():
    if get_current() == V_T.SUB:
        consume_token(V_T.SUB)
        parse_exp3()
    else:
        parse_exp2()

# exp4 -> exp3 Y2
def parse_exp4():
    parse_exp3()
    parse_Y2()

# Y2 -> exp4' Y2 | e
def parse_Y2():
    if get_current() in [V_T.MUL, V_T.DIV]:
        parse_exp4p()
        parse_Y2()

# exp4' -> MUL exp3 | DIV exp3
def parse_exp4p():
    if get_current() == V_T.MUL:
        consume_token(V_T.MUL)
        parse_exp3()
    else:
        consume_token(V_T.DIV)
        parse_exp3()

# exo5 -> exp4 Y3
def parse_exp5():
    parse_exp4()
    parse_Y3()
    

# Y3 -> exp5' Y3 | e
def parse_Y3():
    if get_current() in [V_T.ADD, V_T.SUB]:
        parse_exp5p()
        parse_Y3()

# exp5' -> ADD exp4 | SUB exp4
def parse_exp5p():
    if get_current() == V_T.ADD:
        consume_token(V_T.ADD)
        parse_exp4()
    else:
        consume_token(V_T.SUB)
        parse_exp4()

def parse_input():
    if get_current() in [V_T.NUM, V_T.CALC, V_T.OPAR, V_T.SUB]:
        parse_exp5()
        consume_token(V_T.SEQ)
        parse_input()
    return


#####################################
## Fonction principale de la calculatrice
## Appelle l'analyseur grammatical et retourne
## - None sans les attributs
## - la liste des valeurs des calculs avec les attributs

def parse(stream=sys.stdin):
    init_parser(stream)
    l = parse_input()
    consume_token(V_T.END)
    return l

#####################################
## Test depuis la ligne de commande

if __name__ == "__main__":
    print("@ Testing the calculator in infix syntax.")
    result = parse()
    if result is None:
        print("@ Input OK ")
    else:
        print("@ result = ", repr(result))
