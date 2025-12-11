#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Projet TL : lexer de la calculatrice
"""

import sys
import enum
import definitions as defs


# Pour lever une erreur, utiliser: raise LexerError("message décrivant l'erreur dans le lexer")
class LexerError(Exception):
    pass


#################################
# Variables et fonctions internes (privées)

# Variables privées : les trois prochains caractères de l'entrée
current_char1 = ''
current_char2 = ''
current_char3 = ''

# Initialisation: on vérifie que EOI n'est pas dans V_C et on initialise les prochains caractères
def init_char():
    global current_char1, current_char2, current_char3
    # Vérification de cohérence: EOI n'est pas dans V_C ni dans SEP
    if defs.EOI in defs.V_C:
        raise LexerError('character ' + repr(defs.EOI) + ' in V_C')
    defs.SEP = {' ', '\n', '\t'} - set(defs.EOI)
    defs.V = set(tuple(defs.V_C) + (defs.EOI,) + tuple(defs.SEP))
    current_char1 = defs.INPUT_STREAM.read(1)
    # print("@", repr(current_char1))  # decomment this line may help debugging
    if current_char1 not in defs.V:
        raise LexerError('Character ' + repr(current_char1) + ' unsupported')
    if current_char1 == defs.EOI:
        current_char2 = defs.EOI
        current_char3 = defs.EOI
    else:
        current_char2 = defs.INPUT_STREAM.read(1)
        # print("@", repr(current_char2))  # decomment this line may help debugging
        if current_char2 not in defs.V:
            raise LexerError('Character ' + repr(current_char2) + ' unsupported')
        if current_char2 == defs.EOI:
            current_char3 = defs.EOI
        else:
            current_char3 = defs.INPUT_STREAM.read(1)
            # print("@", repr(current_char3))  # decomment this line may help debugging
            if current_char3 not in defs.V:
                raise LexerError('Character ' + repr(current_char3) + ' unsupported')

    return

# Accès aux caractères de prévision
def peek_char3():
    global current_char1, current_char2, current_char3
    return (current_char1 + current_char2 + current_char3)

def peek_char1():
    global current_char1
    return current_char1

# Avancée d'un caractère dans l'entrée
def consume_char():
    global current_char1, current_char2, current_char3
    if current_char2 == defs.EOI: # pour ne pas lire au delà du dernier caractère
        current_char1 = defs.EOI
        return
    if current_char3 == defs.EOI: # pour ne pas lire au delà du dernier caractère
        current_char1 = current_char2
        current_char2 = defs.EOI
        return
    next_char = defs.INPUT_STREAM.read(1)
    #print("@", repr(next_char))  # decommenting this line may help debugging
    if next_char in defs.V:
        current_char1 = current_char2
        current_char2 = current_char3
        current_char3 = next_char
        return
    raise LexerError('Character ' + repr(next_char) + ' unsupported')

# Finit entièrement la lecture de l'input
def consume_input():
    next_char = peek_char1()
    while next_char != defs.EOI:
        consume_char()
        next_char = peek_char1()
    consume_char()

def expected_digit_error(char):
    return LexerError('Expected a digit, but found ' + repr(char))

def unknown_token_error(char):
    return LexerError('Unknown start of token ' + repr(char))

# Initialisation de l'entrée
def reinit(stream=sys.stdin):
    global input_stream, current_char1, current_char2, current_char3
    assert stream.readable()
    defs.INPUT_STREAM = stream
    current_char1 = ''
    current_char2 = ''
    current_char3 = ''
    init_char()


#################################
## Automates pour les entiers et les flottants


def read_INT_to_EOI():
    next_char = peek_char1()
    if next_char == defs.EOI:
        return False

    while next_char != defs.EOI:
        if next_char not in defs.DIGITS:
            # On sait que l'entrée n'est pas reconnue par l'automate
            # On finit tout de même la lecture
            consume_input()
            return False

        if next_char in defs.DIGITS:
            consume_char()
            next_char = peek_char1()

    return True
    


def read_FLOAT_to_EOI():
    def state_0():
        next_char = peek_char1()
        if next_char in defs.DIGITS:
            consume_char()
            return state_2()
        elif next_char == '.':
            consume_char()
            return state_1()
        
        if next_char == defs.EOI:
            return False
        
        consume_input()
        return False
    
    def state_1():
        next_char = peek_char1()
        if next_char in defs.DIGITS:
            consume_char()
            return state_3()
        
        if next_char == defs.EOI:
            return False
        
        consume_input()
        return False
    
    def state_2():
        next_char = peek_char1()
        if next_char in defs.DIGITS:
            consume_char()
            return state_2()
        elif next_char == '.':
            consume_char()
            return state_3()
        
        if next_char == defs.EOI:
            return False
        
        consume_input()
        return False
    
    def state_3():
        next_char = peek_char1()
        if next_char in defs.DIGITS:
            consume_char()
            return state_3()
        
        if next_char == defs.EOI:
            return True
        
        consume_input()
        return False
    
    return state_0()


#################################
## Lecture de l'entrée: entiers, nombres, tokens


# Lecture d'un chiffre, puis avancée et renvoi de sa valeur
def read_digit():
    current_char = peek_char1()
    if current_char not in defs.DIGITS:
        raise expected_digit_error(current_char)
    value = eval(current_char)
    consume_char()
    return value


# Lecture d'un entier en renvoyant sa valeur
def read_INT():
    entier_lu = 0
    first_char_ok = False
    while peek_char1() != defs.EOI:
        try:
            entier_lu = 10*entier_lu + read_digit()
            first_char_ok = True
        except:
            break

    if not first_char_ok:
        return None
    
    return entier_lu


global int_value
global exp_value
global sign_value

# Lecture d'un nombre en renvoyant sa valeur
def read_NUM():
    # Lecture de la partie entière
    next_char = peek_char1()
    if next_char in defs.DIGITS :
        int_value = read_INT()
    elif next_char == '.' and peek_char3()[1] in defs.DIGITS:
        int_value = 0
    else:
        return None

    # Lecture de la partie décimale
    if peek_char1() == '.':
        nextnext_char = peek_char3()[1]
        consume_char()
        if nextnext_char in defs.DIGITS:
            flottant = read_INT()
            int_value += flottant * (10 ** -len(str(flottant)))

    # Lecture de l'exposant
    if peek_char1() in ['e', 'E']:
        _, ch2, ch3 = peek_char3() 
        
        # On vérifie que l'exposant est bon
        exp = ch2 in defs.DIGITS
        exp_signe = ch2 in ['+', '-'] and ch3 in defs.DIGITS
        
        if exp or exp_signe:
            consume_char() # on saute le 'e'
            
            sign_value = 1
            if peek_char1() == '-':
                consume_char()
                sign_value = -1
            elif peek_char1() == '+':
                consume_char()
            
            exp_value = read_INT()
            int_value *= 10 ** (exp_value * sign_value)

    return int_value


# Parse un lexème (sans séparateurs) de l'entrée et renvoie son token.
# Cela consomme tous les caractères du lexème lu.
def read_token_after_separators():
    next_char = peek_char1()
    if next_char == '#':
        consume_char()
        return (defs.V_T.CALC, read_INT())
    
    if next_char in (defs.DIGITS | {'.'}):
        return (defs.V_T.NUM, read_NUM())
    
    if next_char in defs.TOKEN_MAP.keys():
        consume_char()
        return(defs.TOKEN_MAP[next_char], None)
    
    return (defs.V_T.END, None) # par défaut, on renvoie la fin de l'entrée


# Donne le prochain token de l'entrée, en sautant les séparateurs éventuels en tête
# et en consommant les caractères du lexème reconnu.
def next_token():
    next_char = peek_char1()
    while next_char in defs.SEP:
        consume_char()
        next_char = peek_char1()

    return read_token_after_separators()


#################################
## Fonctions de tests

def test_INT_to_EOI():
    print("@ Testing read_INT_to_EOI. Type a word to recognize.")
    reinit()
    if read_INT_to_EOI():
        print("Recognized")
    else:
        print("Not recognized")

def test_FLOAT_to_EOI():
    print("@ Testing read_FLOAT_to_EOI. Type a word to recognize.")
    reinit()
    if read_FLOAT_to_EOI():
        print("Recognized")
    else:
        print("Not recognized")

def test_lexer():
    print("@ Testing the lexer. Just type tokens and separators on one line")
    reinit()
    token, value = next_token()
    while token != defs.V_T.END:
        print("@", defs.str_attr_token(token, value))
        token, value = next_token()

if __name__ == "__main__":
    ## Choisir une seule ligne à décommenter
    # test_INT_to_EOI()
    # test_FLOAT_to_EOI()
    test_lexer()
