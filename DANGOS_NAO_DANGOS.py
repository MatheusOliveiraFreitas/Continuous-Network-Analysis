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
from qgis.core import QgsCoordinateReferenceSystem, QgsProject, QgsWkbTypes, QgsVectorFileWriter,QgsVectorLayer,QgsField,QgsFeature
from qgis.PyQt.QtCore import QVariant
class DANGOS_NAO_DANGOS(QgsProcessingAlgorithm):
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

    LAYERS='LAYERS'

    OUTPUT = 'OUTPUT'
    OUTPUT2 = 'OUTPUT2'

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

        layers=[ layer.name() for layer in QgsProject.instance().mapLayers().values() if isinstance (layer, QgsVectorLayer)]
        
        self.addParameter(
            QgsProcessingParameterEnum(
                self.LAYERS,
                self.tr('Choose the layers you overlap on the dangles'),
                options=layers,
                allowMultiple = True,
                
            )
        )
        
        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('DANGLES_Non_Overlap')
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT2,
                self.tr('DANGLES_Overlapping')
            )
        )
        
    def shortHelpString(self):
        #DEscrever oque ele faz nada muito grande so falar que ele detecta uma descontinuidade de um atribuo 
        return self.tr("English:\nIdentifies dangles (line sections that do not connect to other lines) in a vector network layer and checks the overlap of these dangles with several layers selected by the user.\n Thus, two files can be generated;\n*DANGLES_Non_Overlap which are the loose ends that do not overlap and/or intersect with the selected layers.\n*DANGLES_Overlapping which are the loose ends (Dangles) that do overlap and/or intersect.\n\n Portuquês:\nIdentifica dangles (trechos de linha que não se conectam a outras linhas) em uma camada de rede vetorial e verifica a sobreposição desses dangles com várias camadas selecionadas pelo usuário.\n Assim podendo gerar dois arquivos;\n*DANGLES_Non_Overlap que são as pontas soltas que não tem sobreposição e/ou interseção com as camadas selecionadas.\n*DANGLES_Overlapping que são as pontas soltas(Dangles) que tem sobreposição e/ou interseção.")


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


        

        
        nasc=processing.run("Continuous_Network_Analysis:Identify Dangles", {'INPUT':parameters['INPUT'],
        'OUTPUT':'memory:'})
        crs_in=nasc['OUTPUT'].sourceCrs()
        selected_indices = self.parameterAsEnums(parameters, self.LAYERS, context)
        selected_layer_names = [self.parameterDefinition(self.LAYERS).options()[i] for i in selected_indices]
        #feedback.pushInfo(f'Selected Layer: {selected_layer_name}')
        output_layer = QgsVectorLayer(f'Polygon?crs=EPSG:{crs_in}', 'Buffer Output', 'memory')
        provider = output_layer.dataProvider()

        provider.addAttributes([QgsField("id", QVariant.Int)])
        output_layer.updateFields()      

        layers = [layer for layer in QgsProject.instance().mapLayers().values() if layer.name() in selected_layer_names]
         
        output_layer.startEditing()
        provider = output_layer.dataProvider()
         
        # Verifica se a coluna "Layer_Name" existe, se não, adiciona
        

        provider.addAttributes([QgsField("Layer_Name", QVariant.String, len=100)])
        output_layer.updateFields()
        field_index = provider.fields().lookupField("Layer_Name")  # Atualiza o índice do campo
         
        for layer in layers:
            feedback.pushInfo(f'Selected Layer: {layer.name()}')
             
                # Criar buffer da camada de entrada
            buff_p = processing.run("native:buffer", {
                    'INPUT': layer,
                    'DISTANCE': 0.000001,
                    'DISSOLVE': False,
                    'END_CAP_STYLE': 0,
                    'JOIN_STYLE': 0,
                    'OUTPUT': 'TEMPORARY_OUTPUT'
                }, context=context, feedback=feedback)['OUTPUT']
             
            for feature in buff_p.getFeatures():
                new_feature = QgsFeature(output_layer.fields())
                new_feature.setGeometry(feature.geometry())
             
                # Copiar os atributos da feature original
                attributes = feature.attributes()
             
                # Adicionar o nome da camada na coluna "Layer_Name"
                
                while len(attributes) <= field_index:  # Evita erro de índice
                    attributes.append(None)
                attributes[field_index] = layer.name()
         
                new_feature.setAttributes(attributes)
                provider.addFeature(new_feature)
         
            output_layer.commitChanges()
            

            # Adiciona a camada de saída ao projeto
            #QgsProject.instance().addMapLayer(output_layer)
            

         
        fields = nasc['OUTPUT'].fields()
        field_names = [field.name() for field in fields]  # Lista os nomes das colunas
        
        #output = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
        #output2 = self.parameterAsOutputLayer(parameters, self.OUTPUT2, context)        
        
        '''deleta_C=processing.run("native:deletecolumn", {'INPUT':nasc['OUTPUT'],
        'COLUMN':field_names,
        'OUTPUT':'memory:'})'''
        
        dan=processing.run("native:extractbylocation",
        {'INPUT':nasc['OUTPUT'],
        'INTERSECT':output_layer,
        'PREDICATE':[2],
        'OUTPUT':'memory:'}) 
        
      
        
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context, nasc['OUTPUT'].fields(), dan['OUTPUT'].wkbType(), dan['OUTPUT'].sourceCrs())

            
        for feature in dan['OUTPUT'].getFeatures():
            geom = feature.geometry()
            new_feature = QgsFeature()
            new_feature.setGeometry(geom)
            new_feature.setAttributes(feature.attributes())
            sink.addFeature(new_feature)
        
        
        dan_2=processing.run("native:intersection", {'INPUT':nasc['OUTPUT'],
        'OVERLAY':output_layer,
        'INPUT_FIELDS':[],
        'OVERLAY_FIELDS':[],
        'OVERLAY_FIELDS_PREFIX':'',
        'OUTPUT':'memory:'})
        

        (sink2, dest_id2) = self.parameterAsSink(parameters, self.OUTPUT2, context, dan_2['OUTPUT'].fields(), dan_2['OUTPUT'].wkbType(), dan_2['OUTPUT'].sourceCrs())

            
        for feature in dan_2['OUTPUT'].getFeatures():
            geom_2 = feature.geometry()
            nova_Feicao = QgsFeature()
            nova_Feicao.setGeometry(geom_2)
            nova_Feicao.setAttributes(feature.attributes())
            sink2.addFeature(nova_Feicao)       

        return{'OUTPUT':dest_id,'OUTPUT2':dest_id2}

        
        
        
    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Dangle Analysis'

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
        return DANGOS_NAO_DANGOS()