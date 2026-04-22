# ENTREGA 2


# CLASES ABSTRACTAS
from abc import ABCMeta, abstractmethod

class RecomendadorStrategy(metaclass=ABCMeta):
    '''
    TAD RecomendadorStrategy (DESCRIPCION: Clase abstracta que define la interfaz base para cualquier estrategia.
    No puede ser instanciada directamente)
    '''         
    
    @abstractmethod
    def aplicarAlgorito(self):
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
        
    
class Cancion:
    def __init__(self, id):
        self. atributos = {}
        self.id = id

class Artista:
    def __init__(self, nombre, fecha):
        self. canciones = []
        self.atributos = {}
        self.nombre = nombre
        self.fecha = fecha

class Playlist:
    def __init__(self, titulo, fecha):
        self.titulo = titulo
        self.fecha = fecha
        self. canciones = []
        self.atributos = {}

class Recomendador:
    _unicaInstancia = None
    def __init__(self):
        catalogo = CatalogoStreaming()
    
    @classmethod
    def obtener_instancia(cls):
        if not cls._unicaInstancia:
            cls._unicaInstancia = cls()
        return cls._unicaInstancia
    
    

        
    
    