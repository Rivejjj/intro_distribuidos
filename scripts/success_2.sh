#!/bin/bash

# En otra terminal ejecutar: pox/pox.py forwarding.l2_learning firewall --rule=rules.json
# Run: chmod +x sucess_1.sh
# Run: ./sucess_1.sh <num switch>

# Este script ejecuta una simulación de red Mininet con una topología personalizada
# para verificar, utilizando iperf, que el host 4 como servidor se puede conectar con el
# host 1 como cliente y el host 3 como servidor se puede conectar con el host 2 como cliente

# Cambiamos al directorio padre que contiene el script y otros archivos necesarios
cd ..

# Comprobamos si se proporciona el número de hosts como argumento
if [ "$#" -eq 1 ]; then
    # Si se proporciona el número de hosts, lo almacenamos en la variable num_hosts
    num_hosts=$1

    # Ejecutamos Mininet con una topología personalizada y el número específico de hosts
    echo "Ejecutando Mininet con topología personalizada y $num_hosts hosts."
    # Utilizamos el contenido de sucess_1.txt como entrada para Mininet
    cat ./scripts/success_1.txt | sudo mn --custom topology.py --topo myTopo,$num_hosts --arp --mac --switch ovsk --controller remote
else
    # Si no se proporciona el número de hosts, ejecutamos Mininet con la topología predeterminada
    echo "Ejecutando Mininet con topología predeterminada."
    # Utilizamos el contenido de sucess_1.txt como entrada para Mininet
    cat ./scripts/success_1.txt | sudo mn --custom topology.py --topo myTopo --arp --mac --switch ovsk --controller remote
fi
