# ENTREGA 2
import functools 
import numpy as np
from collections import deque # Para la cola de la sesión de escuchase 
import random


# Errores

class SingletonException(Exception):
    pass

class IdInexistente(Exception): # el id de la cancion no está en el catalogo
    pass

class SesionVacia(Exception): # la sesión de escucha no tiene canciones, por lo que no se pueden calcular los estadísticos al dividir entre n
	pass

class AtributosIncompatibles(Exception): #las claves de los atirbutos de la entidad no coinciden con los estadisticos
    pass

class RecomendacionNoEncontrada(Exception): #para porque no hay niguna que supera el umbral
    pass

class ElementoDuplicado(Exception): # cuando el id ya es´ta en el catálogo
    pass

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
        try:
            for key in estadisticos['atributos_son'].keys():
                if key not in entidad.atributos_son:
                    raise AtributosIncompatibles(f"Falta el atributo {key} en la entidad")
                if np.abs(estadisticos['atributos_son'][key]['media'] - entidad.atributos_son[key]) < 1:
                    contador += 1
                for key in estadisticos['atributos_sent'].keys():
                    if np.abs(estadisticos['atributos_sent'][key]['media'] - entidad.atributos_sent[key]) < 1:
                        contador += 1
            return (contador > 3)
        except KeyError as e:
            raise AtributosIncompatibles('Los estaditicos no son compatibles')
     
# DEFINICIÓN DE LAS ESTRATEGIAS

class StrategyAlfabetica(RecomendadorStrategy):
    '''
    TAD StrategyAlfabetica (DESCRIPCION: Estrategia que busca recomendaciones siguiendo un órden lexicográfico.
    OPERACIONES: aplicarAlgoritmo())
    '''

    def aplicarAlgoritmo(self, estadisticos, catalogo):
        '''
        Efecto: Método que ordena el catálogo alfabéticamente y luego recorre el catálogo ordenado buscando la primera coincidencia con los estadísticos de la sesión.
        Diferenciamos entre el caso de que el catálogo sea de artistas o de canciones/playlist, ya que en el primer caso se ordena por el atributo "nombre" y en el segundo por el atributo "título".
        Devuelve la primera coincidencia que encuentra o None si no encuentra ninguna.
        '''
        
        if not catalogo:
            return None

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
        '''
        Efecto: Método que ordena el catálogo por fecha de forma descendente y luego recorre el catálogo ordenado buscando la primera coincidencia con los estadísticos de la sesión.
        Esto hace que se prioricen los elementos más recientes en el tiempo. Devuelve la primera coincidencia que encuentra o None si no encuentra ninguna.
        '''
        
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
        '''
        Efecto: Método que selecciona elementos al azar del catálogo hasta encontrar un acierto. Para evitar un bucle infinito, se crea una copia del
        catalogo original y se van eliminando los elementos que ya se han seleccionado. De esta forma, si se encuentra un acierto, se devuelve el elemento coincidente, 
        y si se han seleccionado todos los elementos del catálogo sin encontrar ningún acierto, el método devuelve None.
        '''
        
        disponibles = list(catalogo)
        while disponibles:
            elegido = random.choice(disponibles)
            if self.match(estadisticos,elegido):
                return elegido
            disponibles.remove(elegido)
        return None

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
        '''
        Efecto: Método abstracto que procesa los estadísticos de la sesión. Cada clase concreta de esta cadena implementará este método para calcular
        la media o desviación y luego pasará el resultado al siguiente eslabón de la cadena si existe. 
        '''
        pass



# Desarrollo de las clases de la CHAIN OF RESPONSABILITY


