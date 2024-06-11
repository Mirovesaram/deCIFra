import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, peak_widths
from scipy.ndimage import gaussian_filter1d

def ler_dados_arquivo(nome_arquivo):
    # Lê os dados do arquivo .txt
    dados = np.loadtxt(nome_arquivo)
    angulos = dados[:, 0]
    intensidades = dados[:, 1]
    return angulos, intensidades

def identificar_picos(angulos, intensidades):
    # Suaviza os dados para remover ruídos
    intensidades_suavizadas = gaussian_filter1d(intensidades, sigma=3)
    
    # Identifica os picos nas intensidades usando a função find_peaks do scipy
    indices_picos, _ = find_peaks(intensidades_suavizadas, height=500, distance=20)
    angulos_picos = angulos[indices_picos]
    intensidades_picos = intensidades[indices_picos]
    
    return angulos_picos, intensidades_picos

def salvar_picos_em_arquivo(nome_arquivo, angulos_picos, intensidades_picos):
    # Salva os picos identificados em um arquivo .txt
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write('Ângulo (2θ)\tIntensidade\n')
        for angulo, intensidade in zip(angulos_picos, intensidades_picos):
            f.write(f'{angulo}\t{intensidade}\n')

def plotar_grafico_com_picos(angulos, intensidades, angulos_picos, intensidades_picos):
    # Plotar o gráfico dos dados
    plt.figure(figsize=(10, 6))
    plt.plot(angulos, intensidades, label='Difração de Raios-X')
    
    # Adicionar barras verticais para os picos identificados
    plt.vlines(angulos_picos, ymin=0, ymax=max(intensidades), color='red', linestyles='dashed', label='Picos identificados')
    
    # Adicionar o ângulo do pico no gráfico
    for angulo_pico, intensidade_pico in zip(angulos_picos, intensidades_picos):
        plt.text(angulo_pico, intensidade_pico, f'{angulo_pico:.2f}', horizontalalignment='center', verticalalignment='bottom')
    
    # Configurações do gráfico
    plt.title('Difração de Raios-X')
    plt.xlabel('Ângulo (2θ)')
    plt.ylabel('Intensidade')
    plt.legend()
    plt.grid(True)
    
    # Salvar o gráfico como imagem
    nome_arquivo_grafico = 'difracao_raios_x_com_picos.png'
    plt.savefig(nome_arquivo_grafico)
    
    # Mostrar o gráfico
    plt.show()

def processar_arquivos_na_pasta(pasta):
    # Encontra todos os arquivos .xy na pasta especificada
    arquivos_entrada = glob.glob(os.path.join(pasta, '*.xy'))
    
    for arquivo_entrada in arquivos_entrada:
        # Nome do arquivo de saída baseado no nome do arquivo de entrada
        nome_arquivo_saida = os.path.splitext(arquivo_entrada)[0] + '_picos.txt'
        
        # Ler os dados do arquivo
        angulos, intensidades = ler_dados_arquivo(arquivo_entrada)

        # Identificar os picos
        angulos_picos, intensidades_picos = identificar_picos(angulos, intensidades)

        # Salvar os picos em um arquivo
        salvar_picos_em_arquivo(nome_arquivo_saida, angulos_picos, intensidades_picos)

        print(f'Picos identificados e salvos em {nome_arquivo_saida}')
        
        # Plotar o gráfico com os picos identificados
        plotar_grafico_com_picos(angulos, intensidades, angulos_picos, intensidades_picos)

def main():
    # Obtém o diretório atual onde o script está sendo executado
    diretorioScript=os.path.dirname(os.path.abspath(__file__))
    os.chdir(diretorioScript)
    pasta_atual = os.getcwd()

    # Processa todos os arquivos na pasta atual
    processar_arquivos_na_pasta(pasta_atual)

if __name__ == '__main__':
    main()
