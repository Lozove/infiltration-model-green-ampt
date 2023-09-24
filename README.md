# Modelo Conceitual Hidrológico

Este repositório contém a implementação de um modelo conceitual hidrológico que utiliza funções empíricas para explicar subprocessos do ciclo hidrológico. O modelo busca representar de maneira simplificada os processos físicos do ciclo hidrológico em uma escala de tempo semi-horária.

## Disciplina Hidrologia Física PEC/COPPE/UFRJ
- Professor Doutor Daniel Andres Rodriguez

## Desenvolvedores

- Aline Ferreira de Andrade
- Luiz Fernando Lozove
- Tatiana Finageiv Neder

## Visão Geral do Modelo

Baseado na compreensão teórica do ciclo hidrológico, o modelo conceitual emprega funções empíricas para explicar alguns dos subprocessos envolvidos, procurando representar, de maneira simplificada, todos os processos físicos conhecidos do ciclo hidrológico. (KAISER, 2006)
Dessa forma, a modelagem conceitual a ser apresentada neste relatório foi elaborada seguindo o ponto de vista dos processos físicos do ciclo hidrológico. A escala de tempo selecionada para a modelagem foi a semi-horária. Nessa abordagem o dossel, solo e lençol freático foram considerados como reservatórios e denominados Rdossel, Rsolo e Rsubterrâneo respectivamente, cujo volume de água armazenado pode ser bastante variável no tempo, dependendo de muitos fatores.
A principal entrada de água no sistema é a precipitação. Considerando a cobertura vegetal existente na área de estudo sobre o solo, parte da água da chuva é interceptada pelo dossel e parte atinge diretamente o solo, denominada de precipitação livre (Plivre). A interceptação,  volume de água armazenado no reservatório do dossel, foi calculado pelo modelo de Rutter Adaptado. Ao atingir a capacidade máxima de armazenamento do dossel, o excesso do volume de água armazenada é transferido pro solo. Denomina-se precipitação efetiva (Pefetiva) a parcela de precipitação que atinge o solo. Quando a precipitação cessa, o volume de água interceptado evapora, cuja taxa de evaporação foi calculada com base no modelo de Penman-Monteith.
Em relação à água que atinge a superfície do solo, parte é infiltrada e parte pode escoar superficialmente (Qsup). A água infiltrada irá se distribuir ao longo do perfil de solo, cuja taxa de infiltração e geração de escoamento superficial foram calculadas utilizando o modelo Green-Ampt. A água que atinge o reservatório do solo pode percolar atingindo o lençol freático, bem como pode haver um fluxo de água no solo, gerando o escoamento sub-superficial (Qsub). Quando a chuva cessa, parte da água retida no reservatório do solo é perdida por transpiração. 




