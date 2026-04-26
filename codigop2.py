# ENTREGA 2
import functools 
import numpy as np
from collections import deque # Para la cola de la sesión de escuchase 
import random

# CLASES ABSTRACTAS
from abc import ABCMeta, abstractmethod

class RecomendadorStrategy(metaclass=ABCMeta):
    '''
    TAD RecomendadorStrategy (DESCRIPCION: Clase abstracta que define la interfaz base para cualquier estrategia.
    No puede ser instanciada directamente. OPERACIONES: aplicarAlgoritmo() y match())
    '''         
    
    @abstractmethod
    def aplicarAlgoritmo(self):
        pass


    def match(self, estadisticos, entidad):
        '''
        Efecto: Método que compara los estadísticos de la sesión con los de una entidad (Canción, Artista o Playlist).
        Primero recorre todas las claves de los atributos sonoros (ritmo, tono..) y luego las de lso atributos sentimentales
        (felicidad, energia, ...). 
        Luego para cada atributo, calcula la distancia absoluta entre la media de la sesión y el valor de la entidad.
        Tomamos el siguiente criterio, que es que si la diferencia es menor a uno, consideramos que ese atributo coincide y se
        incrementa un contador. Si es que no, ignoramos el atributo.
        Asi mismo fijamos un umbral de 3 puntos, y cuando el contador es mayor a 3, el método devuelve True, por lo que habrá
        match.
        '''
        contador = 0

        for key in estadisticos['atributos_son'].keys():
            if np.abs(estadisticos['atributos_son'][key]['media'] - entidad.atributos_son[key]) < 1:
                contador += 1
        
        for key in estadisticos['atributos_sent'].keys():
            if np.abs(estadisticos['atributos_sent'][key]['media'] - entidad.atributos_sent[key]) < 1:
                contador += 1
        
        return (contador > 3)
     
# DEFINICIÓN DE LAS ESTRATEGIAS

class StrategyAlfabetica(RecomendadorStrategy):
    '''
    TAD StrategyAlfabetica (DESCRIPCION: Estrategia que busca recomendaciones siguiendo un órden lexicográfico.
    OPERACIONES: aplicarAlgoritmo())
    '''

    def aplicarAlgoritmo(self, estadisticos, catalogo):

        if isinstance(catalogo[0], Artista): # Solo en el caso de que sea Artista entonces x debe acceder a atributo "nombre" y no "título"

            artistas_alfabetico = sorted(catalogo, key=lambda x: x.nombre)

            for artista in artistas_alfabetico:
                matching = self.match(estadisticos, artista)
                if matching:
                    return artista
        
        else: 

            entidad_alfabetico = sorted(catalogo, key=lambda x: x.titulo)

            for entidad in entidad_alfabetico:
                matching = self.match(estadisticos, entidad)
                if matching:
                    return entidad
                
        return None


        
class StrategyTemporal(RecomendadorStrategy):
    '''
    TAD StrategyTemporal (DESCRIPCIÓN: Estrategia de búsqueda de recomendaciones que prioriza los elementos
    más recientes en el tiempo. OPERACIONES: aplicarAlgoritmo())
    '''
    def aplicarAlgoritmo(self,estadisticos, catalogo):
        ordenadas_temporalmente = sorted(catalogo, key=lambda x: x.fecha, reverse=True)
        for i in ordenadas_temporalmente:
            if self.match(estadisticos,i):
                return i
        return None
    

class StrategyAleatoria(RecomendadorStrategy):
    '''
    TAD StrategyAleatoria (DESCRIPCIÓN: Estrategia de búsqueda de recomendaciones seleccionando elementos al azar 
    del catálogo hasta encontrar un acierto. OPERACIONES: aplicarAlgoritmo())
    '''
    def aplicarAlgoritmo(self,estadisticos,catalogo):
        disponibles = list(catalogo)
        while disponibles:
            elegido = random.choice(disponibles)
            if self.match(estadisticos,elegido):
                return elegido
            disponibles.remove(elegido)
        return None
  


class Generador(metaclass=ABCMeta):
    '''
	TAD Generador (DESCRIPCION: Clase abstracta que define la interfaz base para cualquier generador.
	No puede ser instanciada directamente)
	'''  
    def __init__(self,recomendaciones,estrategia):
        self.recomendaciones = recomendaciones
        self.estrategia = estrategia
        
    @abstractmethod
    def generar_recomendacion(self):
        pass


