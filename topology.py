from mininet.topo import Topo



class CustomTopology(Topo):
    def __init__(self, num_switches=4):
        """
        Constructor de la topología personalizada.

        Parameters:
        - num_switches: Número de switches en la parte dinámica (por defecto, 4).
        """
        # Llamada al constructor de la clase base (Topo)
        if num_switches <= 0:
            raise ValueError("The number of switches must be a non-negative value.")
    
        super(CustomTopology, self).__init__()
        
        # Parte estática - Izquierda
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        

        # Parte estática - Derecha
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
        
        # Parte dinámica
        switches = [self.addSwitch(f's{i}') for i in range(1, num_switches + 1)]
        
        # Conexiones entre switches en la parte dinámica
        for i in range(num_switches - 1):
            self.addLink(switches[i], switches[i + 1])
        
        # Conexiones entre hosts estáticos e inicio/fin de la cadena dinámica
        self.addLink(h1, switches[0])
        self.addLink(h2, switches[0])

        self.addLink(switches[-1], h3)
        self.addLink(switches[-1], h4)
        

        
topos = { 'myTopo': CustomTopology }
