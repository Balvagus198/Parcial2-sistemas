import re
import string
import itertools
import pandas as pd
import matplotlib.pyplot as plt
from graphviz import Digraph

def procesar_texto(texto):
    # Operadores booleanos
    operadores = {
        'y': '^',
        'o': 'v',
        'no': '~',
        '-': ' '
    }

    partes = re.split(r'\s+(y|o|no|-)\s+', texto)

    oraciones = {}
    variable_index = 0
    for parte in partes:
        if parte not in operadores:
            oracion = parte.strip()
            if oracion:
                variable = string.ascii_lowercase[variable_index]
                oraciones[variable] = oracion
                variable_index += 1

    # Construir la fórmula lógica
    expresion = ""
    variable_index = 0
    for i, parte in enumerate(partes):
        if parte in operadores:
            if parte == "y":
                expresion += " ^ "
            elif parte == "o":
                expresion += " v "
            elif parte == "no" and i + 1 < len(partes) and partes[i + 1].strip():
                expresion += " ~"
                variable = string.ascii_lowercase[variable_index]
                expresion += variable
                variable_index += 1
                continue
        else:
            if parte.strip():
                variable = string.ascii_lowercase[variable_index]
                expresion += variable
                variable_index += 1

    # Mostrar las proposiciones y ecuación
    for letra, frase in oraciones.items():
        print(f"{letra}: {frase}")
    
    print("\nEcuación:")
    print(expresion)

    # Crear tabla de verdad
    combinaciones, resultados = generar_tabla_verdad(oraciones, expresion)
    
    # Generar el árbol de decisiones
    generar_arbol(oraciones, combinaciones, resultados)
    
    # Generar el árbol con la estructura de la pizarra
    generar_arbol_como_imagen()


def generar_tabla_verdad(oraciones, expresion):
    variables = list(oraciones.keys())
    combinaciones = list(itertools.product([False, True], repeat=len(variables)))

    # Evaluación de la expresión para cada combinación
    resultados = []
    for combinacion in combinaciones:
        contexto = dict(zip(variables, combinacion))

        # Reemplazar variables en la expresión con sus valores en 'contexto'
        expresion_eval = expresion
        for var, val in contexto.items():
            expresion_eval = expresion_eval.replace(var, str(val))

        # Evaluar la expresión lógica
        expresion_eval = expresion_eval.replace('^', ' and ').replace('v', ' or ').replace('~', ' not ')
        resultado = eval(expresion_eval)
        resultados.append(resultado)

    # Crear un DataFrame de pandas para la tabla de verdad
    tabla_verdad = pd.DataFrame(combinaciones, columns=variables)
    tabla_verdad[expresion] = resultados  # Usar la fórmula como título de la columna de resultado

    # Mostrar la tabla de verdad en consola
    print("\nTabla de verdad:")
    print(tabla_verdad)

    # Graficar la tabla de verdad y guardarla como imagen
    fig, ax = plt.subplots(figsize=(8, 4))  # Ajustar tamaño si es necesario
    ax.axis('tight')
    ax.axis('off')
    tabla = ax.table(cellText=tabla_verdad.values,
                     colLabels=tabla_verdad.columns,
                     cellLoc='center', loc='center')
    tabla.scale(1.2, 1.2)  # Ajustar escala si es necesario
    plt.savefig('tabla_verdad.png')  # Guardar la imagen
    plt.show()  # Mostrar la imagen

    return combinaciones, resultados

def generar_arbol(oraciones, combinaciones, resultados):
    # Crear el grafo utilizando Graphviz
    dot = Digraph()

    dot.node('Raiz', 'Combinaciones')
    
    variables = list(oraciones.keys())

    # Crear nodos de variables
    for var in variables:
        dot.node(var, var)
        dot.edge('Raiz', var)

    # Estados finales según resultados
    for i, combinacion in enumerate(combinaciones):
        estado_label = 'y' if resultados[i] else 'x'
        estado_color = 'green' if resultados[i] else 'red'
        estado_nombre = f"Estado_{i+1}"
        dot.node(estado_nombre, estado_label, color=estado_color)
        # Añadir las conexiones de cada variable
        for var_index, valor in enumerate(combinacion):
            if valor:
                dot.edge(variables[var_index], estado_nombre)

    # Guardar y renderizar el árbol
    dot.render('arbol_decisiones', format='png', cleanup=True)
    print("Árbol de decisiones generado y guardado como 'arbol_decisiones.png'.")


def generar_arbol_como_imagen():
    # Crear el grafo utilizando Graphviz
    dot = Digraph()

    # Crear el nodo raíz A
    dot.node('A', 'A')

    # Añadir nodos de A con valores 0 y 1
    dot.node('A0', '0')
    dot.node('A1', '1')
    dot.edge('A', 'A0')
    dot.edge('A', 'A1')

    # Añadir nodos de B bajo A=0 y A=1
    dot.node('B00', 'B = 0')
    dot.node('B01', 'B = 1')
    dot.node('B10', 'B = 0')
    dot.node('B11', 'B = 1')
    dot.edge('A0', 'B00')
    dot.edge('A0', 'B01')
    dot.edge('A1', 'B10')
    dot.edge('A1', 'B11')

    # Añadir nodos de C bajo cada B
    dot.node('C000', 'C = 0')
    dot.node('C001', 'C = 1')
    dot.node('C010', 'C = 0')
    dot.node('C011', 'C = 1')
    dot.node('C100', 'C = 0')
    dot.node('C101', 'C = 1')
    dot.node('C110', 'C = 0')
    dot.node('C111', 'C = 1')
    dot.edge('B00', 'C000')
    dot.edge('B00', 'C001')
    dot.edge('B01', 'C010')
    dot.edge('B01', 'C011')
    dot.edge('B10', 'C100')
    dot.edge('B10', 'C101')
    dot.edge('B11', 'C110')
    dot.edge('B11', 'C111')

    # Añadir los resultados (numéricos) como nodos finales
    dot.node('R000', '1', shape='rectangle')
    dot.node('R001', '1', shape='rectangle')
    dot.node('R010', '2', shape='rectangle')
    dot.node('R011', '2', shape='rectangle')
    dot.node('R100', '-3', shape='rectangle')
    dot.node('R101', '-3', shape='rectangle')
    dot.node('R110', '-3', shape='rectangle')
    dot.node('R111', '-3', shape='rectangle')
    
    # Añadir los bordes finales hacia los resultados
    dot.edge('C000', 'R000')
    dot.edge('C001', 'R001')
    dot.edge('C010', 'R010')
    dot.edge('C011', 'R011')
    dot.edge('C100', 'R100')
    dot.edge('C101', 'R101')
    dot.edge('C110', 'R110')
    dot.edge('C111', 'R111')

    # Guardar y renderizar el árbol
    dot.render('arbol_como_imagen', format='png', cleanup=True)
    print("Árbol de decisiones generado y guardado como 'arbol_como_imagen.png'.")


# Ejemplo de uso
texto_entrada = "Hoy es lunes y está lloviendo, o no voy al trabajo y hay tráfico en la carretera"
print(texto_entrada, "\n")
procesar_texto(texto_entrada)
