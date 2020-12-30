import pygame
import numpy as np
import time
import random as r
pygame.init()
# dimensiones de la pantalla
width, height = 600, 600
DIAS=0
screen = pygame.display.set_mode((height, width))

# color del fondo
bg = 0, 0, 0
# Establecer color
screen.fill(bg)

nxC, nyC = 70, 70

dimCW = width / nxC
dimCH = height / nyC


#! estado de las celdas;
# ESTADOS:

# ? ENFERMO = 1
# ? VIVO = 0
# ? MUERTO = 2
# ? CURADO = 3

# estados 
estados={
    "vivo" : 0,
    "enfermo":1,
    "muerto":2,
    "curado":3
}

# seccion al rededores

switcher = {
        0: [-1,-1], 
        1: [0,-1],
        2: [1,-1], 
        3: [-1,0], 
        4: [1,0], 
        5: [-1,1], 
        6: [0,1], 
        7: [-1,1]  
    }


efectos={
    "muerte":0.06, # probabilidad de morir inicial
    "sana_inicial":7,  #dia en que empieza a curarse
    "contagio":15, #perido por el cual se puede contagiar
    "muerte_inicial":16, # dia desde que se calcula empiezan a morir el infectado
    "taza_infeccion":2 # numero de infectados nuevos que se porducen por turno (entero)
}

# WALKRANDOM movimiento aletorio del infectado
# y suma de nuevos infectados adyacentes dado por limit 

def infectado_mov(limit=2):
    choices= np.random.choice(8, limit, replace=False)
    infecta =[]
    for choice in choices:
        infecta.append(switcher.get(choice))
    return infecta




# estado del juego
gameState = np.zeros((nxC, nyC))

# tiempo de variables
gameTimes = np.zeros((nxC, nyC))

# inicio de infectado posicion de 1 infectado
gameState[round(nxC/2), round(nyC/2)] = 1

pauseExect = False

while True:

    newGameState = np.copy(gameState)

    screen.fill(bg)
    time.sleep(0.2)             #velocidad del juego

    ev = pygame.event.get()
    for event in ev:
        if event.type == pygame.KEYDOWN:            # pause del juego
            pauseExect = not pauseExect
            if event.key == pygame.K_r:             # la tecla r resetea el juego
                DIAS=0
                gameState = np.zeros((nxC, nyC))
                gameTimes = np.zeros((nxC, nyC))
                newGameState = np.copy(gameState)
# tiempo de variables


        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        
        

        mouseClick = pygame.mouse.get_pressed()

        if sum(mouseClick) > 0:

            posx, posy = pygame.mouse.get_pos()
            celx, cely = int(np.floor(posx / dimCW)), int(np.floor(posy / dimCH))
            if newGameState[celx, cely] < len(estados):
                newGameState[celx, cely] = newGameState[celx, cely]+1
            else:
                newGameState[celx, cely] = 0

    for y in range(0, nxC):
        for x in range(0, nyC):
            Vivos = 0
            Enfermos = 0
            Muertos=0
            Curados=0
            if not pauseExect:
                
                n = [
                    gameState[(x-1) % nxC, (y-1) % nyC],
                    gameState[(x) % nxC, (y-1) % nyC],
                    gameState[(x+1) % nxC, (y-1) % nyC],
                    gameState[(x-1) % nxC, (y) % nyC],
                    gameState[(x+1) % nxC, (y) % nyC],
                    gameState[(x-1) % nxC, (y+1) % nyC],
                    gameState[(x) % nxC, (y+1) % nyC],
                    gameState[(x+1) % nxC, (y+1) % nyC]
                ]

                Vivos = n.count(0)
                Enfermos = n.count(estados["enfermo"])
                Muertos=n.count(estados["muerto"])
                Curados=n.count(estados["curado"])
                # REGLAS
                if (gameState[x, y] == 1 ): # condicion de vivios puede mermar la reproduccion
                    
                    # la probabilidad de muerte cumple la formula en funcion del tiempo
                    # p= (1-(1-0.6)^(t*0.1)) esta aumenta la probabilidad de morir en funcion del tiempo
                    # solo muere si tiene mas de 3 enfermos en sus esquinas
                    # la regla empieza cuando la celula e estado enferma cierto tiempo definido 
                    #en "muerte inicial"

                    p_morir = (1-(1-efectos["muerte"])**gameTimes[x,y]*0.1) # probabilidad de morir aumenta con el tiempo y la probabilida de curarse disminuye
                    if r.random() < p_morir and Enfermos > 3 and gameTimes[x,y] > efectos["muerte_inicial"]: 
                        newGameState[x, y] = 2
                        gameTimes[x,y]=1

                    # la probabilidad de no morir es igual a 1-p_morir 
                    # se puede sanar una celula despues de que el tiempo (enfermo) a pasado el definido por ["sana inicial"]

                    elif r.random() < 1-p_morir and gameTimes[x,y]> efectos["sana_inicial"]:#gameTimes[x,y] < 15 and  gameTimes[x,y] > 6:
                        newGameState[x, y] = 3
                        gameTimes[x,y]=1
                    
                    # la celula se mueve y contagia con la taza de infectado dada==2 (un infectado enferma 2)
                    # solo si el tiempo infectado es menor al tiempo de contagio dado en efectos 
                    #  para el covid es 15. 

                    else:    
                        gameTimes[x,y]=gameTimes[x,y]+1
                        data= infectado_mov(efectos["taza_infeccion"])
                        #newGameState[x, y] =0 para caminar esto puede ser
                        for i in range(len(data)):
                            movx,movy= x+data[i][0],y+data[i][1]
                            #!-- desborde de tablero vuelve al inicio (tablero redondo)
                            if movx > nxC-1: 
                                movx=0
                            if movx < 0: 
                                movx=nxC-1
                            if movy > nyC-1: 
                                movy=0
                            if movy < 0: 
                                movy=nyC-1

                            #poner condicion de solo si esta vivo sino no se cambia y si el tiempo de contagio cumple
                            if (gameState[movx, movy] ==0 and gameTimes[x,y]<=efectos["contagio"]) :
                                newGameState[movx, movy] = 1
                                gameTimes[movx,movy]=1
                            
                

        # Dibujar Celda
            poly = [((x) * dimCW, y * dimCH),
                    ((x+1) * dimCW, y * dimCH),
                    ((x+1) * dimCW, (y+1) * dimCH),
                    ((x) * dimCW, (y+1) * dimCH)]

            if newGameState[x, y] == 0:
                pygame.draw.polygon(screen, (148, 134, 128), poly, 1)
            elif newGameState[x, y] == 1:
                pygame.draw.polygon(screen, (255, 120, 120), poly, 0)
            elif newGameState[x, y] == 2:
                pygame.draw.polygon(screen, (0,0,0), poly, 0)
            else:
                pygame.draw.polygon(screen, (120, 255, 120), poly, 0)

    # ACTUALIZAR ESTADO DEL SCREEM
    gameState = np.copy(newGameState)
    if not pauseExect:
        DIAS=DIAS+1
        
                
    print("--------------------------------")
    print("DIAS :",DIAS )
    print("enfermos :",np.count_nonzero(gameState==1))
    print("sanos :",np.count_nonzero(gameState==0))
    print("muertos :",np.count_nonzero(gameState==2))
    print("recuperados :",np.count_nonzero(gameState==3))

    pygame.display.flip()
