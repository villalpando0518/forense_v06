import pandas as pd
import numpy as np 
from sklearn.svm import SVC
from sklearn import svm
from sklearn.preprocessing import LabelEncoder
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
import random
from sklearn.metrics import confusion_matrix

DATAFRAME = "df_esternon.csv"
TARGETS = 2
TARGET_A_USAR = 1
VECTORIZAR = False

HEADER = True
EXTENDER_DATOS = True
APLICAR_PCA = False
APLICAR_NORMALIZAR = False
NUM_CARACTERISTICAS = 16
NUM_DATOS = 2000
VAR_GAUSSIANA = 0.01
GAMMA = 0.001
NUM_C = 50

NUM_MODELOS = 1
NUM_K_VALIDATION = 1

ENCODER = LabelEncoder()
pca = PCA(n_components=NUM_CARACTERISTICAS)
scaler = MinMaxScaler()

def separar_train_test(x_data, y_data, n):
    segmento = NUM_DATOS * (1/NUM_K_VALIDATION)
    segmento = int(segmento)
    inicio = segmento * n
    final = segmento * (n+1)
    if (NUM_K_VALIDATION <3):
        final = inicio + (NUM_DATOS*(1/10))
        final = int(final)
    x_train = np.vstack((x_data[:inicio, :],x_data[final:, :]))
    x_test = x_data[inicio:final] 
    y_train = np.concatenate((y_data[:inicio],y_data[final:]))
    y_test = y_data[inicio:final]
    return x_train, y_train, x_test, y_test

def calcular_presiciones(predicciones, y_testR):
    precision = [0,0,0]
    for i in range(len(predicciones)):
        diferencia = predicciones[i] - y_testR[i]
        diferencia = abs(diferencia)
        #print(y_testR[i], predicciones_ensamble[i], diferencia)
        if(diferencia<=3):
            precision[2] += 1
            if(diferencia<=1):
                precision[1] += 1
                if(diferencia<=0.1):
                    precision[0] += 1
    precision[2] = round(precision[2] / len(y_testR) * 100, 2)
    precision[1] = round(precision[1] / len(y_testR) * 100, 2)
    precision[0] = round(precision[0] / len(y_testR) * 100, 2)
    #print("3 años, 1 año, 0 años: ", precision)
    return precision  

def matriz_de_confusion(predicciones, y_testR):
    matriz_confusion = confusion_matrix(y_testR, predicciones)
    etiquetas = np.unique(np.concatenate((predicciones, y_testR))).astype(int)

    # Crear una figura con un tamaño reducido
    fig = plt.figure(figsize=(len(etiquetas) * 0.2, len(etiquetas) * 0.2))

    # Crear el mapa de calor con ajuste de las etiquetas
    mapa = sns.heatmap(matriz_confusion, annot=True, cmap="BuPu", fmt="d", mask=(matriz_confusion == 0), cbar=False)

    # Ajustar el espaciado de las etiquetas en el eje x
    mapa.set_xticks(np.arange(matriz_confusion.shape[1]) + 0.5)
    mapa.set_xticklabels(etiquetas, rotation='vertical')

    # Ajustar el espaciado de las etiquetas en el eje y
    mapa.set_yticks(np.arange(matriz_confusion.shape[0]) + 0.5)
    mapa.set_yticklabels(etiquetas, rotation=0)

    plt.xlabel('Predicciones')
    plt.ylabel('Reales')

    plt.show()
    return 1

def muestra_votacion(predicciones, predicciones_ens, y_testR):
    predicciones = predicciones.astype(int)
    predicciones_ens = predicciones_ens.astype(int)
    y_testR = y_testR.astype(int)
    
    num_correctas = 0
    num_incorrectas = 0
    terminar = False
    n = 0
    i=0
    muestras = np.zeros((10, NUM_MODELOS+2))
    while(terminar == False):
        muestra = []
        encontrada = False
        if(num_correctas < 5 and predicciones_ens[i] == y_testR[i]):
            muestra = np.append(predicciones[i],[predicciones_ens[i],y_testR[i]])
            encontrada = True
            num_correctas +=1
        if(num_incorrectas < 5 and predicciones_ens[i] != y_testR[i]):
            muestra = np.append(predicciones[i],[predicciones_ens[i],y_testR[i]])
            encontrada = True
            num_incorrectas+=1
        if(encontrada==True):
            muestras[n] = muestra
            n +=1
        
        i+=1
        if(num_correctas >= 5 and num_incorrectas >= 5):
            terminar = True
        if(i>=len(y_testR)):
            terminar = True
    return muestras    


def crear_modelos():
    modelos = []
    for i in range(NUM_MODELOS):
        nuevo_modelo = svm.SVC(kernel='rbf', gamma=random.uniform(0.5, 1.0), C=random.uniform(8, 12))
        modelos.append(nuevo_modelo)
    return modelos

def entrenar_modelos(modelo, x_train, y_train):
    for i in range(NUM_MODELOS):
        modelo[i].fit(x_train,y_train)
    return modelo

