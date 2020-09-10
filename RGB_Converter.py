#!/usr/bin/python

import os
import numpy as np
from bitstring import Bits, BitArray, BitStream, ConstBitStream
from PIL import Image

                # ANCHOR Constantes Globales

# Image
data = np.zeros((576, 720, 3), dtype=np.uint8) # Image dimensions

# Fotogramas
FOTOGRAMAS = 1      # Lo dejamos a 1 para que el tiempo de ejecución no sea tan elevado

                # ANCHOR Variables Globales

# Lectura en disco
fh_read = open('video.yuv', 'rb')      # Lectura .yuv
bs_read = ConstBitStream(fh_read)        # Lectura tipo ConstBitStream

                # ANCHOR Fotograma

for i in range(FOTOGRAMAS):

    # Variables de fotograma

    # En estas listas almacenaremos lo que leamos del fichero.yuv
    Y = []
    CR = []
    CB = []

                #   ANCHOR  Lectura Disco

    # Lectura Y
    for j in range(414720):         # 720 palabras x 576 columnas

        buffer = bs_read.read('uint:8')
        Y.append(buffer)

    # Lectura CB
    for j in range(103680):     # 360 palabras x 288 columnas

        buffer = bs_read.read('uint:8')
        CB.append(buffer)

    # Lectura CR
    for j in range(103680):     # 360 palabras x 288 columnas

        buffer = bs_read.read('uint:8')
        CR.append(buffer)


                # ANCHOR RGB Construcción

    # pos CB, CR
    pos_c = 0
    pos_aux = 0

    for i in range(576):        # Filas
        pos_aux = pos_c
        for j in range(720):        # Columnas
            if(j % 2 == 0):

                # CR
                CR_aux = CR[pos_c]

                # CB
                CB_aux = CB[pos_c]

                pos_c += 1      # Solo se incrementa en caso de que la muestra sea par para así reciclar las crominancias cada 2 muestras
                

            # Y
            Y_aux = Y[720 * i + j]

                # ANCHOR Cálculos
                # Según la normativa de la ITU-R 601, puntos 2.5.1 2.5.2 y 2.5.3 mayoritariamente

            Ey = (Y_aux - 16)/219
            Ecb = (CB_aux - 128)/224
            Ecr = (CR_aux - 128)/224

            R = (1.4025*Ecr + Ey)       #TODO

            B = (1.773*Ecb + Ey)

            G = ((Ey - 0.3*R-0.11*B)/0.59)

            # Procedemos con la desnormalización

            R = R*255
            G = G*255
            B = B*255

                # ANCHOR Saturación

            if(R > 255):
                R = 255
            elif(R < 0):
                R = 0
            if(G > 255):
                G = 255
            elif(G < 0):
                G = 0
            if(B > 255):
                B = 255
            elif(B < 0):
                B = 0

            data[i, j] = [R, G, B]  # Asignación de datos

        if(i % 2 == 0):     # Si estamos en una línea par el contador de las crominancias 
                            # vuelve a su posición de antes de empezar la línea
                            # Así reciclamos las crominancias cada 2 líneas
            pos_c = pos_aux
        
                # ANCHOR RGB Por pantalla

    img = Image.fromarray(data, 'RGB')
    img.save('sample.png')
    img.show() 
