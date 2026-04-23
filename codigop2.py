# ENTREGA 2


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


# OTRAS BÁSICAS
class CatalogoStreaming:
    def __init__(self):
        self.canciones = []
        self.playlists = []
        self.artistas = []
    
    def buscar(self,id_cancion):
        # Cada usuario envía, por cada canción que escucha, una tupla (id, fecha_hora) con el identificador único de la canción de acuerdo con el catálogo de canciones y la fecha y hora exacta en la que escuchó dicha canción 
        for cancion in self.canciones:
            if id_cancion == cancion:
                return cancion
        return None
        
              
class Cancion:
    def __init__(self, id,titulo,fecha,sonoros,sentimentales):
        self.id = id
        self.titulo = titulo
        self.fecha = fecha
        self. atributos_sonoros = sonoros
        self. atributos_sentimentales = sentimentales
    
    def get_titulo(self):
        # para las busquedas alfabeticas
        return self.titulo
    
    def get_fecha(self):
        # para busquedas temporales
        return self.fecha

    def get_atributos_sonoros(self):
        return {**self.atributos_sonoros}
    
    def get_atributos_sentimentales(self):
        return {**self.atributos_sentimentales}
        

class Artista:
    def __init__(self, nombre, fecha, canciones):
        self. canciones = canciones
        self.nombre = nombre
        self.fecha = fecha
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
        self.atributos_sonoros = {}
        # Sacamos las claves de los atributos sonoros:
        for k in self.canciones.atributos_sonoros.keys():
            # sacamos la lista de valores de k en todas las canciones
            v = map(lambda c: c.atributos_sonoros.get(k,0), self.canciones)
            self.atributos_sonoros[k] = media(list(v))
        
        # SENTIMENTALES
        self.atributos_sentimentales = {}
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
        
class StrategyOrdenAlfabetico(RecomendadorStrategy):
    

        

    

        
    
    