class CalculadorMedia(CalculadorEstadistico):
    '''
    TAD CalculadorMedia (DESCRIPCION: Parte de la cadena que calcula la media atrimética de los atributos sonoros y sentimentales
    de las canciones en la cola e la sesión. Si hay un manejador siguiente, le pasa el diccionario resultante. OPERACIONES: manejar_sesion())
    '''

    def manejar_sesion(self, sesion, estadisticos = None):
        '''
        Efecto: Méotodo que calcula la media de los atributos sonoros y sentimentales de las canciones en la cola de la sesión. Para cada atributo, se recorre la cola de 
        la sesión y se suma el valor del atributo en cada canción, para luego dividirlo entre el número de canciones en la sesión. El resultado se almacena en un diccionario 
        con la siguiente estructura: {atributos_son: {atributo1: {'media': valor}, atributo2: {'media': valor}, ...}, atributos_sent: {atributo1: {'media': valor}, atributo2: {'media': valor}, ...}}.
        Si no hay estadisicos de la sesión, se devuelve un diccionario vacío.
        '''
        
        if len(sesion)==0:
            raise SesionVacia('No se puede calcular la media. La sesión no tiene canciones')

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
        '''
        Efecto: Método que calcula la desviación típica de los atributos de la sesión. Para cada atributo, se recorre la cola de la sesión y se suma el cuadrado de la diferencia 
        entre el valor del atributo en cada canción y la media del atributo, para luego dividirlo entre el número de canciones en la sesión y sacar la raíz cuadrada. 
        El resultado se almacena en el mismo diccionario que el calculador de media, añadiendo una nueva clave "std" a cada atributo con el valor de la desviación típica. 
        Si no hay estadisicos de la sesión, se devuelve un diccionario vacío.
        '''
        
        if estadisticos is None:
            estadisticos = {'atributos_son': {}, 'atributos_sent': {}}
        
        n = len(sesion)
        if n == 0:
            raise SesionVacia('No se puede calcular la desviación típica. La sesión no tiene canciones')
        

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
        '''
        Efecto: Método que añade una canción a la cola de la sesión. Si la cola ya tiene 10 canciones, se elimina la canción más antigua.
        '''
        
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
        '''
        Efecto: Método que busca una canción en el catalogo a partir de u id_cancion. Devuelve una lista con la canción encontrada.
        '''        
        res = list(filter(lambda c: c.id == id_cancion, self.canciones))
        return res
    
    def anyadir_cancion(self, cancion):
        '''
        Efecto: Añadir una canción al catálogo
        '''
        self.canciones.append(cancion)
        
    def anyadir_playlist(self, playlist):
        '''
        Efecto: Añadir una playlist al catálogo
        '''
        self.playlists.append(playlist)

    def anyadir_artista(self, artista):
        '''
        Efecto: Añadir un artista al catálogo
        '''
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
        '''
        Efecto: Método que devuelve el título de la cancion.
        '''
        return self.titulo
    
    def get_fecha(self):
        '''
        Efecto: Método que devuelve la fecha de la cancion
        '''
        return self.fecha

    def get_atributos_sonoros(self):
        '''
        Efecto: Método que devuelve los atributos sonoros de la canción.
        '''
        return {**self.atributos_son}
    
    def get_atributos_sentimentales(self):
        '''
        Efecto: Método que devuelve los atributos sentimentales de la canción.
        '''
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
        if n==0:
            raise ValueError(f'No se puede calcular atributos para {self.nombre}: no tiene canciones')
        
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
        '''
        Efecto: Método que devuelve el título de la playlist.
        '''
        return self.titulo
    
    def get_fecha(self):
        '''
        Efecto: Método que devuelve la fecha de la playlist.
        '''
        return self.fecha
    
    def actualizar_media_atributos(self):
        '''
        Efecto: Método que calcula la media de los atributos sonoros y sentimentales de todas las canciones de la playlist. Para cada atributo, 
        se recorre la lista de canciones y se suma el valor del atributo en cada canción, para luego dividirlo entre el número de canciones en la playlist. 
        El resultado se almacena en los diccionarios atributos_son y atributos_sent de la playlist.
        '''
        n = len(self.canciones)
        if n==0:
            raise ValueError(f'No se puede calcular atributos para {self.nombre}: no tiene canciones')
        
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
    def __init__(self, estrategia, catalogo):
        if self._unicaInstancia is not None:
            raise SingletonException('Debes instanciar desde obtener_instancia()')

        self.catalogo = catalogo
        self.configuracion =  {'artistas':False,'playlists':False, 'estrategia': estrategia}
        self.sesion = SesionEscucha()
    
    @classmethod
    def obtener_instancia(cls, estrategia, catalogo = None):
        '''
        Efecto: Método que devuelve la instancia única del Recomendador. Si no existe, la crea.
        '''
        if cls._unicaInstancia is None:
            cls._unicaInstancia = cls(estrategia, catalogo)
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
            raise IdInexistente('La canción no existe en el catálogo')
    
    def recomendar(self):
        decorador = RecomendacionCancion()

        if self.configuracion['artistas']:
            decorador = DecoradorArtistas(decorador)
        if self.configuracion['playlists']:
            decorador = DecoradorPlayList(decorador)
        
        return decorador.generar_recomendacion(self.catalogo, self.sesion.estadisticos, self.configuracion['estrategia'])
            

# DECORADOR


  


class Generador(metaclass=ABCMeta):
    '''
	TAD Generador (DESCRIPCION: Clase abstracta que define la interfaz base para cualquier generador.
	No puede ser instanciada directamente)
	'''  
        
    @abstractmethod
    def generar_recomendacion(self):
        '''
        Efecto: Método que genera una recomendación utilizando la estrategia de búsqueda proporcionada.
        '''
        pass



