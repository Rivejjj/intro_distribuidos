# PROHIBIDO HACER ONELINERS

## PREGUNTAS EN CLASE

## Args
No importa el orden de los argumentos 


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
falta testear todo
Test perdida de handshake

## PRIORIDAD
    - Handshake
    - FIN