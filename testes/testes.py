from scipy.signal import find_peaks as fp
import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import pdb

diretorioScript=os.path.dirname(os.path.abspath(__file__))
os.chdir(diretorioScript)
pastaAtual=os.getcwd()
#pdb.set_trace()
buscaXyPadrao=os.path.join(pastaAtual,'*.xy')
ArrayCaminhoXy=glob.glob(buscaXyPadrao)
dataFramePadrao =pd.read_csv(ArrayCaminhoXy[0], delim_whitespace=True, header=None, names=['x','y'])
angulos=dataFramePadrao.x.values
intensidades=dataFramePadrao.y.values
indicePicos, _ =fp(intensidades, height=None, threshold=None, distance=None, prominence=None, width=intensidades, wlen=None, rel_height=0.5, plateau_size=intensidades)
anguloPicos=angulos[indicePicos]
intensidadePicos=intensidades[indicePicos]
plt.figure(figsize=(10,6))
plt.plot(dataFramePadrao['x'], dataFramePadrao['y'])
plt.plot(anguloPicos,intensidadePicos,color='r')
#plt.vlines(anguloPicos,ymin=0,ymax=max(intensidadePicos), linestyles='dashed',color='red')
plt.title('Teste')
plt.xlabel('Ângulo 2theta')
plt.ylabel('Intensidade')
plt.show()
#Para saber se isso de fato aloca os dados de uma certa coluna
#teste=dataFramePadrao.x.values
#pdb.set_trace()


