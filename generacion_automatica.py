import random
from codigop2 import Cancion, Playlist, Artista

def poblar_catalogo(catalogo,
                     n_canciones=50,
                     n_artistas=10,
                     n_playlists=10):


    # CANCIONES
    canciones_generadas = []

    for i in range(1, n_canciones + 1):

        cancion = Cancion(
            id=i,
            titulo=f"Song_{i}",
            fecha=random.randint(2018, 2026),

            sonoros={
                "ritmo": random.randint(1, 10),
                "tono": random.randint(1, 10)
            },

            sentimentales={
                "energia": random.randint(1, 10),
                "felicidad": random.randint(1, 10)
            }
        )

        catalogo.anyadir_cancion(cancion)
        canciones_generadas.append(cancion)

    # ARTISTAS

    for i in range(1, n_artistas + 1):

        canciones_artista = random.sample(
            canciones_generadas,
            random.randint(2, 6)
        )

        artista = Artista(
            nombre=f"Artista_{i}",
            fecha=random.randint(2018, 2026),
            canciones=canciones_artista
        )

        catalogo.anyadir_artista(artista)

    # PLAYLISTS


    for i in range(1, n_playlists + 1):

        canciones_playlist = random.sample(
            canciones_generadas,
            random.randint(3, 10)
        )

        playlist = Playlist(
            titulo=f"Playlist_{i}",
            fecha=random.randint(2018, 2026),
            canciones=canciones_playlist
        )

        catalogo.anyadir_playlist(playlist)