# CHAIN OF RESPONSABILITY
class CalculadorEstadistico(metaclass=ABCMeta):
    '''
    TAD CalculadorEstadistico (DESCRIPCIÓN: Clase abstracta para el procesamiento secuencial de las 
    mñétricas de la sesión. VALORES: manejador (objeto) que hace referencia al siguiente eslabón de la cadena. 
    OPERACIONES: manejar_seesion())
    '''
    def __init__(self, manejador = None):
        self.manejador = manejador

    @abstractmethod

    def manejar_sesion(self):
        pass



# Desarrollo de las clases de la CHAIN OF RESPONSABILITY


class CalculadorMedia(CalculadorEstadistico):
    '''
    TAD CalculadorMedia (DESCRIPCION: Parte de la cadena que calcula la media atrimética de los atributos sonoros y sentimentales
    de las canciones en la cola e la sesión. Si hay un manejador siguiente, le pasa el diccionario resultante. OPERACIONES: manejar_sesion())
    '''

    def manejar_sesion(self, sesion, estadisticos = None):
        if estadisticos is None:
            estadisticos = {'atributos_son': {}, 'atributos_sent': {}}
        
        for i in sesion[0].atributos_son.keys():
            estadisticos['atributos_son'][i] =  {'media': functools.reduce(lambda total, x: total + x.atributos_son[i], sesion, 0) / len(sesion)}
        
        for i in sesion[0].atributos_sent.keys():
            estadisticos['atributos_sent'][i] =  {'media': functools.reduce(lambda total, x: total + x.atributos_sent[i], sesion, 0) / len(sesion)}
    

        if self.manejador is not None:
            return self.manejador.manejar_sesion(sesion, estadisticos)
        
        return estadisticos
        

class CalculadorDesviacion(CalculadorEstadistico):
    '''
    TAD CalculadorDesviacion (DESCRIPCIÓN: Parte de la cadena que calcula la desviación típica de los atibutos de la sesión.
    OPERACIONES: manejar_sesion())
    '''

    def manejar_sesion(self, sesion, estadisticos = None):
        if estadisticos is None:
            estadisticos = {'atributos_son': {}, 'atributos_sent': {}}
        
        n = len(sesion)

        for i in sesion[0].atributos_son.keys():
            
            media = estadisticos['atributos_son'].setdefault(i, {}).get('media')

            if media is None:
                media = sum(x.atributos_son[i] for x in sesion) / len(sesion)

            suma_cuadrados = functools.reduce(lambda total, x: total + (x.atributos_son[i] - media) ** 2, sesion,0)

            estadisticos['atributos_son'][i]['std'] = np.sqrt(suma_cuadrados / n)

        
        for i in sesion[0].atributos_sent.keys():
            
            media = estadisticos['atributos_sent'].setdefault(i, {}).get('media')

            if media is None:
                media = sum(x.atributos_sent[i] for x in sesion) / len(sesion)

            suma_cuadrados = functools.reduce(lambda total, x: total + (x.atributos_sent[i] - media) ** 2, sesion,0)

            estadisticos['atributos_sent'][i]['std'] = np.sqrt(suma_cuadrados / n)

        if self.manejador is not None:
            return self.manejador.manejar_sesion(sesion, estadisticos)
        
        return estadisticos



# La sesión de escuha

class SesionEscucha:
    '''
    TAD SesionEscucha (DESCRIPCIÓN: Clase que guarda el historial de las últimas 10 canciones escuchadas
    por el usuario que sirven para definir sus recomendaciones. VALORES: cola(de canciones) y estadisticos(diccionario).
    OPERACIONES: anyadir_cancion.
    '''
    def __init__(self):
        self.cola = deque(maxlen=10)
        self.estadisticos = {}
    

    def anyadir_cancion(self, cancion):
        self.cola.append(cancion)

        self.estadisticos = CalculadorMedia(CalculadorDesviacion()).manejar_sesion(list(self.cola))

class CatalogoStreaming:
    '''
    TAD CatalogoStreaming (DESCRIPCIÓN: Clase que guarda todas las canciones, artistas y playlist del sistema.
    VALORES: canciones(list), playlist(list), artistas(list). OPERACIONES: buscar, anyadir_cancion, anyadir_playlist,
    anyadir_artista)
    '''
    def __init__(self):
        self.canciones = []
        self.playlists = []
        self.artistas = []
    
    def buscar(self,id_cancion):
        # Cada usuario envía, por cada canción que escucha, una tupla (id, fecha_hora) con el identificador único de la canción de acuerdo con el catálogo de canciones y la fecha y hora exacta en la que escuchó dicha canción 
        res = list(filter(lambda c: c.id == id_cancion, self.canciones))
        return res
    
    def anyadir_cancion(self, cancion):
        self.canciones.append(cancion)
        
    def anyadir_playlist(self, playlist):
        self.playlists.append(playlist)

    def anyadir_artista(self, artista):
        self.artistas.append(artista)
              
