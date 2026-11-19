# Laboratorio de archivos en Industria 4.0

Tres simulaciones con Python y una demostración para GitHub Pages. La web ejecuta una simulación independiente en JavaScript dentro del navegador; no ejecuta Python ni modifica archivos reales. Sus datos se pierden al recargar.

## Python

Requiere Python 3.9 o posterior y utiliza únicamente la biblioteca estándar. Ejecutar `python python/laboratorio.py` para una demostración temporal, o `python python/pruebas.py` para comprobar réplica, búfer, índice y posiciones en bytes. Las clases `Distribuido`, `Edge` e `Indice` reciben un directorio de trabajo donde generan archivos JSON, CSV y TXT reales.

- `Distribuido`: asigna ID positivo por módulo a tres nodos; guarda primario y réplica siguiente. La caída se simula renombrando el archivo y la consulta usa la réplica si el primario no está disponible. Para escribir, ambos nodos deben estar activos.
- `Edge`: guarda en CSV local sin red; al conectar ordena los pendientes por fecha/hora ISO, los agrega al servidor y vacía el búfer. Es una simulación secuencial; no implementa recuperación transaccional ante interrupciones durante la escritura.
- `Indice`: genera 30 líneas UTF-8 en `registros.txt` e índice JSON con metadatos, posición y longitud en bytes. La búsqueda de lote y vibración > 4.0 solo lee `indice.json`; la lectura por posición es una operación adicional.
