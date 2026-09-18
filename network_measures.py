
import scipy.io as sio
import os
import numpy as np
import statistics

def recebe_input():
    data = []
    arquivo = input("Digite o nome do arquivo:")
    caminho = str(os.path.abspath(arquivo))
    with open(caminho, 'r') as dados:
        for linha in dados:
            data.append(linha.strip("\n"))
    #numero de vertices
    n = int(data.pop(0))
    #numero de arestas
    m = int(data.pop(0))
    #modulosm
    modulos = data.pop().split(" ")
    #matriz de correlação
    matriz =[]
    for i in range(n):
        l = []
        for j in range(n):
            l.append(0)
        matriz.append(l)
    while len(data) > 0:
        atual = data.pop(0).strip("\n")
        atual = atual.split(" ")
        i, j = int(atual[0]), int(atual[1])
        matriz[i][j] = 1
        matriz[j][i] = 1
    
    return n, m, modulos, matriz


def open_txt():
    data = []
    caminho = str(os.path.abspath("matriz-binaria.txt"))
    with open(caminho, 'r') as dados:
        for linha in dados:
            linha = linha.strip("\n")
            linha = linha.split(",")
            for i in range(len(linha)):
                linha[i] = int(linha[i])
            data.append(linha)
    return data


def make_hash(binaria):
    lista =[]
    vizinhos = {}
    #fazer dicionario com vizinhos de cada vértice
    for i in range(len(binaria)):
        for j in range(len(binaria)):
            if binaria[i][j] == 1:
                lista.append(j)
            else: continue
        vizinhos[i] = lista
        lista = []
    return vizinhos

def graus(hash):
    graus = []
    for i in range(len(hash)):
        graus.append(len(hash[i]))
        
    return graus
        
    
def spl1(binaria, a, b):
    if a == b:
        return 0
    
    achou = False
    c = 0
    visitados = []
    falta_visitar = [a]
    
    while len(falta_visitar)>0 and not achou:
        linha = falta_visitar.pop()
        c += 1
        for j in range(len(binaria[linha])):
            if binaria[linha][j] == 1:
                if j == b:
                    achou = True
                    break
                elif j not in visitados:
                    falta_visitar.append(j)
                    visitados.append(j)
                
    if not achou:
        return "infinito"
    else:
        return c
    
def spl(binaria, n):
    caminhos ={}
    v =[]
    for a in range (n):
        for b in range(n):
            if [a,b] in v or [b,a] in v:
                continue
            v.append([a,b])
            if a == b:
                caminhos[a, b] = 0
            else:
                caminhos[a,b] = spl1(binaria, a, b)
    return caminhos
            
     

def triangulos(binaria, i):
    ti = 0
    n = len(binaria[0])
    
    for j in range(n):
        for h in range(n):
            ti += int(binaria[i][j]) * int(binaria[i][h]) * int(binaria[j][h])
    ti = ti/2                 
    return ti

#characteristic path length
def cpl(binaria, d, n):
    n = len(d)
    c =0
    for i in range(n):
        for j in range(n):
            try:
                c+= d[(i, j)]
            except: continue
    C = c/n
    return C
    


def global_efficiency(n, d):
    n = int(n)
    sumi =0
    for i in range(n):
        sumj = 0
        for j in range(n):
            if i==j: continue
            else:
                try:
                    dij =d[i, j]
                except: 
                    dij = d[j, i]
                if dij != "infinito":
                    sumj += 1/dij
        sumi += sumj/(n-1)
    ef = sumi/n
    return ef
        
        
        

#coeficiente de clustering
def clustering(binaria, k):
    c = 0
    for i in range(len(binaria)):
        t = triangulos(binaria, i)
        if k[i] > 1:
            c += (2*t)/(k[i]*(k[i] - 1))
    c = c/len(binaria[0])     
        #else: Ci = 0 => C+=0
    return c

