# comparadorPicos
Um algortimo simples para auxílio na análise de Rietveld (**FPRM** - Full Profile Refinement Method - Método de refinamento de perfil "completo").
Esse foi o começo, hoje em dia o programa abriga mais 2 funções, detecção de picos e filtragem de picos para comparação do padrão de difração com demais CIFs utilizando entre 1 a 5 picos. Aqui terá uma seção abordando cada aba e função do programa com instruções e orientações sobre como utilizar corretamente cada função para evitar erros por mau uso.
## Aba Comparar picos
Essa aba abriga a função primária do programa que é *comparar picos*. Sendo mais específico, a ideia é ter uma série de CIFs em que você deseja comparar cada pico desse CIF com cada pico do seu padrão de difração e, assim, a função abrigada nessa aba é facilitar esse trabalho de analisar e descobrir qual CIF melhor se aproxima às posições de cada pico do seu padrão. Portanto o método de avaliação de cada CIF é ver a qual distância cada ângulo de pico de um CIF está de um ângulo de pico do seu padrão. As distâncias (d) variam de 0° < d <= 0,5°, sendo a classificação para cada pico do CIF como:

> Muito bom - 0,4° < d <= 0,5°

> Bom - 0,3° < d <= 0,4°

> Médio - 0,2° < d <= 0,3°

> Pouco bom - 0,1° < d <= 0,2°

> Pico excedente ou faltante - d > 0,5° *

(* A última classificação tem certa distinção no código para saber se é um ou outro, já que a condição de distância é a mesma.)
### Selecione a pasta com os arquivos .cif
Pois bem, a primeira parte é escolher uma pasta para os CIFs. Tenha em mente que a janela que vai abrir só vai demonstrar as pastas do seu computador. 

> [!TIP]
> É recomendável que você utilize uma pasta que somente tenha os CIFs que você quer analisar com seu padrão.

> [!WARNING]
> Você pode renomear os arquivos como desejar, contudo evite colocar "." no nome, isso pode causar problema para a biblioteca de leitura de arquivos que vasculha a pasta escolhida por arquivos que terminam com ".cif"

Após a escolha, o caminho será exposto como uma nota de que o diretório foi de fato escolhido.
### Selecione a pasta com seu padrão de difração (.txt e .xy)
Essa pasta tem que ter **somente dois** arquivos:

> Um **arquivo .txt** que tem os ângulos dos picos do seu padrão de difração, coloque somente eles sem qualquer "label" de coluna no começo tampouco espaços vazios no fim

> Um **arquivo .xy** com os ângulos e intensidades do seu padrão de difração no todo. Esse tipo de arquivo é comum carregar os dados de um padrão de difração, por isso a escolha de um arquivo .xy

Exemplo:



