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
from collections import defaultdict
from qgis.PyQt.QtCore import QVariant
from qgis.core import QgsProject
from qgis.core import QgsCoordinateReferenceSystem, QgsProject, QgsWkbTypes,QgsProcessingUtils,QgsFeature, QgsVectorLayer, QgsField,QgsPointXY,QgsGeometry
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

        crs=QgsProject.instance().crs()
        
        duplicate_layer = QgsVectorLayer(f"Point?crs=EPSG:{crs}", "Vértices Duplicados", "memory")
        provider = duplicate_layer.dataProvider()
        
        # Adiciona um campo ID da feição original

     
        vertex_counts = defaultdict(int)  # Dicionário para contar ocorrências dos vértices
        vertex_features = defaultdict(list)  # Armazena feições para os vértices duplicados
     
        source = self.parameterAsSource(parameters, self.INPUT, context)
        provider.addAttributes(source.fields())
        duplicate_layer.updateFields()
        
        for feature in source.getFeatures():
            geom = feature.geometry()
            if geom.isMultipart():
                lines = geom.asMultiPolyline()
            else:
                lines = [geom.asPolyline()]
            

           
            for line in lines:
                if len(line) > 1:
                    for i, tipo in [(0, "start"), (-1, "end")]:
                        point = QgsPointXY(line[i])
                        vertex_counts[point] += 1
                        vertex_features[point].append((feature, tipo))
                            
        # Segundo loop: Criar feições apenas para os vértices repetidos
        features_to_add = []
        for point, count in vertex_counts.items():
            if count == 1:  # Se for um dangle
                for feature, tipo in vertex_features[point]:
                    new_feat = QgsFeature()
                    new_feat.setGeometry(QgsGeometry.fromPointXY(point))
                    new_feat.setAttributes(feature.attributes())  # Preserva atributos
                    features_to_add.append(new_feat)
         
        # Adiciona os pontos duplicados à camada
        provider.addFeatures(features_to_add)
        duplicate_layer.updateExtents()
        #QgsProject.instance().addMapLayer(duplicate_layer)
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context, duplicate_layer.fields(), duplicate_layer.wkbType(), duplicate_layer.sourceCrs())

            
        for feature in duplicate_layer.getFeatures():
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