class DecoradorRecomendacion(Generador):
    ''' 
    TAD DecoradorRecomendacion (DESCRIPCIÓN: Clase base para añadir capas a la recomendación. Por defecto se debe
    recomendar una canción. VALORES: generador(objeto))
    '''

    def __init__(self, generador : Generador):
        self.generador = generador


    @abstractmethod
    def generar_recomendacion(self):
        pass



class RecomendacionCancion(Generador):
    def __init__(self, cancion : Cancion):
        self.cancion = cancion

    def generar_recomendacion(self, catalogo, estadisticos, estrategia, recomendaciones = None):
        if recomendaciones is None:
            recomendaciones = dict()
        cancion = estrategia.aplicarAlgoritmo(estadisticos, catalogo.canciones) # Tener en cuenta lo de playlist/listas
        recomendaciones['cancion'] = cancion
        return recomendaciones


        
class DecoradorPlayList(DecoradorRecomendacion):
    '''
    TAD DecoradorPlayList (DESCRIPCIÓN: Extensión que añade a recomendar una playlist a la recomendación base.
    OPERACIONES: generar_recomendacion, match_playlist.
    '''
    def generar_recomendacion(self, catalogo, estadisticos, estrategia, recomendaciones = None):
        if recomendaciones is None:
            recomendaciones = {}
        playlist = estrategia.aplicarAlgoritmo(estadisticos, catalogo.playlists)
        recomendaciones['playlist'] = playlist
        return self.generador.generar_recomendacion(catalogo, estadisticos, estrategia, recomendaciones)
    

class DecoradorArtistas(DecoradorRecomendacion):
    
    def generar_recomendacion(self, catalogo, estadisticos, estrategia, recomendaciones = None):
        if recomendaciones is None:
            recomendaciones = {}

        artista = estrategia.aplicarAlgoritmo(estadisticos, catalogo.artistas)
        recomendaciones['artista'] = artista
        return self.generador.generar_recomendacion(catalogo, estadisticos, estrategia, recomendaciones)

# CLASE CON LA QUE INTERACTÚA EL USUARIO
class PlataformaStreaming:
    
    def __init__(self, catalogo):
        estrategia_predet = StrategyAleatoria()
        self.recomendador = Recomendador.obtener_instancia(estrategia_predet, catalogo)
    
    def establecer_configuracion(self, artistas, playlists):
        self.recomendador.configuracion['artistas'] = artistas
        self.recomendador.configuracion['playlists'] = playlists
    
    def enviar_escucha(self, id, date):
        self.recomendador.recibir_escucha(id, date)
        return (id, date)
    
    def cambiar_estrategia(self, estrategia):
        self.recomendador.configuracion['estrategia'] = estrategia
    
    def solicitar_recomendacion(self):
        recomendaciones = self.recomendador.recomendar()
        
        if recomendaciones.get('cancion') is None:
            raise RecomendacionNoEncontrada('No se ha encontrado canción para recomendar')
            

        print('La canción recomendada es', recomendaciones['cancion'].get_titulo())

        if self.recomendador.configuracion['artistas']:
            print('El artista recomendado es', recomendaciones['artista'].get_nombre())

        if self.recomendador.configuracion['playlists']:
            print('La playlist recomendada es', recomendaciones['playlist'].get_titulo())

            



if __name__ == '__main__':
    '''
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
    '''
    

    if __name__ == "__main__":

    # Crear canciones
        c1 = Cancion(1, "A", 2020,{"ritmo": 5, "tono": 6}, {"energia": 7, "felicidad": 6})

        c2 = Cancion(2, "B", 2021,
                    {"ritmo": 6, "tono": 5},
                    {"energia": 6, "felicidad": 7})

        c3 = Cancion(3, "C", 2022,
                    {"ritmo": 2, "tono": 3},
                    {"energia": 2, "felicidad": 3})

        # Crear catálogo
        catalogo = CatalogoStreaming()
        catalogo.anyadir_cancion(c1)
        catalogo.anyadir_cancion(c2)
        catalogo.anyadir_cancion(c3)

        # Crear artista
        artista = Artista("Artista1", 2022, [c1, c2])
        catalogo.anyadir_artista(artista)

        # Crear playlist
        playlist = Playlist("Mix1", 2023, [c1, c2])
        catalogo.anyadir_playlist(playlist)

        # Crear plataforma
        plataforma = PlataformaStreaming(catalogo)

        # Configuración
        plataforma.establecer_configuracion(artistas=True, playlists=False)

        # Simular escuchas
        plataforma.enviar_escucha(1, "2025-01-01")
        plataforma.enviar_escucha(2, "2025-01-02")

        # Pedir recomendación
        plataforma.solicitar_recomendacion()

       

            

    

        
    
    