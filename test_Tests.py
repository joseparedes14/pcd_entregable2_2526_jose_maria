import pytest 
import asyncio
import codigop2 as Streaming

#------ Test para el patrón Strategy-------

def test_strategy_alfabetica():
    #debería devolver la canción con el título que va primero alfabéticamente
    estadisticos = {
        'atributos_son':{'ritmo': {'media':5}, 'tono':{'media':4}},
        'atributos_sent': {'energia': {'media': 6}, 'felicidad': {'media':5}}
    }
    Cancion1 = Streaming.Cancion(1,'Prueba1',2026,{'ritmo':5.2,'tono':4.1}, {'energia':6.1, 'felicidad':4.9})
    Cancion2 = Streaming.Cancion(2,'Prueba2',2026,{'ritmo':5.2,'tono':4.1}, {'energia':6.1, 'felicidad':4.9})
    estrategia = Streaming.StrategyAlfabetica()
    rdo = estrategia.aplicarAlgoritmo(estadisticos, [Cancion1, Cancion2])
    assert rdo.titulo == 'Prueba1'


def test_strategy_temporal():
    # debería devolver la canción con la fecha más reciente
    estadisticos = {
        'atributos_son':{'ritmo': {'media':5}, 'tono':{'media':4}},
        'atributos_sent': {'energia': {'media': 6}, 'felicidad': {'media':5}}
    }
    Cancion1 = Streaming.Cancion(1,'Prueba1',2020,{'ritmo':5.2,'tono':4.1}, {'energia':6.1, 'felicidad':4.9})
    Cancion2 = Streaming.Cancion(2,'Prueba2',2026,{'ritmo':5.2,'tono':4.1}, {'energia':6.1, 'felicidad':4.9})
    estrategia = Streaming.StrategyTemporal()
    rdo = estrategia.aplicarAlgoritmo(estadisticos, [Cancion1, Cancion2])
    assert rdo.fecha == 2026 

def test_strategy_aleatoria():
    # deberia devolver la única que hay, pues como es random no podemos saber el resultado
    estadisticos = {
        'atributos_son':{'ritmo': {'media':5}, 'tono':{'media':4}},
        'atributos_sent': {'energia': {'media': 6}, 'felicidad': {'media':5}}
    }
    Cancion1 = Streaming.Cancion(1,'Prueba1',2020,{'ritmo':5.2,'tono':4.1}, {'energia':6.1, 'felicidad':4.9})
    estrategia = Streaming.StrategyAleatoria()
    rdo = estrategia.aplicarAlgoritmo(estadisticos, [Cancion1])
    assert rdo.fecha == 2020 


@pytest.mark.asyncio
async def test_strategy_compuesta_sin_resultados():
    estrategia = Streaming.StrategyCompuesta()
    estadisticos = {'atributos_son': {'r': {'media':5}}, 'atributos_sent': {'f': {'media': 5}}}
    rdo = await estrategia._buscar_concurrente(estadisticos, [])
    assert rdo is None #este none la plataforma straming lo convertirá a error



# ----- Test para la chain of responsability -----

@pytest.mark.asyncio #esto es necesario para probar funcioones definidas con asyncio
async def test_calculadora_media():
    Cancion1 = Streaming.Cancion(1,'Prueba1',2026,{'ritmo':5,'tono':5}, {'energia':6, 'felicidad':5})
    Cancion2 = Streaming.Cancion(2,'Prueba2',2026,{'ritmo':7,'tono':8}, {'energia':4, 'felicidad':2})
    calculadora = Streaming.CalculadorMedia()
    res = await calculadora.manejar_sesion([Cancion1,Cancion2])
    assert res['atributos_son']['ritmo']['media'] == 6.0
    assert res['atributos_son']['tono']['media'] == 6.5
    assert res['atributos_sent']['energia']['media'] == 5.0 
    assert res['atributos_sent']['felicidad']['media'] == 3.5
    

@pytest.mark.asyncio #esto es necesario para probar funcioones definidas con asyncio
async def test_calculadora_desviacion():
    Cancion1 = Streaming.Cancion(1,'Prueba1',2026,{'ritmo':5,'tono':5}, {'energia':6, 'felicidad':5})
    Cancion2 = Streaming.Cancion(2,'Prueba2',2026,{'ritmo':7,'tono':8}, {'energia':4, 'felicidad':2})
    estadisticos_previos = {
        'atributos_son': {'ritmo':{'media':6.0}, 'tono':{'media':6.5}},
        'atributos_sent': {'energia': {'media':5}, 'felicidad':{'media':3.5}}
    }
    calculadora = Streaming.CalculadorDesviacion()
    res = await calculadora.manejar_sesion([Cancion1,Cancion2], estadisticos_previos)
    assert res['atributos_son']['ritmo']['std'] == 1.0
    assert res['atributos_son']['tono']['std'] == 1.5
    assert res['atributos_sent']['energia']['std'] == 1.0
    assert res['atributos_sent']['felicidad']['std'] == 1.5   


# ------ Test para Artista y Playlist ------
def test_artista_medias():
    Cancion1 = Streaming.Cancion(1,'Prueba1',2026,{'ritmo':5,'tono':5}, {'energia':6, 'felicidad':5})
    Cancion2 = Streaming.Cancion(2,'Prueba2',2026,{'ritmo':7,'tono':8}, {'energia':4, 'felicidad':2})
    artista = Streaming.Artista('Prueba3', 2026, [Cancion1,Cancion2])
    assert artista.atributos_son['ritmo'] == 6.0
    assert artista.atributos_son['tono'] == 6.5
    assert artista.atributos_sent['energia'] == 5.0
    assert artista.atributos_sent['felicidad'] == 3.5

