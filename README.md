# Implementación de Firewall en Redes Definidas por Software (SDN) con OpenFlow y Mininet

## Introducción
Internet, a pesar de sus fundamentos establecidos en la década de 1960, sigue evolucionando a una velocidad sorprendente. La proliferación de contenido multimedia, el auge del cloud computing y la expansión de dispositivos conectados, especialmente los smartphones, han planteado nuevos desafíos. Con grandes volúmenes de tráfico y la centralización de datos en enormes datacenters, surge la necesidad de utilizar los recursos de manera más eficiente y adaptarse a las cambiantes demandas. Este proyecto se enfoca en la implementación de soluciones utilizando OpenFlow y las Redes Definidas por Software (SDN) para lograr una distribución de paquetes más flexible y dinámica.

## Propuesta de Trabajo
El objetivo principal de este proyecto es construir una topología dinámica que utilice OpenFlow para implementar un Firewall a nivel de capa de enlace. La emulación del comportamiento de la topología se realizará mediante Mininet. El proyecto se compone de varios pasos y requisitos, cada uno introduciendo aspectos específicos del desarrollo.

A continuación, se presentará una guía paso a paso para lograr la implementación exitosa del Firewall en la capa de enlace utilizando OpenFlow y Mininet.

## Requisitos

- Python 2
- Mininet
- POX (controlador OpenFlow)

## Configuración del Entorno Python2

En este proyecto, se utilizará un entorno virtual de Python2 para garantizar la compatibilidad con las herramientas y bibliotecas específicas. A continuación, se proporciona una guía paso a paso para crear y activar el entorno virtual:

1. **Instalación de `virtualenv` (si no está instalado):**
   ```bash
   pip install virtualenv
   ```

2. **Creación del Entorno Virtual:**
   ```bash
   virtualenv -p /usr/bin/python2.7 myenv
   ```

   Esto creará un entorno virtual llamado `myenv` utilizando Python 2.7.

3. **Activación del Entorno Virtual:**
   - En sistemas Linux/Mac:
     ```bash
     source myenv/bin/activate
     ```
   - En sistemas Windows (PowerShell):
     ```bash
     .\myenv\Scripts\Activate
     ```

   Al activar el entorno virtual, el indicador de la terminal cambiará para indicar que estás dentro del entorno virtual.

4. **Instalación de Dependencias:**
   Asegúrate de instalar todas las dependencias necesarias dentro del entorno virtual:
   ```bash
   pip install <lista de dependencias>
   ```

   Reemplaza `<lista de dependencias>` con las bibliotecas necesarias para tu proyecto.

Con estos pasos, habrás configurado un entorno virtual de Python2 listo para ejecutar el proyecto sin interferir con otras versiones de Python instaladas en tu sistema.

Para desactivar el entorno virtual de Python2, simplemente ejecuta el siguiente comando en tu terminal:

- En sistemas Linux/Mac:

```bash
deactivate
```

- En sistemas Windows (PowerShell):

```bash
deactivate
```

Después de ejecutar este comando, el indicador de la terminal volverá al estado anterior, indicando que estás fuera del entorno virtual. Ten en cuenta que debes desactivar el entorno virtual cuando hayas terminado de trabajar en tu proyecto.

## Instalación y Ejecución de POX

POX, un framework de controlador OpenFlow en Python, es esencial para implementar controladores SDN. Aquí están las instrucciones para instalarlo y ejecutarlo:

### Instalación de POX:

1. **Clonar el Repositorio:**
   - Abre una terminal y navega al directorio donde deseas instalar POX.
   - Ejecuta el siguiente comando para clonar el repositorio POX desde GitHub:

     ```bash
     git clone https://github.com/noxrepo/pox.git
     ```

#### Ejecución de POX:

1. **Ejecutar un Módulo Específico:**
   - Navega al directorio de POX en la terminal.
   - Ejecuta POX con un módulo específico. Por ejemplo, para el módulo de spanning tree:

     ```bash
     ./pox.py samples.spanning_tree
     ```

     Asegúrate de especificar el nombre correcto del módulo que deseas ejecutar.

**Nota:** El comando para ejecutar POX y aplicar spanning tree es temporal y deberá ser cambiado según las indicaciones de la cátedra.

## Ejecución

1. Clona este repositorio en tu máquina local:

   ```bash
   git clone git@github.com:Rivejjj/intro_distribuidos.git
   git checkout tp2
   cd intro_distribuidos
   ```

2. Ejecuta la topología personalizada con Mininet:
Para ejecutar la topología personalizada con Mininet, sigue estos pasos. Por defecto, la topología tiene 4 switches dinámicos.

```bash
sudo mn --custom topology.py --topo myTopo --arp --mac --switch ovsk --controller remote
```

Si deseas especificar la cantidad de switches dinámicos, utiliza el siguiente comando, reemplazando `<cant_switchs>` con el número deseado:

```bash
sudo mn --custom topology.py --topo myTopo,10 --arp --mac --switch ovsk --controller remote
```

Este comando te permitirá personalizar la topología según tus necesidades, ajustando la cantidad de switches dinámicos según lo que requieras para tus pruebas y experimentos.


3. Abre otra terminal y ejecuta el controlador POX con la funcionalidad de spanning tree:

   ```bash
   ./pox.py samples.spanning_tree
   ```

**Nota:** El comando para ejecutar POX y aplicar spanning tree es temporal y deberá ser cambiado según las indicaciones de la cátedra.

## Personalización

- Puedes modificar la topología en el archivo `topology.py` para adaptarla a tus necesidades.
- Reemplaza el comando de POX según las instrucciones de la cátedra.

¡Disfruta explorando y experimentando con tu topología personalizada en Mininet!