class Cancion:
    '''
    TAD Cancion (DESCRIPCIÓN: Clase para representar las canciones. VALORES: id (int), fecha(int),
    ,título (str), atributos_son (dict) y atributos_sen (dict). OPERACIONES: get_titulo, get_fecha,
    get_atributos_sonoros, get_atributos_sentimentales.
    '''
    def __init__(self, id,titulo,fecha,sonoros,sentimentales):
        self.id = id
        self.titulo = titulo
        self.fecha = fecha
        self.atributos_son = sonoros
        self.atributos_sent = sentimentales
    
    def get_titulo(self):
        # para las busquedas alfabeticas
        return self.titulo
    
    def get_fecha(self):
        # para busquedas temporales
        return self.fecha

    def get_atributos_sonoros(self):
        return {**self.atributos_son}
    
    def get_atributos_sentimentales(self):
        return {**self.atributos_sent}
        

class Artista:
    '''
    TAD Artista (DESCRIPCIÓN: Clase para representar los artistas/cantantes y sus canciones. 
    VALORES: nombre (str), fecha(int), canciones (list), atributos_son (dict) y atributos_sen (dict). 
    OPERACIONES: get_nombre,, get_fecha, actualizar_media_atributos).
    '''
    def __init__(self, nombre, fecha, canciones):
        self.nombre = nombre
        self.fecha = fecha
        self.canciones = canciones
        self.atributos_son = {}
        self.atributos_sent = {}
        self.actualizar_media_atributos()
    
    def get_nombre(self):
        # para las busquedas alfabeticas
        return self.nombre
    
    def get_fecha(self):
        return self.fecha
    
    def actualizar_media_atributos(self):
        # para calcular la media de los sonores y sentimentales de todas las canciones del artista
        n = len(self.canciones)
        # aqui metemos un error de que si n es 0
        media = lambda x: sum(x)/n
        
        # SONOROS
        # Sacamos las claves de los atributos sonoros:
        for k in self.canciones[0].atributos_son.keys():
            # sacamos la lista de valores de k en todas las canciones
            v = list(map(lambda c: c.atributos_son.get(k,0), self.canciones))
            self.atributos_son[k] = media(v)
        
        # SENTIMENTALES
        for k in self.canciones[0].atributos_sent.keys():
            # sacamos la lista de valores de k en todas las canciones
            v = list(map(lambda c: c.atributos_sent.get(k,0), self.canciones))
            self.atributos_sent[k] = media(v)
    

class Playlist:
    '''
    TAD Playlist (DESCRIPCIÓN: Clase para representar las playlist. VALORES: titulo (str), fecha(int), 
    canciones (list), atributos_son (dict) y atributos_sen (dict). OPERACIONES: get_titulo, get_fecha, 
    actualizar_media_atributos).
    '''
    def __init__(self, titulo, fecha,canciones):
        self.titulo = titulo
        self.fecha = fecha
        self.canciones = canciones
        self.atributos_son = {}
        self.atributos_sent = {}
        self.actualizar_media_atributos()
   
    def get_titulo(self):
        # para las busquedas
        return self.titulo
    
    def get_fecha(self):
        return self.fecha
    
    def actualizar_media_atributos(self):
        # para calcular la media de los sonores y sentimentales de todas las canciones del artista
        n = len(self.canciones)
        # aqui metemos un error de que si n es 0
        media = lambda x: sum(x)/n
        
        # SONOROS
        # Sacamos las claves de los atributos sonoros:
        for k in self.canciones[0].atributos_son.keys():
            # sacamos la lista de valores de k en todas las canciones
            v = map(lambda c: c.atributos_son.get(k,0), self.canciones)
            self.atributos_son[k] = media(list(v))
        
        # SENTIMENTALES
        for k in self.canciones[0].atributos_sent.keys():
            # sacamos la lista de valores de k en todas las canciones
            v = map(lambda c: c.atributos_sent.get(k,0), self.canciones)
            self.atributos_sent[k] = media(list(v))
        