def eflocal(vizinhos, binaria, k):
    lista = []
    distancias = {}
    falta_visitar = []
    visitados = []
    e = []

        
    for i in range(len(vizinhos)):
        permitidos = vizinhos[i]
        for a in range(len(vizinhos)):
            pode = False
            if a == i:
                for b in range(len(binaria)):
                    distancias[a, b] = 0
                continue
            if a in permitidos:
                pode = True
            if not pode:
                for v in vizinhos[a]:
                    if v in permitidos:
                        pode = True
                        break
            if not pode:
                for b in range(len(binaria)):
                    distancias[a, b] = 0
                continue
            else:
                falta_visitar.append(a)
                visitados.append(a)
                c = 0
                for b in range(len(vizinhos)):
                    achou= False
                    pode2 =False
                    if b in permitidos:
                        pode2 = True
                    elif not pode2:
                        for v in vizinhos[b]:
                            if v in permitidos:
                                pode2 = True
                                break
                    if not pode2:
                        distancias[a, b] = 0
                        continue
                    else:
                        while len(falta_visitar) >0 and not achou:
                            x = falta_visitar.pop(0)
                            lista = vizinhos[x]
                            
                            c+=1
                            for elemento in lista:
                                if elemento == b:
                                    distancias[a, b] = 1/c
                                    achou = True
                                elif elemento in permitidos and elemento not in visitados:
                                    falta_visitar.append(elemento)
                                    visitados.append(elemento)        
                        if not achou:
                            distancias[a, b] = 0

        e.append(0)
        for j in range(len(binaria)):
            for h in range(len(binaria)):
                if j == h:
                    continue
                if k[i] > 1:
                    num = binaria[i][j]*binaria[i][h]*distancias[j, h]
                    e[-1] = e[-1] + num/(k[i]*(k[i]-1))
                
    E = statistics.mean(e)
                            
    return  E

def make_matrix(binaria, hash):
    M = []
    n = len(binaria)
    for i in range(len(binaria)):
        linha= n*[0]
        if i in hash.keys():
            for v in hash[i]:
                linha[v] += 1
        M.append(linha)
    return M

def localef(b, binaria, k):
    s1 = 0
    for i in range (len(b)):
        new = {}
        vertices = b[i]
        new[i] = vertices
        for a in vertices:
            lista =[i]
            for v in b[a]:
                if v in vertices:
                    lista.append(v)
            new[a] = sorted(lista)
        #caminho só com os vizinhos de i
        d = spl(make_matrix(binaria, new), len(make_matrix(binaria, new)))
        
        for j in range(len(binaria)):
            for h in range(len(binaria)):
                if j == i or j == h:
                    continue
                try: a = d[j, h]
                except: a = d[h, j]
                if a != "infinito" and k[i] >= 2:
                    a = 1/a
                    s1 += binaria[i][j]*binaria[i][h]*a
                else:
                    continue
        if k[i] > 1:
            e2 = s1/(k[i]*(k[i]-1))
        else:
            e2 = 0
        s1 = 0
        
    e3 = e2/(len(binaria[0])) 
    return e3

def transitividade(binaria, k):
    num = 0
    den = 0
    for i in range(len(binaria)):
        ki = k[i]
        t = triangulos(binaria, i)
        num += 2*t
        den += ki*(ki-1)
    try:
        tr = num/den
    except:
        tr = 0
    return tr

def modularity(binaria, k, modulos, l):
    Q = 0
    for i in range(len(binaria)):
        for j in range(len(binaria)):
            if modulos[i] == modulos[j]:
                Q += binaria[i][j] - ((k[i]*k[j])/l)
            else: continue
    Q = Q/l
    
    return Q

def closeness(i, d, n):
    c =0
    for j in range(n):
        try: dij = d[i, j]
        except: dij = d[j, i]
        if dij != "infinito":
            c+=dij
    Li = c/(n-1)
    if Li >0:
        return 1/Li
    else:
        return 0

def num_spl(d,binaria, a, b):
    try:
        djh = d[a, b]
    except:
        djh = d[b, a]
        
    x = make_hash(binaria)
    v = len(x)
    dist ={}
    caminhos = {}
    for i in range (v):
        dist[i] = float("inf")
        caminhos[i] =0
    c = 0
    fila = []
    fila.append(a)
    dist[a] = 0
    caminhos[a] = 1
    visitados = []

    while len(fila) != 0:
        atual = fila.pop(0)
        c += 1
        for elemento in x[atual]:
            if elemento not in visitados:
                fila.append(elemento)
                visitados.append(elemento)
            if dist[elemento] == float("inf") or dist[atual] == float('inf'):
                continue
            if dist[elemento] > dist[atual] +1 and c<=djh:
                dist[elemento] = dist[atual] +1
                caminhos[elemento] = caminhos[atual]
            elif dist[elemento] == dist[atual] +1 and c<= djh:
                caminhos[elemento] = caminhos[elemento]+caminhos[atual]
    return caminhos[b]

def num_paths(hash, a, b, d):
    visitados =[]
    falta_visitar=[]
    atual = None
    c = 0
    caminhos = {}
    num_caminhos = 0
    
    if a == b:
        return 0
    
    try: di = d[a, b]
    except: di = d[b, a]
    if di == "infinito":
        return 0
    falta_visitar.append([a, 0])
    visitados.append([a, 0])
    
    while len(falta_visitar) > 0:
        atual = falta_visitar.pop()
        c = atual[1]
        atual = atual[0]
        c += 1
        
        if c <= di:
            for e in hash[atual]:
                if e == b:
                    num_caminhos +=1
                    caminhos[num_caminhos] = c               
                elif [e, c] not in visitados:
                    falta_visitar.append([e, c])
                    visitados.append([e, c])
        else:
            continue
                        
    return num_caminhos