def test_playlist_calculo_medias():
    c1 = Streaming.Cancion(1, 'S1', 2026, {'ritmo': 100}, {'energia': 100})
    playlist = Streaming.Playlist('Mix', 2026, [c1])
    assert playlist.atributos_son['ritmo'] == 100.0
        

# ----- Test para el singleton ----

def test_singleton():
    # vamos a limpiar la instancia antes de empezar
    Streaming.Recomendador._unicaInstancia = None
    catalogo = Streaming.CatalogoStreaming()
    estrategia = Streaming.StrategyAleatoria()
    recomendador1= Streaming.Recomendador.obtener_instancia(estrategia,catalogo)
    recomendador2 = Streaming.Recomendador.obtener_instancia(estrategia,catalogo)
    assert recomendador1 is recomendador2 #deberia devolver true
   
   
# --- Test para el catálogo ----
def test_catalogo_streaming():
    # prueba la busqueda por id
    cat = Streaming.CatalogoStreaming()
    c = Streaming.Cancion(99, 'Test', 2026, {}, {})
    cat.anyadir_cancion(c)
    resultado = cat.buscar(99)
    assert resultado[0].titulo == 'Test'


# ---- Test para la sesion de escucha ----

def test_sesion_escucha():
    # vamos a crear una sesion de escucha y ver si se añaden las canciones correctamente
    sesion = Streaming.SesionEscucha()
    c1 = Streaming.Cancion(1, 'S1', 2026, {'ritmo': 100}, {'energia': 100})
    c2 = Streaming.Cancion(2, 'S2', 2026, {'ritmo': 50}, {'energia': 50})
    sesion.anyadir_cancion(c1)
    sesion.anyadir_cancion(c2)
    assert len(sesion.cola) == 2

# --- Test plataforma streaming --- 
def test_plataforma_streaming():
    #vemos si funciona la 
    catalogo = Streaming.CatalogoStreaming()
    plataforma = Streaming.PlataformaStreaming(catalogo)
    plataforma.establecer_configuracion(artistas=True, playlists=True)
    assert plataforma.recomendador.configuracion['artistas'] == True
    assert plataforma.recomendador.configuracion['playlists'] == True

# ----- Test para RecomendacionCancion ------

def test_recomendacioncancion():
    # Probamos si la salida tiene el formato esperado y si lo que hay dentro es un objeto cancion : {'cancion': obj_cancion}
    generador = Streaming.RecomendacionCancion()
    catalogo = Streaming.CatalogoStreaming()
    c1 = Streaming.Cancion(1, 'S1', 2026, {'ritmo':7,'tono':8}, {'energia':4, 'felicidad':2})
    catalogo.anyadir_cancion(c1)
    estrategia = Streaming.StrategyTemporal()
    estadisticos = {'atributos_son': {'ritmo': {'media': 7}, 'tono': {'media': 8}}, 
                    'atributos_sent': {'energia': {'media': 4}, 'felicidad': {'media': 2}}}
    resultado = generador.generar_recomendacion(catalogo,estadisticos,estrategia)
    assert 'cancion' in resultado
    assert resultado['cancion'].titulo == 'S1'    

def test_decoradorplaylist():
    # probamos si el diccionario devuelto tiene la clave playlist y cancion y el objeto guardado es realmente una playlist
    catalogo = Streaming.CatalogoStreaming()
    c1 = Streaming.Cancion(1, 'S1', 2026, {'ritmo': 5, 'tono': 5}, {'energia': 5, 'felicidad': 5})
    playlist_esperada = Streaming.Playlist("Mix 2026", 2026, [c1])
    catalogo.anyadir_playlist(playlist_esperada)
    base = Streaming.RecomendacionCancion()
    decorador = Streaming.DecoradorPlayList(base)
    estrategia = Streaming.StrategyAlfabetica()
    estadisticos = {'atributos_son': {'ritmo': {'media': 5},'tono': {'media': 5},},
                    'atributos_sent': {'energia': {'media': 5},'felicidad': {'media': 5}}}
    resultado = decorador.generar_recomendacion(catalogo,estadisticos,estrategia)
    assert 'cancion' in resultado
    assert 'playlist' in resultado
    assert isinstance(resultado['playlist'], Streaming.Playlist) 
    
def test_decoradorartistas():
    # probamos si el diccionario devuelto tiene la clave artista y cancion y el objeto guardado es realmente un artista
    catalogo = Streaming.CatalogoStreaming()
    c1 = Streaming.Cancion(1, 'S1', 2026, {'ritmo': 5, 'tono': 5}, {'energia': 5, 'felicidad': 5})
    artista_esperada = Streaming.Artista("Maria", 2026, [c1])
    catalogo.anyadir_artista(artista_esperada)
    base = Streaming.RecomendacionCancion()
    decorador = Streaming.DecoradorArtistas(base)
    estrategia = Streaming.StrategyAlfabetica()
    estadisticos = {'atributos_son': {'ritmo': {'media': 5},'tono': {'media': 5},},
                    'atributos_sent': {'energia': {'media': 5},'felicidad': {'media': 5}}}
    resultado = decorador.generar_recomendacion(catalogo,estadisticos,estrategia)
    assert 'cancion' in resultado
    assert 'artista' in resultado
    assert isinstance(resultado['artista'], Streaming.Artista) 
    

    
    
    
