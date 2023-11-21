#!/bin/bash
export PYTHONPATH=.:$PYTHONPATH
cd ..
#gnome-terminal -- bash -c "sh scripts/levantar_controlador.sh; exec bash"

# Nos fijamos si se pasan host por parametro
if [ "$#" -eq 2 ]; then
    scr="./scripts/$1"
    n=$2
    echo "$scr"

    cat $scr | sudo mn --custom topology.py --topo myTopo,$n --arp --mac --switch ovsk --controller remote
fi
if [ "$#" -eq 1 ]; then
    scr="./scripts/$1"
    echo "$scr"

    echo "Ejecutando Mininet con topología predeterminada."

    cat $scr  | sudo mn --custom topology.py --topo myTopo --arp --mac --switch ovsk --controller remote
fi