def betwenness_centrality(binaria, hash, i, n, d):
    somatorio = 0
    for h in range(len(binaria[0])):
        for j in range(len(binaria[0])):
            if h == j or h == i or j ==i:
                continue
            else:
                try:
                    di = d[j, h]
                except:
                    di = d[h, j]
                if di == 1:
                    phi = 1
                    phii = 0
                else:
                    phi = num_paths(hash, j, h, d)
                    phii = num_paths(hash,i, j,d)*num_paths(hash, i, h, d)
                if phi == 0:
                    continue
                else:
                    somatorio += phii/phi
    r = 1/((n-1)*(n-2))
    bi = r*somatorio
    return bi

def average_neighbour(hash, i, k):
    soma = 0
    for v in hash[i]:
            soma+= k[v]
    if k[i] > 0:
        soma = soma/k[i]
    return soma

def within_module_z_score(hash, n, modulos, i):
    conexoes = {}
    for j in range(n):
        conexoes[j] = []
        modulo = modulos[j]
        for a in hash[j]:
            if modulos[a] == modulo:
                conexoes[j].append(a)
    kmi = len(conexoes[i])
    k = []
    for j in range(n):
        k.append(len(conexoes[j]))
    k_ = statistics.mean(k)
    std =statistics.stdev(k)
    z = (kmi - k_)/std
    
    return z

def participation_coefficient(degree, hash, modulos, i):
    soma = 0

    num_mod = len(set(modulos)) #numero de modulos
    for ind in range(num_mod): #para cada modulo
        mi = modulos[ind]
        m =[]
        for a in range(len(modulos)):
            if modulos[a] == mi:
                m.append(a) #achar elementos daquele modulo
        linha = []
        for elemento in hash[i]:
            if elemento in m:
                linha.append(elemento) #elementos do modulo ligados a i
                
        kmi = len(linha)
        ki = degree[i]
        if ki >0:
            soma += (kmi/ki)**2
        else: continue

    p = 1 - soma  
    
    return p  
  
def assortativity_coefficient(l, k, binaria):
    sum1 = 0
    sum2 = 0
    sum3 = 0
    for i in range(len(binaria[0])):
        for j in range(len(binaria[0])):
            if binaria[i][j] == 1:
                sum1 += k[i]*k[j]
                sum2 += (1/2)*(k[i]+k[j])
                sum3 += (1/2)*(k[i]**2+k[j]**2)
    num = sum1/l - ((sum2/l)**2)
    den = sum3/l - ((sum2/l)**2)
    if den> 0:
        A = num/den
    else: A = 0
    return A
     
        
def main():
    n, m, modulos, binaria = recebe_input()
    l = 2*m
    hash = make_hash(binaria)
    i = int(input("i:"))
    j = int(input("j:"))
    di = spl(binaria, n)
    
    degree = graus(hash)
    shortest_path_length = spl1(binaria,i,j)
    triangles = triangulos(binaria, i)
    characteristic_path_length = cpl(binaria, di, n)
    global_efficiency_ = global_efficiency(n, di)
    clustering_coefficient= clustering(binaria, degree)
    transitivity = transitividade(binaria, degree)
    local_efficiency = localef (hash, binaria, degree)
    modularidade = modularity(binaria, degree, modulos, l)
    closenesscentrality = closeness(i, di, n)
    betwennesscentrality = betwenness_centrality(binaria, hash, i, n, di)
    within_module_degree_z_score = within_module_z_score(hash, n, modulos, i)
    participation_coefficient_ = participation_coefficient(degree, hash, modulos, i)
    average_neighbour_degree = average_neighbour(hash, i, degree)
    assortativity_coefficient_ = assortativity_coefficient(l, degree, binaria)
    
    
    print("degree:", degree)
    print("shortest_path_length:", shortest_path_length)
    print("triangles", triangles)
    print("characteristic_path_length ", characteristic_path_length )
    print("global_efficiency", global_efficiency_)
    print("clustering_coefficient", clustering_coefficient)
    print("transitivity",  transitivity)
    print("local_efficiency", local_efficiency)
    print('modularity:', modularidade)
    print("closeness_centrality", closenesscentrality)
    print("betwenness_centrality", betwennesscentrality)
    print("within_module_degree_zscore:", within_module_degree_z_score )
    print("participation_coefficient:", participation_coefficient_)
    print("average neighbour degree", average_neighbour_degree )
    print("assortativity_coefficient", assortativity_coefficient_)
    
    
    
    

main()
