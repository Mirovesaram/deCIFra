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
(* Mais para frente (Na sub-seção "Comparar" dessa seção, a explicação desta distinção vai evidenciar que a maneira aqui usada para explicar a avaliação de cada pico é um tanto errada e esconde um aspecto fundamental dessa função))
### Selecione a pasta com os arquivos .cif
Pois bem, a primeira parte é escolher uma pasta para os CIFs. Tenha em mente que a janela que vai abrir só vai demonstrar as pastas do seu computador. 

> [!TIP]
> É recomendável que você utilize uma pasta que somente tenha os CIFs que você quer analisar com seu padrão.

> [!WARNING]
> Você pode renomear os arquivos como desejar, contudo evite colocar "." no nome, isso pode causar problema para a biblioteca de leitura de arquivos que vasculha a pasta escolhida por arquivos que terminam com ".cif"

Após a escolha, o caminho será exposto como uma nota de que o diretório foi de fato escolhido.
### Selecione a pasta com seu padrão de difração (.txt e .xy)
Essa pasta tem que ter **somente dois** arquivos:

> Um *arquivo .txt* que tem os ângulos dos picos do seu padrão de difração, coloque somente eles sem qualquer "label" de coluna no começo tampouco espaços vazios no fim

> Um *arquivo .xy* com os ângulos e intensidades do seu padrão de difração no todo. Esse tipo de arquivo é comum carregar os dados de um padrão de difração, por isso a escolha de um arquivo .xy

Exemplos:

[Exemplo de arquivo .xy](./exemplo.xy)

[Exemplo de arquivo .txt](./exemplo.txt)

Também como no caso anterior, o caminho da pasta aparecerá como nota de que o diretório de fato foi escolhido.
### Selecione a radiação característica (Angstrons)
Nesse "comboBox" você escolhe a radiação característica que será utilizada para detectar os picos de reflexão dos CIFs, note que as 3 primeiras opções se tratam dos valores de radiação característica K-alfa (Primária, se não me engano) de Cobre (Cu), radiação característica K-beta (Muito provavelmente primária) de Cu (Esses dois primeiros foram retirados do software Diamond (https://www.crystalimpact.com/diamond/)) e a média aritmética das duas anteriores, respectivamente. Após ela, tem opções em texto que são disponibilizados pela biblioteca pymatgen (https://github.com/materialsproject/pymatgen) (https://pymatgen.org/pymatgen.analysis.diffraction.html#pymatgen.analysis.diffraction.xrd.XRDCalculator.AVAILABLE_RADIATION), basicamente as opções são para diversos elementos e as radiações características tem as seguintes siglas:

> Ka1 - radiação característica K-alfa primária

> Ka2 - radiação característica K-alfa secundária

> Kb1 - radiação característica K-beta primária

> Ka - radiação característica K-alfa média aritmética entre a primária e a secundária (Provavelmente)

### Comparar
Caso esteja tudo correto com os diretórios que você escolheu, aparecerá uma janela de informação e então quando a comparação for terminada aparecerá uma janela com três opções:

> [!Important]
> Pode ser que depois desse aviso que basicamente confirma que a primeira verificação permitiu a continuação do programa, ainda pode haver um erro caso escolha uma pasta que não tenha os arquivos necessários ou que tenha os arquivos de tipo correto mas com informações erradas (Que não permitam a continuação do código, quero dizer). A existência dessa janela inicial que segura o início da comparação (Enquanto você não teclar "Ok") é mais pelo fato de eu não ter criado uma forma mais robusta de demonstração para o usuário que a comparação está ocorrendo (Como uma barra de progresso). Então não acredite que já está tudo certo com as pastas e consequentemente com os arquivos que você escolheu. Isso também reflete a construção do código que só permite a aparição desses problemas somente em meio à comparação, bom, eu poderia corrigir isso e atribuir isso à verificação de diretórios antes da comparação, mas paciência, pode ser que eu nunca faça essa mudança.

> Mostrar gráfico

> Salvar planilha de comparações

> Salvar planilha de CIFs

A primeira opção mostra o gráfico dentando as posições e intensidades dos picos dos 3 melhores CIFs demonstrando também quais são suas colocações no ranking (Explicarei melhor a mecânica do ranking no tópico seguinte), a partir dessa janela de observação você pode salvar esse gráfico para posteridade.
A segunda opção salva a planilha com os resultados das comparações. É basicamente grandes tabelas (Cada tabela corresponde a um CIF e cada tabela está em uma aba da planilha que tem como título o nome do arquivo do CIF) que têm diversas colunas. Aqui vale ressaltar e explicar a distinção que garante se um pico em análise que tem distância maior que 0,5° de qualquer outro pico do seu padrão é excedente ou faltante.
> [!Note]
> Basicamente, é importante saber que tanto os picos do seu padrão são usados como referência para análise quanto os picos dos CIFs. O que eu quero dizer com isso é: Não só os picos dos CIFs são usados para comparar com os picos do seu padrão, os picos do seu padrão são usados para comparar com os picos dos CIFs também. Se ainda ficou estranho, deixe-me esclarecer com uma explicação de como a comparação é feita: Na fase 0, escolhe-se um CIF. Já na primeira fase, escolhe-se um pico desse CIF e então compara-se as distâncias desse pico para todos os picos do seu padrão, isso é feito com o primeiro pico do CIF então com o segundo e por aí vai até o último pico desse CIF. Caso o pico em questão que foi selecionado para ser comparado com todos os picos do seu padrão não tenha uma distância (d) menor que 0,5° com nenhum pico dele, quer dizer que esse CIF tem um *pico excedente* - Um pico que o CIF tem e que excede o número de picos que existem em seu padrão. Um pico que fica sobrando nesse seu padrão. Na segunda fase é feito o contrário, primeiro se escolhe um pico do seu padrão e então compara-se com todos os picos do CIF em questão. Caso o pico do seu padrão não corresponda a nenhum pico do CIF, temos um *pico faltante* - Quer dizer que para aquele CIF, caso você utilize ele no seu padrão vai ficar faltando um pico, então podemos erroneamente dizer que o pico faltante pertence ao CIF (Errôneo em modo de falar, digo. Por isso que eu afirmei anteriormente que a explicação que eu dei mais acima é meio errada, pois dá a entender que o ponto de referência de comparação para *pico faltante* e *pico excedente* pertence somente ao CIF). Em resumo, a comparação primeiro escolhe o CIF então escolhe um pico desse CIF e compara com todos os picos do seu padrão e quanto todos os picos do CIF passarem por essa comparação, é escolhido um pico do seu padrão e compara-se o mesmo com todos os picos do CIF, quando todos os picos do seu padrão passarem por essa comparação, passa-se para o próximo CIF.

Agora, vamos à explicação de cada coluna:

> 2theta-Padrão: Um ângulo do pico do seu padrão que corresponde (ou não) a algum ângulo do pico do CIF dessa linha

> [!Note]
> Caso não apareça nenhum ângulo em uma dada linha, é porque não houve nenhum ângulo do seu padrão que correspondeu com a comparação com o respectivo ângulo desse CIF nessa linha, logo esse pico do CIF é excedente.

> 2theta: Um ângulo do pico do CIF que corresponde (Ou não) a algum ângulo do pico do seu padrão dessa linha

> [!Note]
> Caso não apareça nenhum ângulo em uma dada linha, é porque não houve nenhum ângulo do CIF que correspondeu com a comparação com o respectivo ângulo do seu padrão nessa linha, logo esse pico para esse CIF falta no padrão, um pico faltante