def hacer_predicciones(modelo, x_test):
    predicciones = np.zeros((NUM_MODELOS,len(x_test)))
    for i in range(NUM_MODELOS):
        nuevas_predicciones = modelo[i].predict(x_test)
        #nuevas_predicciones =np.argmax(nuevas_predicciones,axis=1)
        #nuevas_predicciones = ENCODER.inverse_transform(nuevas_predicciones)
        predicciones[i] = nuevas_predicciones
    predicciones = predicciones.transpose()
    return predicciones

def leer_datos():
    if(HEADER==False):
        df = pd.read_csv(DATAFRAME, header=None)
    else:
        df = pd.read_csv(DATAFRAME, header=0)
    nc = df.shape[1]-TARGETS
    num_copias = NUM_DATOS // len(df)
    num_para_completar = NUM_DATOS % len(df)
    datos_originales = np.array(df)
    #print("datos originales: ", datos_originales)
    datos_extendidos = np.copy(datos_originales)
    #aplicamos PCA
    if(APLICAR_PCA==True):
        print("aplicando pca")
        carac = datos_originales[:,:nc]
        objetivos = datos_originales[:,nc:]
        #pca = PCA(n_components=NUM_CARACTERISTICAS)
        carac_pca = pca.fit_transform(carac)
        datos_originales = np.column_stack((carac_pca, objetivos))
        #print("PCA: ", sum(pca.explained_variance_ratio_))
        datos_extendidos = np.copy(datos_originales)
        nc = NUM_CARACTERISTICAS
    #Normalizamos
    if(APLICAR_NORMALIZAR == True):
        print("normalizando")
        carac = datos_originales[:,:nc]
        objetivos = datos_originales[:,nc:]
        #scaler = MinMaxScaler()
        carac_normalizados = scaler.fit_transform(carac)
        datos_normalizados = np.column_stack((carac_normalizados, objetivos))
        datos_originales = np.copy(datos_normalizados)
        datos_extendidos = np.copy(datos_normalizados)
    #Extendemos los datos hasta tener los datos deseados
    for i in range(num_copias-2):
        datos_extendidos = np.vstack((datos_extendidos,datos_originales))
    complemento = datos_originales[:num_para_completar,:]
    datos_extendidos = np.vstack((datos_extendidos,complemento))
    #print(datos_extendidos)
    valores = datos_extendidos[:,:nc]
    objetivos = datos_extendidos[:,nc:]
    ruido = np.random.normal(0, VAR_GAUSSIANA, size=(valores.shape[0],valores.shape[1]))
    valores_con_ruido = valores + ruido
    #valores_con_ruido = np.clip(valores_con_ruido,a_min = 0,a_max=1) //sólo si se normalizo
    #print("datos completos despues de extender: ,", valores, ruido ,valores_con_ruido)
    datos_extendidos_con_ruido = np.column_stack((valores_con_ruido,objetivos))
    datos_completos = np.vstack((datos_originales,datos_extendidos_con_ruido))
    #print("datos completos despues de extender: ,",datos_extendidos_con_ruido)
    np.random.shuffle(datos_completos)
    x_data = datos_completos[:,:nc]
    y_data = datos_completos[:,[nc+TARGET_A_USAR-1]]
    #y_data = ENCODER.fit_transform(y_data.reshape(-1))
    #y_data = pd.get_dummies(y_data).values
    if(VECTORIZAR == True):
        y_data = pd.get_dummies(y_data).values
    
    return x_data, y_data

def train_test(X, Y, inicio, final):
    X_entrenamiento = np.vstack((X[:inicio, :],X[final:, :]))
    Y_entrenamiento = np.concatenate((Y[:inicio],Y[final:]))
    X_prueba = X[inicio:final] 
    Y_prueba = Y[inicio:final]
    
    return X_entrenamiento, Y_entrenamiento, X_prueba, Y_prueba

def main(datos_entrada):
    #para importar en el programa principal
    x_data, y_data = leer_datos()
    #print("xdata: ",x_data)
    modelos = crear_modelos()
    modelos_entrenados = entrenar_modelos(modelos, x_data, y_data)
    predicciones = hacer_predicciones(modelos_entrenados, datos_entrada)


    #para ver que onda con la precision
    
    i=0
    for p in predicciones:
        p = p.astype(int)
        
        correctas = 0
        print("i,p,ydata: ",i,p,y_data[i])
        if (p == y_data[i]):
            correctas +=1
        i+=1
       
    return predicciones

def mockup_data():
    #datos_entrada=np.array([[61,44,12,75,22,20,119,2,21,20,5,1,0,2,0,1],[67,46,10,98,42,43,144,15,30,45,5,2,0,0,0,2]])
    datos_entrada, y = leer_datos()
    datos_entrada = datos_entrada[:20]
    #print("datos entrada: ", datos_entrada)
    return datos_entrada

if __name__ == "__main__":
    main(mockup_data())  # Call the main function
