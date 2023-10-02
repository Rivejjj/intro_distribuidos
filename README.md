# Cliente y Servidor de Aplicación de Línea de Comandos (CLI) para Transferencia de Archivos

Este conjunto de herramientas CLI consta de un cliente y un servidor que te permiten gestionar la transferencia de archivos de manera sencilla. El cliente ofrece comandos para cargar y descargar archivos desde el servidor, mientras que el servidor proporciona un servicio de almacenamiento y descarga de archivos.

## Cliente: Comandos Disponibles

### Comando `upload`

El comando `upload` se utiliza para enviar un archivo al servidor. A continuación, se muestra la interfaz de línea de comandos para este comando:

```bash
python3 upload -h
```

#### Opciones Disponibles:

- `-h`, `--help`: Muestra un mensaje de ayuda y sale.
- `-v`, `--verbose`: Aumenta la verbosidad de la salida.
- `-q`, `--quiet`: Reduce la verbosidad de la salida.
- `-H`, `--host`: Especifica la dirección IP del servidor.
- `-p`, `--port`: Especifica el puerto del servidor.
- `-s`, `--src`: Especifica la ruta del archivo fuente que deseas cargar.
- `-n`, `--name`: Especifica el nombre que se asignará al archivo en el servidor.

### Comando `download`

El comando `download` se utiliza para descargar un archivo desde el servidor. A continuación, se muestra la interfaz de línea de comandos para este comando:

```bash
python3 download -h
```

#### Opciones Disponibles:

- `-h`, `--help`: Muestra un mensaje de ayuda y sale.
- `-v`, `--verbose`: Aumenta la verbosidad de la salida.
- `-q`, `--quiet`: Reduce la verbosidad de la salida.
- `-H`, `--host`: Especifica la dirección IP del servidor.
- `-p`, `--port`: Especifica el puerto del servidor.
- `-d`, `--dst`: Especifica la ruta de destino donde se guardará el archivo descargado.
- `-n`, `--name`: Especifica el nombre del archivo que deseas descargar desde el servidor.

## Servidor: Comando de Inicio

El servidor se inicia utilizando el siguiente comando:

```bash
python3 start-server -h
```

### Opciones Disponibles:

- `-h`, `--help`: Muestra un mensaje de ayuda y sale.
- `-v`, `--verbose`: Aumenta la verbosidad de la salida.
- `-q`, `--quiet`: Reduce la verbosidad de la salida.
- `-H`, `--host`: Especifica la dirección IP del servicio.
- `-p`, `--port`: Especifica el puerto del servicio.
- `-s`, `--storage`: Especifica la ruta del directorio de almacenamiento en el servidor.

## Ejemplos de Uso

A continuación, se presentan algunos ejemplos de uso de los comandos del cliente y el comando de inicio del servidor:

### Ejemplo de Uso de `upload`:

```bash
python3 upload -H 192.168.1.100 -p 8080 -s archivo_local.txt -n archivo_remoto.txt
```

Este comando enviará el archivo `archivo_local.txt` al servidor con la dirección IP `192.168.1.100` y el puerto `8080`. El archivo se guardará en el servidor con el nombre `archivo_remoto.txt`.

### Ejemplo de Uso de `download`:

```bash
python3 download -H 192.168.1.100 -p 8080 -n archivo_remoto.txt -d /ruta/local/
```

Este comando descargará el archivo `archivo_remoto.txt` desde el servidor con la dirección IP `192.168.1.100` y el puerto `8080`, y lo guardará en la ruta local `/ruta/local/`.

### Ejemplo de Inicio del Servidor:

```bash
python3 start-server -H 195.168.10.7 -p 8080 -s /ruta/de/almacenamiento/
```

Este comando iniciará el servidor en la interfaz de red (`195.168.10.7`) en el puerto `8080` y utilizará el directorio `/ruta/de/almacenamiento/` para almacenar archivos.

## Notas Adicionales

- Asegúrate de tener una conexión activa a Internet y que el servidor esté en funcionamiento antes de ejecutar los comandos del cliente.
- Puedes ajustar la verbosidad de la salida según tus preferencias utilizando las opciones `-v` y `-q`.

¡Disfruta utilizando esta aplicación de cliente