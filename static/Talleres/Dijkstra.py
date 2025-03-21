import json  # Librería para manejar datos en formato JSON
import networkx as nx  # Librería para trabajar con grafos
import matplotlib.pyplot as plt  # Librería para graficar los grafos

def cargar_grafo(datos):
    G_tiempo = nx.DiGraph()
    G_distancia = nx.DiGraph()
    
    for origen, destinos in datos.items():
        for destino, valores in destinos.items():
            G_tiempo.add_edge(origen, destino, weight=valores["tiempo"])
            G_distancia.add_edge(origen, destino, weight=valores["distancia"])
    
    return G_tiempo, G_distancia

def ruta_mas_rapida(G, inicio):
    try:
        distancias, _ = nx.single_source_bellman_ford(G, inicio, weight='weight')
        return distancias
    except nx.NetworkXUnbounded:
        print("Error: el grafo contiene un ciclo negativo.")
        return None

def tsp_aproximado(G, inicio):
    if nx.is_strongly_connected(G):
        return nx.approximation.traveling_salesman_problem(G, cycle=True, weight="weight")
    else:
        print("El grafo no es fuertemente conectado, convirtiéndolo en no dirigido...")
        G_undirected = G.to_undirected()
        ruta = nx.approximation.traveling_salesman_problem(G_undirected, cycle=True, weight="weight")
        
        # Filtrar ruta para incluir solo conexiones válidas en el grafo de distancias
        ruta_filtrada = [ruta[0]]
        for i in range(1, len(ruta)):
            if ruta_filtrada[-1] in G and ruta[i] in G[ruta_filtrada[-1]]:
                ruta_filtrada.append(ruta[i])
        
        if len(ruta_filtrada) < 2:
            print("Error: No se encontró una ruta válida.")
            return None
        
        return ruta_filtrada

def graficar_ruta(G, ruta, titulo, color):
    plt.figure(figsize=(10, 7))
    posiciones = {
        "Universidad Sergio Arboleda": (4.6584, -74.0937),
        "Calle 80": (4.7100, -74.1000),
        "Avenida Suba": (4.7199, -74.0844),
        "Suba Rincón": (4.7545, -74.0832),
        "Autopista Norte": (4.7130, -74.0720),
        "Avenida Boyacá": (4.7200, -74.1250)
    }
    
    pos = {nodo: posiciones[nodo] for nodo in G.nodes if nodo in posiciones}
    nx.draw(G, pos, with_labels=True, node_color='lightgray', node_size=1500, font_size=9, edge_color="gray")
    
    path_edges = list(zip(ruta, ruta[1:]))
    nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color=color, width=2.5, style="solid" if color == 'red' else "dashed")
    
    for i, nodo in enumerate(ruta):
        plt.text(pos[nodo][0], pos[nodo][1] + 0.02, str(i + 1), fontsize=12, fontweight='bold', color=color)
    
    plt.title(titulo)
    plt.show()

json_data = '''
{
    "Universidad Sergio Arboleda": {
        "Calle 80": {"tiempo": 20, "distancia": 8},
        "Autopista Norte": {"tiempo": 15, "distancia": 6},
        "Avenida Boyacá": {"tiempo": 30, "distancia": 12}
    },
    "Calle 80": {
        "Suba Rincón": {"tiempo": 30, "distancia": 12}
    },
    "Avenida Suba": {
        "Suba Rincón": {"tiempo": 15, "distancia": 7}
    },
    "Autopista Norte": {
        "Avenida Suba": {"tiempo": 10, "distancia": 5}
    },
    "Avenida Boyacá": {
        "Suba Rincón": {"tiempo": 25, "distancia": 11}
    }
}
'''

datos = json.loads(json_data)
G_tiempo, G_distancia = cargar_grafo(datos)
inicio = "Universidad Sergio Arboleda"

tiempos = ruta_mas_rapida(G_tiempo, inicio)
if tiempos:
    print(f"🔴 Ruta más rápida desde {inicio}:")
    for nodo, tiempo in tiempos.items():
        print(f"   {nodo} -> {tiempo} min")

ruta_optima = tsp_aproximado(G_distancia, inicio)
if ruta_optima:
    distancia_total = sum(
        G_distancia[ruta_optima[i]][ruta_optima[i+1]]['weight']
        for i in range(len(ruta_optima)-1)
        if ruta_optima[i] in G_distancia and ruta_optima[i+1] in G_distancia[ruta_optima[i]]
    )
    print(f"\n🟢 Ruta más óptima (circuito más corto): {ruta_optima}")
    print(f"   Distancia total: {distancia_total} km")

graficar_ruta(G_tiempo, list(tiempos.keys()), "Ruta más rápida (menor tiempo)", "red")
graficar_ruta(G_distancia, ruta_optima, "Ruta más óptima (menor distancia)", "green")
