# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterVectorDestination,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterField)
from qgis import processing
from qgis.core import QgsProject
from qgis.core import QgsCoordinateReferenceSystem, QgsProject, QgsWkbTypes,QgsFeature

class NascentesAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT = 'INPUT'
    INPUT_2='INPUT_2'
    OUTPUT = 'OUTPUT'
    OUTPUT2 = 'OUTPUT2'
    VALUE='VALUE'
    Parameter='Parameter'


    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input layer'),
                [QgsProcessing.TypeVectorLine]
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_2,
                self.tr('River Mouth'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )
        self.MU=['Minimum Value', 'Maximum Value', 'ALL']
        
        self.addParameter(
            QgsProcessingParameterEnum(
                self.Parameter,
                self.tr('Parameters'),
                self.MU
            )
        )        
        self.addParameter(
            QgsProcessingParameterNumber(
                self.VALUE,
                self.tr('Value. \nRegarding the function $leng:'),
                defaultValue=1000,
                minValue=0
                                
            )
        )        
        

        
        
        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Headwater_Lines')
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT2,
                self.tr('Headwater_Points')
            )
        )
    def shortHelpString(self):
        #DEscrever oque ele faz nada muito grande so falar que ele extrair as nascentes mesma merda que o danglge nao dagle só que tira apenas um ponto
        f='<='
        return self.tr("English:\nThe program performs a series of processes to identify and extract sources from a vector network. The extraction options include:\nALL: Extracts all sources from the network, without any filtering criteria.\nMinimum Value: Extracts sources with length less than or equal to the value defined by the user.\nMaximum Value: Extracts sources with length greater than or equal to the value defined by the user.\nThe extraction can generate results of the Line and/or Point type;\n*Line will be only the length in relation to $leng in the attribute table\n*Point, in addition to having the length, will have the attributes of the original layer in the source.\nPortuguês:\nO programa realiza uma série de processos para identificar e extrair nascentes de uma rede vetorial. As opções de extração incluem:\nALL:Extrai todas as nascentes da rede, sem nenhum critério de filtragem.\n Minimum Value: Extrai nascentes com comprimento menor ou igual ao valor definido pelo usuário.\nMaximum Value: Extrai nascentes com comprimento maior ou igual ao valor definido pelo usuário. \n A extração pode gerar resultados do tipo Linha e/ou Ponto;\n*Linha será apenas o comprimento em relação ao $leng na tabela de atributos\n*Ponto além de ter o comprimento terá os atributos da camada original na nascente.")


    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        source = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )

        # If source was not found, throw an exception to indicate that the algorithm
        # encountered a fatal error. The exception text can be any string, but in this
        # case we use the pre-built invalidSourceError method to return a standard
        # helper text for when a source cannot be evaluated
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))
#######


        
        inter=processing.run("native:lineintersections", {'INPUT':parameters['INPUT'],
        'INTERSECT':parameters['INPUT'],
        'INPUT_FIELDS':[],
        'INTERSECT_FIELDS':[],
        'INTERSECT_FIELDS_PREFIX':'',
        'OUTPUT':'memory:'})
        #buff das intersecao para fazer a contagem de pontos, isso serve para contar quantos pontos tem
        buff_p=processing.run("native:buffer",
        {'INPUT':inter['OUTPUT'],
        'DISTANCE': 1e-05,
        'DISSOLVE': False,
        'END_CAP_STYLE': 0,
        'JOIN_STYLE':0,
        'OUTPUT': 'memory:'})


        #Contagem de pontos de intersecao tem dentro deste micro buff, caso tenha apenas dois ponto quer dizer que tenha apenas dois vertices, isso quer dizer que tem uma quebra com massa d agua
        cont_p=processing.run("native:countpointsinpolygon", {'POLYGONS':buff_p['OUTPUT'],
        'POINTS':inter['OUTPUT'],
        'WEIGHT':'',
        'CLASSFIELD':'',
        'FIELD':'NUMPOINTS',
        'OUTPUT':'memory:'})
        #QgsProject.instance().addMapLayer(cont_p['OUTPUT'])


        #extrair por expressao tudo maior que 2 vertices
        expre_cont=processing.run("native:extractbyexpression",
        {'INPUT': cont_p['OUTPUT'],
        'EXPRESSION':'"NUMPOINTS" > 2 ',
        'OUTPUT':'memory:'})
        #QgsProject.instance().addMapLayer(expre_cont['OUTPUT'])

        #REMOVER as duplicadas intersse
        remove_du=processing.run("native:deleteduplicategeometries", {'INPUT':inter['OUTPUT'],
        'OUTPUT':'memory:'})

        #DISSOVER A CAMADA PRINCIPAL PARA SER QUEBRADA
        disso=processing.run("native:dissolve", {'INPUT':parameters['INPUT'],
        'FIELD':[],
        'SEPARATE_DISJOINT':False,
        'OUTPUT':'memory:'})


        #Achar as intesesao que nao so de duas linhas
        extrair=processing.run("native:extractbylocation",
        {'INPUT':remove_du['OUTPUT'],
        'INTERSECT':expre_cont['OUTPUT'],
        'PREDICATE':[0],
        'OUTPUT':'memory:'})

        #quebra os dissolvidos com as interssecao que nao sao duas interssecao
        quebra=processing.run("native:splitwithlines", {'INPUT':disso['OUTPUT'],
        'LINES':extrair['OUTPUT'],
        'OUTPUT':'memory:'})
       
        '''PARTE 2 do PROGRAMA // extrair as nascente depois extrair conforme os parametros'''



        #Extrair o vertice 0 da camada dissolvidos quebrados 
        verti_0=processing.run("native:extractspecificvertices",{
        'INPUT':quebra['OUTPUT'],
        'VERTICES':0,
        'OUTPUT':'memory:'})

        #Extrair o vertice -1 da camada quebrada a parti dos dissolvidos
        verti_1=processing.run("native:extractspecificvertices",{
        'INPUT':quebra['OUTPUT'],
        'VERTICES':-1,
        'OUTPUT':'memory:'})

        #Mesclar (unir) os output dos vertices 0 e -1 
        mescla=processing.run("native:mergevectorlayers",{
        'LAYERS':[verti_0['OUTPUT'],verti_1['OUTPUT']],
        'OUTPUT':'memory:'})


        X_Y=processing.run("native:fieldcalculator", 
        {'INPUT':mescla['OUTPUT'],
        'FIELD_NAME':'cont',
        'FIELD_LENGTH':0,
        'FIELD_PRECISION':0,
        'FORMULA':'$X + $Y\r\n\r\n',
        'OUTPUT':'memory:'})
        
        #ver quantas vezes se repete a soma se reperti mais que duas quer dizer que é intercessao
        rep=processing.run("native:fieldcalculator", {'INPUT':X_Y['OUTPUT'],
        'FIELD_NAME':'repe',
        'FIELD_TYPE':0,
        'FIELD_LENGTH':0,
        'FIELD_PRECISION':0,
        'FORMULA':'count( "cont","cont" )',
        'OUTPUT':'memory:'})
        
        #Retira os simples
        remov=processing.run("native:extractbyattribute",
        {'INPUT':rep['OUTPUT'],
        'FIELD':'repe',
        'OPERATOR':0,
        'VALUE':'1',
        'OUTPUT':'memory:'})
        
        #Achar os vertices que sao nascentes, extrair por localizaca (desunidos),  pela os mescla depois e se tem sobreposicao quer dizer que nao é nascente
        nasc=processing.run("native:extractbylocation",
        {'INPUT':mescla['OUTPUT'],
        'INTERSECT':remov['OUTPUT'],
        'PREDICATE':[0],
        'OUTPUT':'memory:'})
        

        
        
        
        '''FIM DO PROCESSO QUE EU QUERO'''
        #NAO ENTENDI PORQUE ESTA MERDA ESTAVA ATIVADA PARA GERAR.
        
        #QgsProject.instance().addMapLayer(nasc['OUTPUT'])

        #Por enquanto esta tudo como ponto, então queremos extrair os trechos das nascentes;
        #para isso ultilizando extrair por localização (interseçao)
        trech_nasc=processing.run("native:extractbylocation",
        {'INPUT':quebra['OUTPUT'],
        'INTERSECT':nasc['OUTPUT'],
        'PREDICATE':[0],
        'OUTPUT':'memory:'})
        
        #QgsProject.instance().addMapLayer(trech_nasc['OUTPUT'])
        

        
        
        
        #Aqui ele vai deletar as colunas do dissolvidos

        fields = trech_nasc['OUTPUT'].fields()
        field_names = [field.name() for field in fields]  # Lista os nomes das colunas
        
     
        
        deleta_C=processing.run("native:deletecolumn", {'INPUT':trech_nasc['OUTPUT'],
        'COLUMN':field_names,
        'OUTPUT':'memory:'})
        
        #Cria uma coluna com nos trechos de nascente e coloca a expressao $length (comprimento)
        
        calcu=processing.run("native:fieldcalculator", {'INPUT':deleta_C['OUTPUT'],
        'FIELD_NAME':'Compri',
        'FIELD_TYPE':0,
        'FIELD_LENGTH':0,
        'FIELD_PRECISION':0,
        'FORMULA':' $length ',
        'OUTPUT':'memory:'})
        
        nume=parameters['VALUE'] 
        

        #lado_=parameters['ENTE']
        la_in=self.parameterAsEnum(parameters,self.Parameter,context)
        lado=self.MU[la_in]
        
        
        #MINIMO A PARTI DE 
        if lado=='Minimum Value':
            LAD=3
        #MAXIMPO ATE
        elif lado=='Maximum Value':
            LAD=5
            
        #TUDO
        
        elif lado=='ALL':
            LAD=5
            nume=100000000000000000
        
        #QgsProject.instance().addMapLayer(calcu['OUTPUT'])

        #como a coluna feita faz uma extracao por expressao com os parametos ditos la em cima
        c=processing.run("native:extractbyattribute", 
        {'INPUT': calcu['OUTPUT'],
        'FIELD':'Compri',
        'OPERATOR':LAD,
        'VALUE':nume,
        'OUTPUT':'memory:'})
        #QgsProject.instance().addMapLayer(c['OUTPUT'])        
        
        #Cria um buff da foz/limite da folha esse buff é para 
        buff=processing.run("native:buffer",
        {'INPUT':parameters['INPUT_2'],
        'DISTANCE': 1e-05,
        'DISSOLVE': False,
        'END_CAP_STYLE': 0,
        'JOIN_STYLE':0,
        'OUTPUT': 'memory:'})
        #output2 = self.parameterAsOutputLayer(parameters, self.OUTPUT2, context)        
        #output = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
        
        #o codigo vai identifica a foz como uma nascente entao vou descarta a "nascentes" incorretas e por isso vou ultilizar o extrair por localizacao(desunido)
        nasc_sem_F=processing.run("native:extractbylocation",
        {'INPUT':c['OUTPUT'],
        'INTERSECT':buff['OUTPUT'],
        'PREDICATE':[2],
        'OUTPUT': 'memory:'})
        
        #QgsProject.instance().addMapLayer(nasc_sem_F['OUTPUT'])
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context, nasc_sem_F['OUTPUT'].fields(), nasc_sem_F['OUTPUT'].wkbType(), nasc_sem_F['OUTPUT'].sourceCrs())

            
        for feature in nasc_sem_F['OUTPUT'].getFeatures():
            geom = feature.geometry()
            new_feature = QgsFeature()
            new_feature.setGeometry(geom)
            new_feature.setAttributes(feature.attributes())
            sink.addFeature(new_feature)        

       
                
        po=processing.run("native:extractbylocation",
        {'INPUT':nasc['OUTPUT'],
        'INTERSECT':buff['OUTPUT'],
        'PREDICATE':[2],
        'OUTPUT': 'memory:'})
        
        fields_2 = po['OUTPUT'].fields()
        field_names_2 = [field.name() for field in fields_2]  # Lista os nomes das colunas 
        
        deleta_Pont=processing.run("native:deletecolumn", {'INPUT':po['OUTPUT'],
        'COLUMN':field_names_2,
        'OUTPUT':'memory:'})
        
        nas_Pon=processing.run("native:intersection", {'INPUT':deleta_Pont['OUTPUT'],
        'OVERLAY':parameters['INPUT'],
        'INPUT_FIELDS':[],
        'OVERLAY_FIELDS':[],
        'OVERLAY_FIELDS_PREFIX':'',
        'OUTPUT':'memory:'})
        
        nasc_Pont_2=processing.run("native:intersection", {'INPUT':nas_Pon['OUTPUT'],
        'OVERLAY':nasc_sem_F['OUTPUT'],
        'INPUT_FIELDS':[],
        'OVERLAY_FIELDS':[],
        'OVERLAY_FIELDS_PREFIX':'',
        'OUTPUT':'memory:'})
        
        (sink, dest_id_2) = self.parameterAsSink(parameters, self.OUTPUT2, context, nasc_Pont_2['OUTPUT'].fields(), nasc_Pont_2['OUTPUT'].wkbType(), nasc_Pont_2['OUTPUT'].sourceCrs())

            
        for feature in nasc_Pont_2['OUTPUT'].getFeatures():
            Feicao = feature.geometry()
            Nova_Feicao = QgsFeature()
            Nova_Feicao.setGeometry(Feicao)
            Nova_Feicao.setAttributes(feature.attributes())
            sink.addFeature(Nova_Feicao) 
            
        return{'OUTPUT':dest_id,'OUTPUT2':dest_id_2}

        
        
        
    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Extract Springs'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return ''

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return NascentesAlgorithm()