# EN STAND-BY
class Recomendador:
    '''
    TAD Recomendador (DESCRIPCIÓN: Clase Singleton que coordina el sistema de recomendación.
    VALORES: _unicainstancia (instancia única) y CatalogoStreaming (objeto). OPERACIONES: 
    obtener_instancia)
    '''
    _unicaInstancia = None
    def __init__(self):
        self.catalogo = CatalogoStreaming()
        self.sesion = SesionEscucha()
    
    @classmethod
    def obtener_instancia(cls):
        if not cls._unicaInstancia:
            cls._unicaInstancia = cls()
        return cls._unicaInstancia
    
    def recibir_escucha(self, id_cancion, fecha):
        # para recibir la tupla (id,fecha) cuando el usuario escucha una canción y convertir
        # el id en un objeto Cancion para buscarlo en el Catálogo y añadirlo a la sesión para que empiece
        # al chain of responsabilitu
        cancion_encontrada = self.catalogo.buscar(id_cancion)
        if cancion_encontrada:
            obj_cancion = cancion_encontrada[0]
            self.sesion.anyadir_cancion(obj_cancion)
        else:
            #aqui meter un error.
            print('La canción no existe en el catálogo')
            

# DECORADOR

class DecoradorRecomendacion(metaclass=ABCMeta):
    ''' 
    TAD DecoradorRecomendacion (DESCRIPCIÓN: Clase base para añadir capas a la recomendación. Por defecto se debe
    recomendar una canción. VALORES: generador(objeto))
    '''
    def __init__(self,generador):
        self.generador = generador
        
class DecoradorPlayList(DecoradorRecomendacion):
    '''
    TAD DecoradorPlayList (DESCRIPCIÓN: Extensión que añade a recomendar una playlist a la recomendación base.
    OPERACIONES: generar_recomendacion, match_playlist.
    '''
    def generar_recomendacion(self,estadisticos):
        recomendacion_base = self.cancion.recomendar(estadisticos) 
        playlist_recomendada = self.match_playlist(estadisticos)
        if playlist_recomendada:
            recomendacion_base.append(playlist_recomendada)
        return recomendacion_base
    
    def match_playlist(self,estadisticos):
        return self.estrategia_busqueda.aplicarAlgoritmo(self.CatalogoStreaming.playlist, estadisticos)
  
class DecoradorArtistas(DecoradorRecomendacion):
    
    def match_artista(self,estadisticos):
        return self.estrategia_busqueda.aplicarAlgoritmo(self.CatalogoStreaming.artista, estadisticos)
    
    def generar_recomendacion(self,estadisticos):
        recomendacion_base = self.cancion.recomendar(estadisticos) 
        artista_recomendado = self.match_artista(estadisticos)
        if artista_recomendado:
            recomendacion_base.append(artista_recomendado)
        return recomendacion_base

# CLASE CON LA QUE INTERACTÚA EL USUARIO
class PlataformaStreaming:
    
    def __init__(self,catalogo):
        self.catalogo = catalogo
        self.configuracion_usuario = {'artistas':False,'playlists':False} # por defecto solo canciones
    
    def establecer_configuracion(self, artistas, playlists):
        self.configuracion_usuario['artistas']=artistas
        self.configuracion_usuario['playlists']=playlists
    
    def enviar_recomendador(self, estrategia):
        # por defecto recomendar canciones
        generador = Generador(self.catalogo,estrategia)
        # luego ya depende de lo que haya pedido el usuario
        if self.configuracion_usuario['artistas']:
            generador = DecoradorArtistas(generador)
        elif self.configuracion_usuario['playlists']:
            generador = DecoradorPlayList(generador)
        return generador
            



if __name__ == '__main__':
    cancion1 = Cancion(1,'Hola','2026-23-4', {'ritmo':0.1}, {'felicidad':0.8})
    cancion2 = Cancion(2,'Adios','2026-23-2', {'ritmo':0.8}, {'felicidad':0.2})
    cancion3 = Cancion(3,'Buenas','2026-23-1', {'ritmo':0.32}, {'felicidad':0.23})

    sesion = SesionEscucha()
    sesion.anyadir_cancion(cancion1)
    sesion.anyadir_cancion(cancion2)
    sesion.anyadir_cancion(cancion3)

    Calculador = CalculadorMedia(CalculadorDesviacion()).manejar_sesion(list(sesion.cola))
    print(Calculador)
    
    recomendador = Recomendador.obtener_instancia()
    c1 = Cancion(101, "Song A", "2023-10-01", {'ritmo': 120, 'tono': 1}, {'felicidad': 0.5})
    c2 = Cancion(102, "Song B", "2023-10-02", {'ritmo': 130, 'tono': 2}, {'felicidad': 0.7})

    recomendador.catalogo.anyadir_cancion(c1)
    recomendador.catalogo.anyadir_cancion(c2)
    recomendador.recibir_escucha(101, "2023-10-25 14:00")
    recomendador.recibir_escucha(102, "2023-10-25 14:05")

    print("Estadísticos actuales de la sesión:")
    print(recomendador.sesion.estadisticos)

    




        

    

        
    
    