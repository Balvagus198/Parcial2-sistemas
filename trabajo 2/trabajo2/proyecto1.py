import itertools
import pandas as pd
import matplotlib.pyplot as plt
from graphviz import Digraph
import sympy as sp

def procesar_expresiones():
    # Proposiciones
    oraciones = {
        'A': "Recibo ayuda",
        'B': "Me siento bien",
        'C': "Puedo salir de vacaciones"
    }

    # Definir las variables simbólicas
    A, B, C = sp.symbols('A B C')

    # Expresión lógica combinada
    expresion_comb = (sp.Not(A) | sp.Not(B)) & (sp.Not(C))  # Modificada para ejemplo sencillo

    # Mostrar las proposiciones
    print("Proposiciones:")
    for letra, frase in oraciones.items():
        print(f"{letra}: {frase}")

    # Generar tabla de verdad para la expresión combinada
    print("\nTabla de verdad para la expresión combinada:")
    combinaciones, resultados = generar_tabla_verdad(oraciones, expresion_comb)

    # Generar árbol de decisiones
    print("\nGenerando árbol de decisiones...")
    generar_arbol(oraciones, combinaciones, resultados)

def generar_tabla_verdad(oraciones, expresion):
    variables = list(oraciones.keys())
    combinaciones = list(itertools.product([False, True], repeat=len(variables)))

    # Evaluación de la expresión para cada combinación
    resultados = []
    for combinacion in combinaciones:
        contexto = dict(zip(variables, combinacion))

        # Evaluar la expresión lógica de forma segura usando sympy
        resultado = expresion.subs(contexto).simplify()
        resultados.append(bool(resultado))

        # Depuración: imprimir la expresión a evaluar
        print(f"Evaluando: {contexto} -> Resultado: {resultado}")

    # Crear un DataFrame de pandas para la tabla de verdad
    tabla_verdad = pd.DataFrame(combinaciones, columns=variables)
    tabla_verdad['Resultado'] = resultados

    # Mostrar la tabla de verdad en consola
    print(tabla_verdad)

    return combinaciones, resultados

def generar_arbol(oraciones, combinaciones, resultados):
    # Crear el grafo utilizando Graphviz
    dot = Digraph()

    # Crear nodos y ramas basados en el árbol de la imagen
    nodos = list(oraciones.keys())
    
    # Añadir el nodo raíz
    dot.node('Raiz', 'A')

    # Crear las ramificaciones para el nodo A
    dot.node('A0', '0')
    dot.node('A1', '1')
    dot.edge('Raiz', 'A0', label='0')
    dot.edge('Raiz', 'A1', label='1')

    # Añadir los nodos para B
    dot.node('B00', 'B=0')
    dot.node('B01', 'B=1')
    dot.edge('A0', 'B00', label='0')
    dot.edge('A0', 'B01', label='1')

    dot.node('B10', 'B=0')
    dot.node('B11', 'B=1')
    dot.edge('A1', 'B10', label='0')
    dot.edge('A1', 'B11', label='1')

    # Añadir nodos para C y los resultados finales
    dot.node('C000', 'C=0')
    dot.node('C001', 'C=1')
    dot.node('C010', 'C=0')
    dot.node('C011', 'C=1')
    dot.node('C100', 'C=0')
    dot.node('C101', 'C=1')
    dot.node('C110', 'C=0')
    dot.node('C111', 'C=1')

    # Añadir ramas de B a C
    dot.edge('B00', 'C000', label='0')
    dot.edge('B00', 'C001', label='1')
    dot.edge('B01', 'C010', label='0')
    dot.edge('B01', 'C011', label='1')
    dot.edge('B10', 'C100', label='0')
    dot.edge('B10', 'C101', label='1')
    dot.edge('B11', 'C110', label='0')
    dot.edge('B11', 'C111', label='1')

    # Estados finales con los resultados
    for i, combinacion in enumerate(combinaciones):
        estado_label = 'True' if resultados[i] else 'False'
        estado_color = 'green' if resultados[i] else 'red'
        estado_nombre = f"Estado_{i+1}"
        dot.node(estado_nombre, estado_label, color=estado_color)
        # Crear la conexión a los resultados
        if combinacion == (False, False, False):
            dot.edge('C000', estado_nombre)
        elif combinacion == (False, False, True):
            dot.edge('C001', estado_nombre)
        elif combinacion == (False, True, False):
            dot.edge('C010', estado_nombre)
        elif combinacion == (False, True, True):
            dot.edge('C011', estado_nombre)
        elif combinacion == (True, False, False):
            dot.edge('C100', estado_nombre)
        elif combinacion == (True, False, True):
            dot.edge('C101', estado_nombre)
        elif combinacion == (True, True, False):
            dot.edge('C110', estado_nombre)
        elif combinacion == (True, True, True):
            dot.edge('C111', estado_nombre)

    # Guardar y renderizar el árbol
    dot.render('arbol_decisiones_actualizado', format='png', cleanup=True)
    print("Árbol de decisiones generado y guardado como 'arbol_decisiones_actualizado.png'.")

# Ejemplo de uso
procesar_expresiones()
