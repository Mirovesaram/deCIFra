import numpy as np
from findpeaks import findpeaks
import matplotlib.pyplot as plt
import os
import glob
import pandas as pd
import peakdetect

def testar3():
    caminho=r"C:\Users\aojor\Downloads\CodigosPython\vsCode\projetos\pacoteComparadorPicos\comparadorPicos"
    buscaXyPadrao=os.path.join(caminho,'*.xy')
    ArrayCaminhoXy=glob.glob(buscaXyPadrao)
    dataFramePadrao =pd.read_csv(ArrayCaminhoXy[0], delim_whitespace=True, header=None, names=['x','y'])
    angulos=dataFramePadrao.x.values
    print(angulos)
    intensidades=dataFramePadrao.y.values
    print(intensidades)
    picos = peakdetect.peakdetect(intensidades,angulos,14,100)
    print(picos)
def testar2():
    X = [9,60,377,985,1153,672,501,1068,1110,574,135,23,3,47,252,812,1182,741,263,33]
    fp = findpeaks(method='peakdetect',lookahead=1,interpolate=10)
    results = fp.fit(X)
    fp.plot()
"""
# 2D array example
from findpeaks import findpeaks
X = fp.import_example('2dpeaks')
results = fp.fit(X)
fp.plot()

# Image example
from findpeaks import findpeaks
fp = findpeaks(method='topology',imsize=(300,300),denoise='fastnl',params={'window': 30})
X = fp.import_example('2dpeaks_image')
results = fp.fit(X)
fp.plot()

# Plot each seperately
fp.plot_preprocessing()
fp.plot_persistence()
fp.plot_mesh()
"""
def testar1():
    caminho=r"C:\Users\aojor\Downloads\repositorioCienciasExatasTerra\PIBIC\praticaFPRM\DadosZnO"
    #caminho=r"C:\Users\aojor\Downloads\CodigosPython\vsCode\projetos\pacoteComparadorPicos\comparadorPicos"
    buscaXyPadrao=os.path.join(caminho,'*.xy')
    ArrayCaminhoXy=glob.glob(buscaXyPadrao)
    dataFramePadrao =pd.read_csv(ArrayCaminhoXy[0], delim_whitespace=True, header=None, names=['x','y'])
    angulos=dataFramePadrao.x.values
    intensidades=dataFramePadrao.y.values
    X = intensidades
    #fp=findpeaks.stats.topology()
    fp = findpeaks(method='topology',limit=None)
    print(np.min(np.min(X))-1)
    results = fp.fit(X)
    fp.plot()

    # Extract peak positions
    peak_positions = results['df'].index[results['df']['peak'] == True].tolist()

    # Plotting the results
    plt.plot(angulos, intensidades, label='Data')
    plt.scatter(angulos[peak_positions], intensidades[peak_positions], color='red', label='Peaks')
    plt.legend()
    plt.show()

    # Print peak positions
    print("Peak positions:", angulos[peak_positions])
    print(len(angulos[peak_positions]))
    
    df=pd.DataFrame(results['df'])
    caminho=r'C:\Users\aojor\Downloads\CodigosPython\vsCode\projetos\pacoteComparadorPicos\comparadorPicos\df.xlsx'
    df.to_excel(caminho)
    
if __name__ == "__main__":
    testar1()