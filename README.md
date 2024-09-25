**contact email**: matheus18.1@yahoo.com

Vector Network Analysis is a processing plugin for Qgis that provides several tools that expand the Basic Qgis Network Analysis, providing innovative tools to facilitate Network Analysis, which in total are 5 functions.

**Main features are**:

***"Attribute discontinuity in a network"***: It will identify through points where in the Network the selected attribute was stopped, ideal for analyzing road networks where a highway with acronym connects to another highway with acronym or drainage network where the name should connect to another named section.

***"Dangle Analysis"***: A tool where the user will choose a network, it will identify the loose ends (Dangles) in the network, with this the user will be able to select several layers of the project, to identify if the Dangles have overlap and/or intersection with these selected layers. Thus, it can generate two files:

- DANGLES_Non_Overlap which are the loose ends that do not overlap and/or intersection with the selected layers.
- DANGLES_Overlapping are the loose ends (Dangles) that have overlap and/or intersection.

***"Extract Springs"***: The program performs a series of processes to identify and extract springs from a vector network. The extraction options include: ALL, Minimum Value and Maximum Value. The extraction can generate results of the Line and/or Point type;

- Headwater_Lines: Line will only be the length in relation to the $leng in the attribute table
- Headwater_Points: Point will have the attributes of the original layer in the source in addition to the length.

***"Identify Dangles"***: A tool where the user will choose a network, it will identify the loose ends (Dangles) in the network.

***"Network Connectivity From a Point"***: Performs a series of procedures to verify the topological connectivity of a line layer from an initial layer (which must have intersection and/or overlap with at least one section of the network). At the end of the process, the plugin can generate two files:

-  Excerpt Disconnected: The network sections that are not topologically connected to the initial layer, that is, the disconnected sections.
-  Connected Section: The network sections that are topologically connected to the initial layer.

Português:

**email para contato**: matheus18.1@yahoo.com


O Vector Network Analysis é um complemento processing para o Qgis que traz varias ferramentas que expande a Análise de rede do Qgis Básico, trazendo ferramentas inovadoras para a facilitação de Analise de Rede, que no total são 5 funções.

**Recursos Principais são**:

***"Attribute discontinuity in a network"***: Vai identificar por meio de pontos onde na Rede onde o atributo selecionado foi parado, ideal para analise de redes rodoviárias onde uma rodovia com Sigla conecta com outra rodovia com Sigla ou rede de drenagem onde o nome deve conectar com outro trecho com nome.

***"Dangle Analysis"***: Uma ferramenta onde o usuário ira escolher uma rede, ira identificar as pontas soltas(Dangles) na rede, com isso o usuário poderá selecionar varias camadas do projeto, para identificar se os Dangles tem sobreposição e/ou interseção com essas camadas selecionadas.
Assim podendo gerar dois arquivos:
-	DANGLES_Non_Overlap que são as pontas soltas que não tem sobreposição e/ou interseção com as camadas selecionadas.
-	DANGLES_Overlapping que são as pontas soltas(Dangles) que tem sobreposição e/ou interseção.

***"Extract Springs"***: O programa realiza uma série de processos para identificar e extrair nascentes de uma rede vetorial. As opções de extração incluem:ALL, Minimum Value e Maximum Value, A extração pode gerar resultados do tipo Linha e/ou Ponto;
-	Headwater_Lines: Linha será apenas o comprimento em relação ao $leng na tabela de atributos
-	Headwater_Points: Ponto além de ter o comprimento terá os atributos da camada original na nascente.

***"Identify Dangles"***: Uma ferramenta onde o usuário ira escolher uma rede, ira identificar as pontas soltas(Dangles) na rede.

***"Network Connectivity From a Point"***:Realiza uma série de procedimentos para verificar a conectividade topológica de uma camada de linhas a partir de uma camada inicial (que deve obrigatoriamente ter interseção e/ou sobreposição com pelo menos um trecho da rede). Ao final do processo, o plugin poderar gerar dois arquivos:
-	Excerpt Disconnected: Os trechos da rede que não estão conectados topologicamente com a camada inicial, ou seja, os trechos desconectados.
-	Connected Section: Os trechos da rede que estão conectados topologicamente com a camada inicial.
