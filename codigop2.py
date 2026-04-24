# ENTREGA 2
import functools 
import numpy as np
from collections import deque # Para la cola de la sesión de escuchase 

# CLASES ABSTRACTAS
from abc import ABCMeta, abstractmethod

class RecomendadorStrategy(metaclass=ABCMeta):
    '''
    TAD RecomendadorStrategy (DESCRIPCION: Clase abstracta que define la interfaz base para cualquier estrategia.
    No puede ser instanciada directamente)
    '''         
    
    @abstractmethod
    def aplicarAlgoritmo(self):
        pass
    
class Generador(metaclass=ABCMeta):
    '''
	TAD Generador (DESCRIPCION: Clase abstracta que define la interfaz base para cualquier generador.
	No puede ser instanciada directamente)
	'''  
    def __init__(self,recomendaciones,estrategia):
        self.recomendaciones = {}
        self.estrategia = RecomendadorStrategy()
        
    @abstractmethod
    def generar_recomendacion(self):
        pass

class DecoradorRecomendacion(metaclass=ABCMeta):
    def __init__(self,generador):
        self.generador = Generador()

# CHAIN OF RESPONSABILITY
class CalculadorEstadistico(metaclass=ABCMeta):
    def __init__(self, manejador = None):
        self.manejador = manejador

    @abstractmethod

    def generar_estadistico(self):
        pass


# OTRAS BÁSICAS

# Desarrollo de las clases de la CHAIN OF RESPONSABILITY


class CalculadorMedia(CalculadorEstadistico):

    def manejar_sesion(self, sesion, estadisticos = None):
        if estadisticos is None:
            estadisticos = {'atributos_son': {}, 'atributos_sent': {}}
        
        for i in sesion[0].atributos_son.keys():
            estadisticos['atributos_son'][i] =  {'media': functools.reduce(lambda total, x: total + x.atributos_son[i], sesion, 0) / len(sesion)}
        
        for i in sesion[0].atributos_sent.keys():
            estadisticos['atributos_sent'][i] =  {'media': functools.reduce(lambda total, x: total + x.atributos_sent[i], sesion, 0) / len(sesion)}
    

        if self.manejador is not None:
            self.manejador.manejar_sesion(sesion, estadisticos)
        else:
            return estadisticos
        

class CalculadorDesviacion(CalculadorEstadistico):

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
            self.manejador.manejar_sesion(sesion, estadisticos)
        else:
            return estadisticos



# La sesión de escuha

class SesionEscucha:
    def __init__(self):
        self.cola = deque(maxlen=10)
        self.estadisticos = CalculadorMedia(CalculadorEstadistico).manejar_sesion(list(self.cola))
    

    def anyadir_cancion(self, cancion):
        self.cola.append(cancion)

class CatalogoStreaming:
    def __init__(self):
        self.canciones = []
        self.playlists = []
        self.artistas = []
    
    def buscar(self,id_cancion):
        # Cada usuario envía, por cada canción que escucha, una tupla (id, fecha_hora) con el identificador único de la canción de acuerdo con el catálogo de canciones y la fecha y hora exacta en la que escuchó dicha canción 
        res = list(filter(lambda c: c.id_cancion == c.id, self.canciones))
        return res
    
    def anyadir_cancion(self, cancion):
        self.canciones.append(cancion)
        
    def anyadir_playlist(self, playlist):
        self.playlists.append(playlist)

    def anyadir_artista(self, artista):
        self.artistas.append(artista)
              
class Cancion:
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
    def __init__(self, nombre, fecha, canciones):
        self.nombre = nombre
        self.fecha = fecha
        self.canciones = canciones
        self.atributos_sonoros = {}
        self.atributos_sentimentales = {}
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
        for k in self.canciones.atributos_sonoros.keys():
            # sacamos la lista de valores de k en todas las canciones
            v = map(lambda c: c.atributos_sonoros.get(k,0), self.canciones)
            self.atributos_sonoros[k] = media(list(v))
        
        # SENTIMENTALES
        for k in self.canciones.atributos_sentimentales.keys():
            # sacamos la lista de valores de k en todas las canciones
            v = map(lambda c: c.atributos_sentimentales.get(k,0), self.canciones)
            self.atributos_sentimentales[k] = media(list(v))
        

class Playlist:
    def __init__(self, titulo, fecha,canciones):
        self.titulo = titulo
        self.fecha = fecha
        self.canciones = canciones
        self.atributos_sonoros = {}
        self.atributos_sentimentales = {}
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
        for k in self.canciones.atributos_sonoros.keys():
            # sacamos la lista de valores de k en todas las canciones
            v = map(lambda c: c.atributos_sonoros.get(k,0), self.canciones)
            self.atributos_sonoros[k] = media(list(v))
        
        # SENTIMENTALES
        for k in self.canciones.atributos_sentimentales.keys():
            # sacamos la lista de valores de k en todas las canciones
            v = map(lambda c: c.atributos_sentimentales.get(k,0), self.canciones)
            self.atributos_sentimentales[k] = media(list(v))
        

class Recomendador:
    _unicaInstancia = None
    def __init__(self):
        catalogo = CatalogoStreaming()
    
    @classmethod
    def obtener_instancia(cls):
        if not cls._unicaInstancia:
            cls._unicaInstancia = cls()
        return cls._unicaInstancia

class DecoradorPlayList(DecoradorRecomendacion):
    
    def generar_recomendacion(self,estadisticos):
        recomendacion_base = self.cancion.recomendar(estadisticos) 
        playlist_recomendada = self.match_playlist(estadisticos)
        if playlist_recomendada:
            recomendacion_base.append(playlist_recomendada)
        return recomendacion_base
    
    def match_playlist(self,estadisticos):
        return self.estrategia_busqueda.aplicarAlgoritmo(self.CatalogoStreaming.playlist, estadisticos)
        
if __name__ == '__main__':
    cancion1 = Cancion(1,'Hola','2026-23-4', {'ritmo':0.1}, {'felicidad':0.8})
    cancion2 = Cancion(2,'Adios','2026-23-2', {'ritmo':0.8}, {'felicidad':0.2})
    cancion3 = Cancion(3,'Buenas','2026-23-1', {'ritmo':0.32}, {'felicidad':0.23})



        

    

        
    
    