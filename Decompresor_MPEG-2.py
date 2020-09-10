#!/usr/bin/python

import os
import numpy as np
from bitstring import Bits, BitArray, BitStream, ConstBitStream

# BitArray -> Lectura/Escritura
# ConstBitStream -> Lectura

                # ANCHOR Constantes Globales

# Fotogramas
FOTOGRAMAS = 2

# Blanking
BLANKING = '10000000000001000000' # 020 + 040  quitando los '00' al principio

# Preámbulo fijo
P_F = '1111111111000000000000000000001' # Se quita el '00 del principio

# Protection Bits
d={
# FVH  P3P2P1P0
 '000':'0000',
 '001':'1101',
 '010':'1011',
 '011':'0110',
 '100':'0111',
 '101':'1010',
 '110':'1100',
 '111':'0001'}

                # ANCHOR Variables Globales

# Lectura en disco
fh_read = open('video.yuv', 'rb')      # Lectura .yuv
bs_read = ConstBitStream(fh_read)        # Lectura tipo ConstBitStream

# Escritura en disco
fh_write = open('video.sdi', 'wb')

# Escritura general en Memoria
bs_write = BitArray()

                # ANCHOR Fotograma

for i in range(FOTOGRAMAS):

    # Variables de fotograma
    Y = []
    CR = []
    CB = []

                #   ANCHOR  Lectura Disco

    # Lectura Y
    for j in range(414720):         # 720 palabras x 576 columnas

        buffer = bs_read.read('bin:8')
        Y.append(buffer)

    # Lectura CR
    for j in range(103680):     # 360 palabras x 288 columnas

        buffer = bs_read.read('bin:8')
        CR.append(buffer)

    # Lectura CB
    for j in range(103680):     # 360 palabras x 288 columnas

        buffer = bs_read.read('bin:8')
        CB.append(buffer)

                #   ANCHOR   bs_write Escritura memoria
             
    # ANCHOR  1-22 Sincronismo
    for j in range(22):

        # EAV -> 40 bits
        F = '0'  
        V = '1'
        H = '1'
        buffer = P_F + F + V + H + d[F + V + H] + '00' # eav/sav
        bs_write.append('0b' + buffer)

        # Blanking 1
        for o in range(140):    # 280 palabras -> 2800 bits, 2800/20 = 140
            bs_write.append('0b' + BLANKING)

        # SAV -> 40 bits
        F = '0'
        V = '1'
        H = '0'
        buffer = P_F + F + V + H + d[F + V + H] + '00' # eav/sav
        bs_write.append('0b' + buffer)

        # Blanking 2
        for o in range(720):    # 1440 palabras -> 14400 bits, 14400/20 = 720
            bs_write.append('0b' + BLANKING)
       
        # 40 + 2800 + 40 + 14400 = 17280 bits


    # ANCHOR 23 - 310 Campo 1

    Y_impares = 0
    pos_C1 = 0

    for j in range(288):
        
        # EAV
        F = '0'
        V = '0'
        H = '1'
        buffer = P_F + F + V + H + d[F + V + H] + '00' # eav/sav
        bs_write.append('0b' + buffer)

        # Blanking
        for a in range(140):    # 2800 bits (280 palabras), 2800/20 = 140
            bs_write.append('0b' + BLANKING)

        # SAV
        F = '0'
        V = '0'
        H = '0'
        buffer = P_F + F + V + H + d[F + V + H] + '00' # eav/sav
        bs_write.append('0b' + buffer)

        # Escritura activa
        for k in range(720):    # 1440 palabras

            if((k % 2) == 0):       # Palabras 'impares'

                # CR
                buffer = CR[pos_C1]
                bs_write.append('0b' + buffer + '00')

                # Y
                buffer = Y[720 * Y_impares + k]
                bs_write.append('0b' + buffer + '00')

                # CB
                buffer = CB[pos_C1]
                bs_write.append('0b' + buffer + '00')

                pos_C1 += 1     # Incremento de pos_C1 solo cuando se use

            else:       # Palabras 'pares'

                buffer = Y[720 * Y_impares + k]
                bs_write.append('0b' + buffer + '00')

        Y_impares += 2      # Incremento de Y_impares

                
    # ANCHOR 311 - 335 Sincronismo

    for j in range(25):

        # EAV
        F = '1' 
        V = '1'
        H = '1'
        buffer = P_F + F + V + H + d[F + V + H] + '00' # eav/sav
        bs_write.append('0b' + buffer)

        # Blanking
        for o in range(140):
            bs_write.append('0b' + BLANKING)

        # SAV
        F = '0'
        V = '1'
        H = '0'
        buffer = P_F + F + V + H + d[F + V + H] + '00' # eav/sav
        bs_write.append('0b' + buffer)

        # Blanking
        for o in range(720):
            bs_write.append('0b' + BLANKING)


    # Escritura activa

    Y_pares = 1
    pos_C2 = 0

    # ANCHOR 336 - 623 Campo 2 

    for j in range(288):
    
        # EAV
        F = '1'
        V = '0'
        H = '1'
        buffer = P_F + F + V + H + d[F + V + H] + '00' # eav/sav
        bs_write.append('0b' + buffer)

        # Blanking
        for a in range(140):
            bs_write.append('0b' + BLANKING)

        # SAV
        F = '1'
        V = '0'
        H = '0'
        buffer = P_F + F + V + H + d[F + V + H] + '00' # eav/sav
        bs_write.append('0b' + buffer)

        # Escritura activa
        for k in range(720):

            if((k % 2) == 0):       # Palabras 'impares'

                # CR
                buffer = CR[pos_C2]
                bs_write.append('0b' + buffer + '00')

                # Y
                buffer = Y[720 * Y_pares + k]
                bs_write.append('0b' + buffer + '00')

                # CB
                buffer = CB[pos_C2]
                bs_write.append('0b' + buffer + '00')

                pos_C2 += 1     # Incremento de pos_C2 solo cuando se use

            else:       # Palabras 'pares

                buffer = Y[720 * Y_pares + k]
                bs_write.append('0b' + buffer + '00')

        Y_pares += 2      # Incremento de Y_pares

    # ANCHOR 624 - 625 Sincronismo

    for j in range(2):
        
        # EAV
        F = '1'
        V = '1'
        H = '1'
        buffer = P_F + F + V + H + d[F + V + H] + '00' # eav/sav
        bs_write.append('0b' + buffer)

        # Blanking
        for o in range(140): 
            bs_write.append('0b' + BLANKING)

        # SAV
        F = '1'
        V = '1'
        H = '0'
        buffer = P_F + F + V + H + d[F + V + H] + '00' # eav/sav
        bs_write.append('0b' + buffer)
        for o in range(720):
            bs_write.append('0b' + BLANKING)

# ANCHOR Volcamos datos en el video.sdi
bs_write.tofile(fh_write)
