import re
import json
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from itertools import product

def transformar_a_logica(oracion):
    elementos = re.split(r'\s+y\s+|\s+o\s+', oracion)
    expresion_logica = oracion.replace(" y ", " ∧ ").replace(" o ", " ∨ ")
    etiquetas = ['X', 'Y', 'Z', 'W', 'P', 'Q']
    correspondencia = {elementos[i]: etiquetas[i] for i in range(len(elementos))}
    for elemento, etiqueta in correspondencia.items():
        expresion_logica = expresion_logica.replace(elemento, etiqueta)
    return expresion_logica, correspondencia

def crear_tabla_verdad(lista_reglas):
    variables = sorted(set(var for regla in lista_reglas for var in regla["correspondencia"].values()))
    casos = list(product([True, False], repeat=len(variables)))
    tabla_verdad = []
    for caso in casos:
        valor_actual = dict(zip(variables, caso))
        resultado_reglas = []
        for regla in lista_reglas:
            expresion = regla["expresion_logica"]
            resultado = eval(expresion.replace("∧", " and ").replace("∨", " or "), {}, valor_actual)
            resultado_reglas.append(resultado)
        tabla_verdad.append((caso, resultado_reglas))
    return tabla_verdad, variables

def guardar_tabla_como_imagen(tabla, variables, nombre_imagen):
    casos = [list(caso) + resultado for caso, resultado in tabla]
    columnas = variables + [f"Regla {i+1}" for i in range(len(tabla[0][1]))]
    df = pd.DataFrame(casos, columns=columnas)
    fig, ax = plt.subplots(figsize=(10, len(df) * 0.5 + 1))
    ax.axis('tight')
    ax.axis('off')
    tabla_mostrar = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')
    tabla_mostrar.auto_set_font_size(False)
    tabla_mostrar.set_fontsize(10)
    plt.title('Tabla de Verdad')
    plt.savefig(nombre_imagen, bbox_inches='tight')
    plt.close()

def generar_arbol_decisiones_por_niveles(lista_reglas, tabla_verdad, variables):
    G = nx.DiGraph()
    G.add_node("A", subset=0)  # Nodo raíz en el nivel 0
    
    nodos_nivel_anterior = [("A", 0)]
    
    for i, variable in enumerate(variables):
        nodos_nivel_actual = []
        for nodo, nivel in nodos_nivel_anterior:
            nivel_siguiente = nivel + 1
            nodo_true = f"{nodo}_{variable}_V"
            nodo_false = f"{nodo}_{variable}_F"
            
            G.add_node(nodo_true, subset=nivel_siguiente)
            G.add_node(nodo_false, subset=nivel_siguiente)
            
            G.add_edge(nodo, nodo_true, label="V")
            G.add_edge(nodo, nodo_false, label="F")
            
            nodos_nivel_actual.extend([(nodo_true, nivel_siguiente), (nodo_false, nivel_siguiente)])
        
        nodos_nivel_anterior = nodos_nivel_actual
    
    for idx, (caso, resultados) in enumerate(tabla_verdad):
        resultado_final = all(resultados)
        resultado_nodo = f"Resultado_{'Verdadero' if resultado_final else 'Falso'}_{idx+1}"
        G.add_node(resultado_nodo, color="green" if resultado_final else "red", subset=len(variables)+1)
        
        for nodo, nivel in nodos_nivel_anterior:
            G.add_edge(nodo, resultado_nodo)

    pos = nx.multipartite_layout(G, subset_key="subset")
    
    colors = [G.nodes[n].get("color", "skyblue") for n in G.nodes]
    edge_labels = nx.get_edge_attributes(G, "label")
    
    plt.figure(figsize=(12, 10))
    nx.draw(G, pos, with_labels=True, node_size=2000, node_color=colors, font_size=10, font_weight="bold", arrows=False)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.title("Árbol de Decisiones por Niveles")
    plt.savefig("arbol_decisiones_niveles.png")
    plt.close()

def mostrar_tabla_de_atomos(tabla_verdad, variables, lista_reglas):
    with open("tabla_atomos.txt", "w") as archivo:
        archivo.write("Tabla de Átomos:\n")
        archivo.write("Variables | Valor | Reglas\n")
        for caso, resultados in tabla_verdad:
            valores_atomos = {variable: valor for variable, valor in zip(variables, caso)}
            resultados_textuales = [f"{lista_reglas[i]['expresion_logica']}: {'V' if r else 'F'}" for i, r in enumerate(resultados)]
            archivo.write(f"{valores_atomos} | Resultados: {', '.join(resultados_textuales)}\n")
    print("Tabla de átomos guardada en 'tabla_atomos.txt'.")

def programa_principal():
    lista_reglas = []
    archivo_json = "reglas.json"
    while True:
        print("\n1. Crear nueva regla")
        print("2. Mostrar reglas, tabla de verdad, tabla de átomos y árbol de decisiones")
        print("3. Guardar reglas")
        print("4. Cargar reglas")
        print("5. Salir")
        opcion = input("Seleccione una opción: ")
        if opcion == "1":
            oracion = input("Ingrese una proposición lógica: ")
            expresion_logica, correspondencia = transformar_a_logica(oracion)
            lista_reglas.append({"expresion_logica": expresion_logica, "correspondencia": correspondencia})
            print("Regla creada.")
        elif opcion == "2":
            if not lista_reglas:
                print("No hay reglas para mostrar.")
                continue
            tabla_verdad, variables = crear_tabla_verdad(lista_reglas)
            guardar_tabla_como_imagen(tabla_verdad, variables, "tabla_verdad.png")
            print("Tabla de verdad guardada como 'tabla_verdad.png'.")
            img = plt.imread("tabla_verdad.png")
            plt.imshow(img)
            plt.axis('off')
            plt.show()
            mostrar_tabla_de_atomos(tabla_verdad, variables, lista_reglas)
            generar_arbol_decisiones_por_niveles(lista_reglas, tabla_verdad, variables)
            img = plt.imread("arbol_decisiones_niveles.png")
            plt.imshow(img)
            plt.axis('off')
            plt.show()
        elif opcion == "3":
            with open(archivo_json, 'w', encoding='utf-8') as file:
                json.dump(lista_reglas, file)
            print(f"Reglas guardadas en {archivo_json}.")
        elif opcion == "4":
            try:
                with open(archivo_json, 'r', encoding='utf-8') as file:
                    lista_reglas = json.load(file)
                print(f"Reglas recuperadas desde {archivo_json}.")
            except FileNotFoundError:
                print("Archivo no encontrado.")
        elif opcion == "5":
            print("Saliendo del programa.")
            break
        else:
            print("Opción no válida. Intente nuevamente.")

if __name__ == "__main__":
    programa_principal()
