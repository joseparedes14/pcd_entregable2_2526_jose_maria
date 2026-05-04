import pytest 
import asyncio
import codigop2 as Streaming

#------ Test para el patrón Strategy-------

def test_match_insuficiente():
    # Solo 3 atributos coinciden (ritmo, energia, felicidad). Tono falla (dif=1)
    # Como 3 no es >3, debe devolver False.
    estadisticos = {
		'atributos_son':{'ritmo': {'media':5}, 'tono':{'media':4}},
		'atributos_sent': {'energia': {'media': 6}, 'felicidad': {'media':5}}
	}
    # Tono es 5, media es 4 -> abs(4-5)=1. No cuenta porque es <1
    Cancion1 = Streaming.Cancion(1,'Prueba1',2026,{'ritmo':5.2,'tono':5}, {'energia':6.1, 'felicidad':4.9})
    estrategia = Streaming.StrategyAlfabetica()

    assert estrategia.match(estadisticos,Cancion1) is False


def test_atributos_incompatibles():
    estadisticos = {
		'atributos_son':{'ritmo': {'media':5}, 'tono':{'media':4}},
		'atributos_sent': {'energia': {'media': 6}, 'felicidad': {'media':5}}
	}
    Cancion_estadistico_diferente = Streaming.Cancion(3,'Prueba3',2026,{'armonia':5.2,'tono':5}, {'energia':6.1, 'felicidad':4.9})
    estrategia = Streaming.StrategyAlfabetica()
    with pytest.raises(Streaming.AtributosIncompatibles):
        estrategia.match(estadisticos,Cancion_estadistico_diferente)

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
    
@pytest.mark.asyncio   
async def test_error_sesion_vacia_calculadoras():
    calculadora_media = Streaming.CalculadorMedia()
    calculadora_std = Streaming.CalculadorDesviacion()
    with pytest.raises(Streaming.SesionVacia):
        await calculadora_media.manejar_sesion([])
    
    with pytest.raises(Streaming.SesionVacia):
        await calculadora_std.manejar_sesion([])
         

# ------ Test para Artista y Playlist ------
def test_artista_medias():
    Cancion1 = Streaming.Cancion(1,'Prueba1',2026,{'ritmo':5,'tono':5}, {'energia':6, 'felicidad':5})
    Cancion2 = Streaming.Cancion(2,'Prueba2',2026,{'ritmo':7,'tono':8}, {'energia':4, 'felicidad':2})
    artista = Streaming.Artista('Prueba3', 2026, [Cancion1,Cancion2])
    assert artista.atributos_son['ritmo'] == 6.0
    assert artista.atributos_son['tono'] == 6.5
    assert artista.atributos_sent['energia'] == 5.0
    assert artista.atributos_sent['felicidad'] == 3.5

def test_artista_error_lista_vacia():
    with pytest.raises(ValueError):
        Streaming.Artista('Artista vacío', 2026, [])

def test_playlist_vacia():
    with pytest.raises(ValueError):
        Streaming.Playlist('Playlist vacia', 2026, [])
        

# ----- Test para el singleton ----

def test_singleton():
    # vamos a limpiar la instancia antes de empezar
    Streaming.Recomendador._unicaInstancia = None
    catalogo = Streaming.CatalogoStreaming()
    estrategia = Streaming.StrategyAleatoria()
    recomendador1= Streaming.Recomendador.obtener_instancia(estrategia,catalogo)
    recomendador2 = Streaming.Recomendador.obtener_instancia(estrategia,catalogo)
    assert recomendador1 is recomendador2 #deberia devolver true
    
def test_recibir_escucha():
    #para ver si lanza el error de ID inexistente
    Streaming.Recomendador._unicaInstancia = None
    catalogo = Streaming.CatalogoStreaming()
    estrategia = Streaming.StrategyTemporal()
    recomendador= Streaming.Recomendador.obtener_instancia(estrategia,catalogo)
    with pytest.raises(Streaming.IdInexistente):
        recomendador.recibir_escucha(1,13022005)


def test_error_instanciacion_sin_metodo():
    Streaming.Recomendador._unicaInstancia = None
    estrategia = Streaming.StrategyAleatoria()
    Streaming.Recomendador.obtener_instancia(estrategia) #esta va bien
    with pytest.raises(Streaming.SingletonException):
        Streaming.Recomendador(estrategia, None) #esto no se puede

def test_error_recomendacion_no_encontrada():
    #vamos a crear dos canciones distintas y pedir una recomendacion pero que no pase el match
    # entonces no recomienda nada
    Streaming.Recomendador._unicaInstancia = None
    Cancion1 = Streaming.Cancion(1,'Pop',2026,{'ritmo':10}, {'felicidad':10})
    catalogo = Streaming.CatalogoStreaming()
    catalogo.anyadir_cancion(Cancion1)
    plataforma = Streaming.PlataformaStreaming(catalogo)
    Cancion2 = Streaming.Cancion(2,'Ondas Alfa',2026,{'ritmo':0}, {'felicidad':0})
    catalogo.anyadir_cancion(Cancion2)
    plataforma.enviar_escucha(2,'2026-05-04')
    with pytest.raises(Streaming.RecomendacionNoEncontrada):
        plataforma.solicitar_recomendacion()

# ---- Test decorador ----

def test_todos_los_decoradores():
    # vemos si mezclamos los 3 decoradores tenemos un diccionario con 3 claves
    Streaming.Recomendador._unicaInstancia = None
    Cancion1 = Streaming.Cancion(1,'Pop',2026,{'ritmo':10}, {'felicidad':10})
    catalogo = Streaming.CatalogoStreaming()
    catalogo.anyadir_cancion(Cancion1)
    catalogo.anyadir_artista(Streaming.Artista('Maria', 2026, [Cancion1]))
    catalogo.anyadir_playlist(Streaming.Playlist('Playlist de Jose', 2026, [Cancion1]))
    
    plataforma = Streaming.PlataformaStreaming(catalogo)
    plataforma.establecer_configuracion(artistas=True, playlists=True)
    plataforma.enviar_escucha(1,'2026-05-05')
    rdo = plataforma.recomendador.recomendar()
    
    assert 'cancion' in rdo
    assert 'artista' in rdo
    assert 'playlist' in rdo
    
   
    
    
    
    
    
