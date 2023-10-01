# PROHIBIDO HACER ONELINERS

## PREGUNTAS EN CLASE

## Args
No importa el orden de los argumentos 
Default stop and wait

## Header
### V1
- Formato:
    - **2 bits**  
    0: REQUEST (UPLOAD=0, DOWNLOAD=1, ack= 2, solicitud de files disponibles = 3)
    - **32 u 64 bytes:**  
    Nombre del archivo (64 para los chinos)
    - **X bytes para 2gb**:  
    Longitud del archivo (por ahora no es necesaria) //cantidad de paquetes (dividido el tam max)
    - **2 bytes**:  
    Longitud [0-65535] del payload variable con tope superior
    - **Hacer la cuenta:**
    Sequence number 
    - Hash

    - **A decidir**: se manda un ack y despues el archivo o directamente el archivo?

    - **Payload bytes:**  
    Contenido del archivo (solo si request es UPLOAD)

## TESTS

### Necesario
1- Varios clientes operando con el mismo archivo
1- revistar todas las constantes (timeout, header, etc)

2- falta testear todo(no necesariamente tests de codigo, Test perdida de handshake, tests options, que pasa si subis directorios)

3- comcast
3- wireshark 

4- que te agarre una direccion disponible

5- correr linter: https://flake8.pycqa.org/en/latest/


### Lujo
Servidor ofrece lo que esta subido
barra descarga
agregar el nombre del usuario como "carpeta"
Aclarar que != usuarios no pueden subir disitnas cosas 

### ultra shanpan
appendear un header a llos archivos para hacer continuacion de descarga


## DONE
agregar el window al send
1- nombre de archivos repetidos en sv, que se hace? -reemplazar
1- interrupcion de descarga/subida                  -descarta_lo_guardado
1- graceful_finish_server                           -en algun momento del ciclo del while chequear la terminal (esperar a los demas threads)
## PRIORIDAD


## INFORME pongan su nombre hijos deperra

https://docs.google.com/document/d/1S2-F9Iz4kt0NOC0vLm8QkQX6uunWNbiO0uwa1qXId70/edit