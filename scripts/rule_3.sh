#!/bin/bash


# En otra terminal ejecutar: pox/pox.py forwarding.l2_learning firewall --rule=rules.json
# Run: chmod +x rule_3.sh
# Run: ./rule_3.sh <num switch>

# Este script ejecuta una simulación de red Mininet con una topología personalizada
# para verificar la Regla 3: Dos hosts específicos no deben poder comunicarse.

# Estoy en scripts
cd ..

# Comprobamos si se proporciona el número de hosts como argumento
if [ "$#" -eq 1 ]; then
    # Si se proporciona el número de hosts, lo almacenamos en la variable num_hosts
    num_hosts=$1

    # Ejecutamos Mininet con una topología personalizada y el número específico de hosts
    echo "Ejecutando Mininet con topología personalizada y $num_hosts hosts."
    echo "pingall" | sudo mn --custom topology.py --topo myTopo,$num_hosts --arp --mac --switch ovsk --controller remote
else
    # Si no se proporciona el número de hosts, ejecutamos Mininet con la topología predeterminada
    echo "Ejecutando Mininet con topología predeterminada."
    echo "pingall" | sudo mn --custom topology.py --topo myTopo --arp --mac --switch ovsk --controller remote
fi

# Nota: El comando "pingall" se utiliza para intentar realizar ping entre todos los hosts.
# El comportamiento esperado es que h1 y h2 no deberían poder comunicarse según la Regla 3.
# Antes de ejecutar este script en otra terminal, se recomienda ejecutar el controlador POX con el módulo de firewall y una regla definida en rules.json.
