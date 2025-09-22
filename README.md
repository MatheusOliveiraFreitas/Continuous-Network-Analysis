**contact email**: matheus18.1@yahoo.com

Vector Network Analysis is a processing plugin for Qgis that provides several tools that expand the Basic Qgis Network Analysis, providing innovative tools to facilitate Network Analysis, which in total are 5 functions.

**Main features are**:

***"Attribute Discontinuity Detector"***: It will identify through points where in the Network the selected attribute was stopped, ideal for analyzing road networks where a highway with acronym connects to another highway with acronym or drainage network where the name should connect to another named section.

***"Dangle Analysis"***: A tool where the user will choose a network, it will identify the loose ends (Dangles) in the network, with this the user will be able to select several layers of the project, to identify if the Dangles have overlap and/or intersection with these selected layers. Thus, it can generate two files:

- DANGLES_Non_Overlap which are the loose ends that do not overlap and/or intersection with the selected layers.
- DANGLES_Overlapping are the loose ends (Dangles) that have overlap and/or intersection.

***"Extract Springs"***: The program performs a series of processes to identify and extract springs from a vector network. The extraction options include: ALL, Minimum Value and Maximum Value. The extraction can generate results of the Line and/or Point type;

- Headwater_Lines: Line will only be the length in relation to the $leng in the attribute table
- Headwater_Points: Point will have the attributes of the original layer in the source in addition to the length.

***"Identify Dangles"***: A tool where the user will choose a network, it will identify the loose ends (Dangles) in the network.

***"Disconnected Network Segments"***: Performs a series of procedures to verify the topological connectivity of a line layer from an initial layer (which must have intersection and/or overlap with at least one section of the network). At the end of the process, the plugin can generate two files:

-  Excerpt Disconnected: The network sections that are not topologically connected to the initial layer, that is, the disconnected sections.
-  Connected Section: The network sections that are topologically connected to the initial layer.

***"Pseudo-node"***: Identifies pseudo-nodes in a line layer and returns points with the attributes of the two segments connected at that node. For each detected pseudo-node, a point is created with the combined attributes of the two connected line features.
   
-  Attribute fields from the second feature are suffixed with _2 to avoid duplication.

***"Pseudo-node Analysis"***: It analyzes whether the breaks (Pseudo-node) are topologically connected to the vertices of the layers that the user selected.

-  Returns Non_Overlap Pseudo-node, Pseudo-node that is not topologically connected to any vertex of the selected layers.
-  Returns Overlapping Pseudo-node, Pseudo-node that is topologically connected to any vertex of the selected layers, in addition to having a column that identifies which layer each vertex is topologically connected to.

***"Pseudo-node Analysis"***: Connection Counter Per Vertex Calculates which vertices in a line network are connected to other vertices, and how many connections each has. Algorithm topologically calculates vertices with more than one connection (degree > 1).

-  Creates points only at vertices with more than one connection (degree > 1), with a 'Vertex' field indicating the number of connections at each point.
  
Português:

**email para contato**: matheus18.1@yahoo.com


O Vector Network Analysis é um complemento processing para o Qgis que traz varias ferramentas que expande a Análise de rede do Qgis Básico, trazendo ferramentas inovadoras para a facilitação de Analise de Rede, que no total são 5 funções.

**Recursos Principais são**:

***"Attribute Discontinuity Detector"***: Vai identificar por meio de pontos onde na Rede onde o atributo selecionado foi parado, ideal para analise de redes rodoviárias onde uma rodovia com Sigla conecta com outra rodovia com Sigla ou rede de drenagem onde o nome deve conectar com outro trecho com nome.

***"Dangle Analysis"***: Uma ferramenta onde o usuário ira escolher uma rede, ira identificar as pontas soltas(Dangles) na rede, com isso o usuário poderá selecionar varias camadas do projeto, para identificar se os Dangles tem sobreposição e/ou interseção com essas camadas selecionadas.
Assim podendo gerar dois arquivos:
-	DANGLES_Non_Overlap que são as pontas soltas que não tem sobreposição e/ou interseção com as camadas selecionadas.
-	DANGLES_Overlapping que são as pontas soltas(Dangles) que tem sobreposição e/ou interseção.

***"Extract Springs"***: O programa realiza uma série de processos para identificar e extrair nascentes de uma rede vetorial. As opções de extração incluem:ALL, Minimum Value e Maximum Value, A extração pode gerar resultados do tipo Linha e/ou Ponto;
-	Headwater_Lines: Linha será apenas o comprimento em relação ao $leng na tabela de atributos
-	Headwater_Points: Ponto além de ter o comprimento terá os atributos da camada original na nascente.

***"Identify Dangles"***: Uma ferramenta onde o usuário ira escolher uma rede, ira identificar as pontas soltas(Dangles) na rede.

***"Disconnected Network Segments"***:Realiza uma série de procedimentos para verificar a conectividade topológica de uma camada de linhas a partir de uma camada inicial (que deve obrigatoriamente ter interseção e/ou sobreposição com pelo menos um trecho da rede). Ao final do processo, o plugin poderar gerar dois arquivos:
-	Excerpt Disconnected: Os trechos da rede que não estão conectados topologicamente com a camada inicial, ou seja, os trechos desconectados.
-	Connected Section: Os trechos da rede que estão conectados topologicamente com a camada inicial.

***"Pseudo-node"***: Identifica Pseudo-nodes em uma camada de linhas e retorna pontos com atributos dos dois segmentos conectados nesse nó. Para cada pseudo-nó detectado, um ponto é criado com a junção dos atributos das duas feições conectadas.
-  Os campos de atributos da segunda feição recebem o sufixo _2 para evitar duplicação de nomes.

***"Pseudo-node Analysis"***: Ele analisa se as quebras (Pseudo-node) estão topologicamente conectadas nos vértices das camadas que usuário selecionou.
-  Retorna Pseudo-node sem conexão, Pseudo-node que não estão conectados topologicamente em nenhum vértice das camadas selecionadas.
-  Retorna Pseudo-node com conexão, Pseudo-node que estão conectados topologicamente com algum vértice das camadas selecionadas, além disso tem uma coluna que identifica qual camada cada vértice está topologicamente conectado.

***"Vertex Connection Counter"***: Calcula quais vértices em uma rede de linhas estão conectados a outros vértices, e quantas conexões cada um possui. Algoritmo calcula topologicamente os vértices com mais de uma conexão (grau > 1).
-  Cria pontos apenas nos vértices com mais de uma conexão (grau > 1), com um campo 'Vertice' indicando o número de conexões em cada ponto.
