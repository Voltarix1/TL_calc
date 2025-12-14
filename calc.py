#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Projet TL : parser - requires Python version >= 3.10
"""

import sys
from math import factorial, pow
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
def parse_exp0(l):
    if get_current() == V_T.NUM:
        n = consume_token(V_T.NUM)
        return n
    elif get_current() == V_T.CALC:
        i = consume_token(V_T.CALC)
        return l[i-1]
    else:
        consume_token(V_T.OPAR)
        n = parse_exp5(l)
        consume_token(V_T.CPAR)
        return n

# exp1 -> exp0 exp1'
def parse_exp1(l):
    n1 = parse_exp0(l)
    n = parse_exp1p(l, n1)
    return n

# exp1' -> POW exp1 | e
def parse_exp1p(l, n1):
    if get_current() == V_T.POW:
        consume_token(V_T.POW)
        n2 = parse_exp1(l)
        return pow(n1, n2)
    return n1

# exp2 -> exp1 Y1
def parse_exp2(l):
    n1 = parse_exp1(l)
    n = parse_Y1(l, n1)
    return n

# Y1 -> FACT Y1 | e
def parse_Y1(l, n1):
    n = n1 #par défaut
    if get_current() == V_T.FACT:
        consume_token(V_T.FACT)
        n = parse_Y1(l, factorial(n1))
    return n

# exp3 -> SUB exp3 | exp2
def parse_exp3(l):
    if get_current() == V_T.SUB:
        consume_token(V_T.SUB)
        n0 = parse_exp3(l)
        return -n0
    else:
        n = parse_exp2(l)
        return n

# exp4 -> exp3 Y2
def parse_exp4(l):
    n1 = parse_exp3(l)
    n = parse_Y2(l, n1)
    return n

# Y2 -> exp4' Y2 | e
# exp4' -> MUL exp3 | DIV exp3
def parse_Y2(l, n1):
    n = n1 #par défaut
    if get_current() in [V_T.MUL, V_T.DIV]:
        if get_current() == V_T.MUL:
            consume_token(V_T.MUL)
            n2 = parse_exp3(l)
            n = parse_Y2(l, n1*n2)
        else:
            consume_token(V_T.DIV)
            n2 = parse_exp3(l)
            n = parse_Y2(l, n1/n2)
    return n

# exo5 -> exp4 Y3
def parse_exp5(l):
    n1 = parse_exp4(l)
    n = parse_Y3(l, n1)
    return n

# Y3 -> exp5' Y3 | e
# exp5' -> ADD exp4 | SUB exp4
def parse_Y3(l, n1):
    n = n1 #par défaut
    if get_current() in [V_T.ADD, V_T.SUB]:
        if get_current() == V_T.ADD:
            consume_token(V_T.ADD)
            n2 = parse_exp4(l)
            n = parse_Y3(l, n1+n2)
        else:
            consume_token(V_T.SUB)
            n2 = parse_exp4(l)
            n = parse_Y3(l, n1-n2)
    return n

def parse_input(l0):
    l = l0 #par défaut
    if get_current() in [V_T.NUM, V_T.CALC, V_T.OPAR, V_T.SUB]:
        n = parse_exp5(l0)
        consume_token(V_T.SEQ)
        l = parse_input(l0 + [n])
    return l


#####################################
## Fonction principale de la calculatrice
## Appelle l'analyseur grammatical et retourne
## - None sans les attributs
## - la liste des valeurs des calculs avec les attributs

def parse(stream=sys.stdin):
    init_parser(stream)
    l = parse_input([])
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
