from mininet.topo import Topo



class CustomTopology(Topo):
    def __init__(self, num_switches=4):
        """
        Constructor de la topología personalizada.

        Parameters:
        - num_switches: Número de switches en la parte dinámica (por defecto, 4).
        """
        # Llamada al constructor de la clase base (Topo)
        if num_switches < 0:
            raise ValueError("The number of switches must be a non-negative value.")
    
        super(CustomTopology, self).__init__()
        
        # Parte estática - Izquierda
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        s1 = self.addSwitch('s1')
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        

        # Parte estática - Derecha
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
        s2 = self.addSwitch('s2')
        self.addLink(s2, h3)
        self.addLink(s2, h4)

        if num_switches == 0:
            self.addLink(s1, s2)
            return
        
        # Parte dinámica
        switches = [self.addSwitch(f's{i +2}') for i in range(1, num_switches + 1)]
        
        # Conexiones entre switches en la parte dinámica
        for i in range(num_switches - 1):
            self.addLink(switches[i], switches[i + 1])
        
        # Conexiones entre switches estáticos e inicio/fin de la cadena dinámica
        self.addLink(s1, switches[0])
        self.addLink(switches[-1], s2)
        

        
topos = { 'myTopo': CustomTopology }
