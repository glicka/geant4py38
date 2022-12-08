import numpy as np
import matplotlib.pyplot as plt
import Geant4 as g4

energy = 9
enfwhm = 0.05
gaussEnrg = np.random.normal(loc=energy, scale=(enfwhm*energy)/2.355,size=1000)
cdfGauss = np.cumsum(gaussEnrg)
cdfGauss /= max(cdfGauss)
x = np.linspace(7,11,1000)
d = np.zeros(20000)
for i in range(len(d)):
    rndm = g4.G4UniformRand()
    d[i] = np.interp(rndm,cdfGauss,gaussEnrg)

frq,edges = np.histogram(d,bins=500)

plt.figure()
plt.step(edges[:-1],frq)
plt.show()
