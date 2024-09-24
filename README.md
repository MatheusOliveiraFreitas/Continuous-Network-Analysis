# Continuous-Network-Analysis
Processing plugin that adds several scripts to assist in decision making and validation of line-type vector networks by generating inconsistencies, further expanding the “Network Analysis” tool.

Português:

email para contato: matheus18.1@yahoo.com

O Vector Network Analysis é um complemento processing para o Qgis que traz varias ferramentas que expande a Análise de rede do Qgis Básico, trazendo ferramentas inovadoras para a facilitação de Analise de Rede, que no total são 5 funções.

Recursos Principais são:

# "Attribute discontinuity in a network": Vai identificar por meio de pontos onde na Rede onde o atributo selecionado foi parado, ideal para analise de redes rodoviárias onde uma rodovia com Sigla conecta com outra rodovia com Sigla ou rede de drenagem onde o nome deve conectar com outro trecho com nome.

# "Dangle Analysis": Uma ferramenta onde o usuário ira escolher uma rede, ira identificar as pontas soltas(Dangles) na rede, com isso o usuário poderá selecionar varias camadas do projeto, para identificar se os Dangles tem sobreposição e/ou interseção com essas camadas selecionadas.
Assim podendo gerar dois arquivos;
	*DANGLES_Non_Overlap que são as pontas soltas que não tem sobreposição e/ou interseção com as camadas selecionadas.
	*DANGLES_Overlapping que são as pontas soltas(Dangles) que tem sobreposição e/ou interseção.

# -"Extract Springs": O programa realiza uma série de processos para identificar e extrair nascentes de uma rede vetorial. As opções de extração incluem:ALL, Minimum Value e Maximum Value, A extração pode gerar resultados do tipo Linha e/ou Ponto;
	*Linha será apenas o comprimento em relação ao $leng na tabela de atributos
	*Ponto além de ter o comprimento terá os atributos da camada original na nascente.

# -"Identify Dangles": Uma ferramenta onde o usuário ira escolher uma rede, ira identificar as pontas soltas(Dangles) na rede.

# -"Network Connectivity From a Point":Realiza uma série de procedimentos para verificar a conectividade topológica de uma camada de linhas a partir de uma camada inicial (que deve obrigatoriamente ter interseção e/ou sobreposição com pelo menos um trecho da rede). Ao final do processo, o plugin poderar gerar dois arquivos:
	*Os trechos da rede que não estão conectados topologicamente com a camada inicial, ou seja, os trechos desconectados.
	*Os trechos da rede que estão conectados topologicamente com a camada inicial.
