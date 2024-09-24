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
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsProcessingFeatureSourceDefinition,
                       QgsProcessingParameterField)
from qgis import processing
from qgis.core import QgsProject
from qgis.core import QgsCoordinateReferenceSystem, QgsProject, QgsWkbTypes,QgsProcessingUtils,QgsFeature
class Dangles(QgsProcessingAlgorithm):
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

    OUTPUT = 'OUTPUT'



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


        
        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Dangles'),
                QgsProcessing.TypeVectorPoint
            )
        )
        
    def shortHelpString(self):
        #DEscrever oque ele faz nada muito grande so falar que ele detecta uma descontinuidade de um atribuo 
        return self.tr("Finds dangles (loose ends) in a line type layer\nPortuguês:\nEncontra Dangles (pontas soltas) em uma camada de tipo de linha")
        


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
        #output = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
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
 
        fields = nasc['OUTPUT'].fields()
        field_names = [field.name() for field in fields]  # Lista os nomes das colunas
        
        
        deleta_C=processing.run("native:deletecolumn", {'INPUT':nasc['OUTPUT'],
        'COLUMN':field_names,
        'OUTPUT':'memory:'})
        


         
        # Executar o algoritmo de interseção
        FINAL = processing.run("native:intersection", {
            'INPUT': deleta_C['OUTPUT'],
            'OVERLAY': parameters['INPUT'],
            'INPUT_FIELDS': [],
            'OVERLAY_FIELDS': [],
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT':'memory:'})
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context, FINAL['OUTPUT'].fields(), FINAL['OUTPUT'].wkbType(), FINAL['OUTPUT'].sourceCrs())

            
        for feature in FINAL['OUTPUT'].getFeatures():
            geom = feature.geometry()
            new_feature = QgsFeature()
            new_feature.setGeometry(geom)
            new_feature.setAttributes(feature.attributes())
            sink.addFeature(new_feature)
        
        return {self.OUTPUT: dest_id}
            

        
        
        
    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Identify Dangles'

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
        return Dangles()