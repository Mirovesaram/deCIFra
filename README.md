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

Pois bem, a primeira parte é escolher uma pasta para os CIFs
