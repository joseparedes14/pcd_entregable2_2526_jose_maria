import pytest 
import asyncio
import codigop2 as Streaming

# Test para el patrón Strategy

def test_match_insuficiente():
    # verificamos si devuelve false cuando tres o menos atributos coinciden
    estadisticos = {
		'atributos_son':{'ritmo': {'media':5}, 'tono':{'media':4}},
		'atributos_sent': {'energia': {'media': 6}, 'felicidad': {'media':5}}
	}
    Cancion1 = Streaming.Cancion(1,'Prueba1',2026,{'ritmo':5,'tono':5}, {'energia':6, 'felicidad':5})
    estrategia = Streaming.StrategyAlfabetica()

    assert estrategia.match(estadisticos,Cancion1) is True

# Test para la chain of responsability

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
    assert res['atributos_sent']['felicidad']['stf'] == 1.5        


