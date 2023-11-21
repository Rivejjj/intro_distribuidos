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

#### Ejecución de POX con Firewall Personalizado:

1. **Configuración inicial:**
   - Mueve el archivo `firewall.py` a la carpeta `pox` del directorio POX.
   - Accede al directorio POX desde la terminal.

2. **Ejecución con Firewall Personalizado:**
   - Utiliza el siguiente comando para ejecutar POX con nuestro firewall y el módulo de aprendizaje de nivel 2 (`forwarding.l2_learning`):

     ```bash
     pox/pox.py firewall forwarding.l2_learning
     ```

   - Asegúrate de que el archivo `firewall.py` está correctamente ubicado en la carpeta `pox`. Este comando iniciará POX con nuestro firewall personalizado y el módulo de aprendizaje de nivel 2 para la red definida.


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
sudo mn --custom topology.py --topo myTopo,<cant_switchs> --arp --mac --switch ovsk --controller remote
```

Este comando te permitirá personalizar la topología según tus necesidades, ajustando la cantidad de switches dinámicos según lo que requieras para tus pruebas y experimentos.


3. Abre otra terminal y ejecuta el controlador POX con la funcionalidad de spanning tree:

   ```bash
   pox/pox.py forwarding.l2_learning firewall --rule=rules.json
   ```

**Nota:** El comando para ejecutar POX y aplicar spanning tree es temporal y deberá ser cambiado según las indicaciones de la cátedra.

## Personalización

- Puedes modificar la topología en el archivo `topology.py` para adaptarla a tus necesidades.
- Reemplaza el comando de POX según las instrucciones de la cátedra.

¡Disfruta explorando y experimentando con tu topología personalizada en Mininet!







Client/Server:
  -b, --bandwidth #[kmgKMG | pps]  bandwidth to send at in bits/sec or packets per second
  -e, --enhancedreports    use enhanced reporting giving more tcp/udp and traffic information
  -f, --format    [kmgKMG]   format to report: Kbits, Mbits, KBytes, MBytes
  -i, --interval  #        seconds between periodic bandwidth reports
  -l, --len       #[kmKM]    length of buffer in bytes to read or write (Defaults: TCP=128K, v4 UDP=1470, v6 UDP=1450)
  -m, --print_mss          print TCP maximum segment size (MTU - TCP/IP header)
  -o, --output    <filename> output the report or error message to this specified file
  -p, --port      #        server port to listen on/connect to
  -u, --udp                use UDP rather than TCP
      --udp-counters-64bit use 64 bit sequence numbers with UDP
  -w, --window    #[KM]    TCP window size (socket buffer size)
  -z, --realtime           request realtime scheduler
  -B, --bind <host>[:<port>][%<dev>] bind to <host>, ip addr (including multicast address) and optional port and device
  -C, --compatibility      for use with older versions does not sent extra msgs
  -M, --mss       #        set TCP maximum segment size (MTU - 40 bytes)
  -N, --nodelay            set TCP no delay, disabling Nagle's Algorithm
  -S, --tos       #        set the socket's IP_TOS (byte) field

Server specific:
  -s, --server             run in server mode
  -t, --time      #        time in seconds to listen for new connections as well as to receive traffic (default not set)
      --udp-histogram #,#  enable UDP latency histogram(s) with bin width and count, e.g. 1,1000=1(ms),1000(bins)
  -B, --bind <ip>[%<dev>]  bind to multicast address and optional device
  -H, --ssm-host <ip>      set the SSM source, use with -B for (S,G) 
  -U, --single_udp         run in single threaded UDP mode
  -D, --daemon             run the server as a daemon
  -V, --ipv6_domain        Enable IPv6 reception by setting the domain and socket to AF_INET6 (Can receive on both IPv4 and IPv6)

Client specific:
  -c, --client    <host>   run in client mode, connecting to <host>
  -d, --dualtest           Do a bidirectional test simultaneously
      --ipg                set the the interpacket gap (milliseconds) for packets within an isochronous frame
      --isochronous <frames-per-second>:<mean>,<stddev> send traffic in bursts (frames - emulate video traffic)
  -n, --num       #[kmgKMG]    number of bytes to transmit (instead of -t)
  -r, --tradeoff           Do a bidirectional test individually
  -t, --time      #        time in seconds to transmit for (default 10 secs)
  -B, --bind [<ip> | <ip:port>] bind ip (and optional port) from which to source traffic
  -F, --fileinput <name>   input the data to be transmitted from a file
  -I, --stdin              input the data to be transmitted from stdin
  -L, --listenport #       port to receive bidirectional tests back on
  -P, --parallel  #        number of parallel client threads to run
  -R, --reverse            reverse the test (client receives, server sends)
  -T, --ttl       #        time-to-live, for multicast (default 1)
  -V, --ipv6_domain        Set the domain to IPv6 (send packets over IPv6)
  -X, --peer-detect        perform server version detection and version exchange
  -Z, --linux-congestion <algo>  set TCP congestion control algorithm (Linux only)

Miscellaneous:
  -x, --reportexclude [CDMSV]   exclude C(connection) D(data) M(multicast) S(settings) V(server) reports
  -y, --reportstyle C      report as a Comma-Separated Values
  -h, --help               print this message and quit
  -v, --version            print version information and quit

[kmgKMG] Indicates options that support a k,m,g,K,M or G suffix
Lowercase format characters are 10^3 based and uppercase are 2^n based
(e.g. 1k = 1000, 1K = 1024, 1m = 1,000,000 and 1M = 1,048,576)

The TCP window size option can be set by the environment variable
TCP_WINDOW_SIZE. Most other options can be set by an environment variable
IPERF_<long option name>, such as IPERF_BANDWIDTH.

Source at <http://sourceforge.net/projects/iperf2