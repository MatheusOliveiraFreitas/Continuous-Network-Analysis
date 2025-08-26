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
class Pseudo_node_Analysis(QgsProcessingAlgorithm):
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
        
        layers=[ layer.name() for layer in QgsProject.instance().mapLayers().values()]
        

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
                self.tr('Pseudo-node Non_Overlap'),
                QgsProcessing.TypeVectorPoint
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT2,
                self.tr('Pseudo-node Overlapping')
            )
        )       
    def shortHelpString(self):
        #DEscrever oque ele faz nada muito grande so falar que ele detecta uma descontinuidade de um atribuo 
        return self.tr("🔹 Pseudo-node Analysis\nIt analyzes whether the breaks (Pseudo-node) are topologically connected to the vertices of the layers that the user selected.\n • Returns Non_Overlap Pseudo-node, Pseudo-node that is not topologically connected to any vertex of the selected layers.\n • Returns Overlapping Pseudo-node, Pseudo-node that is topologically connected to any vertex of the selected layers, in addition to having a column that identifies which layer each vertex is topologically connected to.\n🔹 Pseudo-node Analysis\n Português:\n  Ele analisa se as quebras (Pseudo-node) estão topologicamente conectadas nos vértices das camadas que usuário selecionou.\n •	Retorna Pseudo-node sem conexão, Pseudo-node que não estão conectados topologicamente em nenhum vértice das camadas selecionadas.\n •	Retorna Pseudo-node com conexão, Pseudo-node que estão conectados topologicamente com algum vértice das camadas selecionadas, além disso tem uma coluna que identifica qual camada cada vértice está topologicamente conectado.")
        

    def TIPO(self,layer):
        tipo = layer.geometryType()

        if tipo == QgsWkbTypes.PointGeometry:
            rep = 'Point'
        elif tipo == QgsWkbTypes.LineGeometry:
            rep = 'Line'
        elif tipo == QgsWkbTypes.PolygonGeometry:
            rep = 'Polygon'
        elif tipo == QgsWkbTypes.MultiPoint:
            rep = 'MultiPoint'
        elif tipo == QgsWkbTypes.MultiLineString:
            rep = 'MultiLineString'
        elif tipo == QgsWkbTypes.MultiPolygon:
            rep = 'MultiPolygon'
        return rep
    
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


        # Adiciona um campo ID da feição original
        try:
            pseu=processing.run("Continuous_Network_Analysis:Pseudo-node",
            {'INPUT':parameters['INPUT'],
            'OUTPUT':'TEMPORARY_OUTPUT'},
            context=context, feedback=feedback, is_child_algorithm=True)            
            pseu_ofici=QgsProcessingUtils.mapLayerFromString(pseu['OUTPUT'], context)  
            prove=pseu_ofici.dataProvider()
            
            index_status = prove.hasSpatialIndex()            
            if index_status== 1:
                #feedback.pushInfo('Sem indice espacial')
                processing.run("native:createspatialindex", 
                {'INPUT': pseu_ofici}, 
                context=context, feedback=feedback, is_child_algorithm=True)
              
        except Exception as erro:
            if feedback.isCanceled():
                return {}
            else:
                raise erro
        
        #QgsProject.instance().addMapLayer(duplicate_layer)
        selected_indices = self.parameterAsEnums(parameters, self.LAYERS, context)
        selected_layer_names = [self.parameterDefinition(self.LAYERS).options()[i] for i in selected_indices]                 
        layers = [layer for layer in QgsProject.instance().mapLayers().values() if layer.name() in selected_layer_names]
        
        #feedback.pushInfo(f'Selected Layer: {selected_layer_name}')
        crs = source.sourceCrs()
        output_layer = QgsVectorLayer(f'Point?crs=EPSG:{crs.authid()}', 'Vertice_das_camadas_selecionadas', 'memory')
        output_layer.startEditing()
        provider_output_layer = output_layer.dataProvider()
         
        # Verifica se a coluna "Layer_Name" existe, se não, adiciona
        

        provider_output_layer.addAttributes([QgsField("Layer_Name", QVariant.String, len=100)])
        output_layer.updateFields()
        field_index = provider_output_layer.fields().lookupField("Layer_Name")  # Atualiza o índice do campo
        try:
            for layer in layers:
                Tip_lay=self.TIPO(layer)
                
                
                if Tip_lay in['Point','MultiPoint']:
                
                    for Camada_ponto in layer.getFeatures():
                    
                        GE=Camada_ponto.geometry()
                        nova_feature = QgsFeature(output_layer.fields())
                        nova_feature.setGeometry(GE)
                        attributes = Camada_ponto.attributes()
                        while len(attributes) <= field_index:  # Evita erro de índice
                            attributes.append(None)
                        attributes[field_index] = layer.name()
                     
                        nova_feature.setAttributes(attributes)
                        provider_output_layer.addFeature(nova_feature)
                        
                        

                elif Tip_lay in ['Polygon','MultiPolygon']:
                        
                    for Camada in layer.getFeatures():
                        a=Camada.geometry()
                                 
                        if a.isMultipart():
                            geometria_1=Camada.geometry()
                            geometria_1.asMultiPolygon()
                            polygons = geometria_1.asMultiPolygon()
                            for polygon in polygons:
                                
                                for ring in polygon:
                                    for ring_2 in ring:
                                        nova=QgsFeature(output_layer.fields())
                                        geometra=QgsGeometry.fromPointXY(ring_2)
                                        nova.setGeometry(geometra)
                                        attributes = Camada.attributes()
                                        
                                        while len(attributes) <= field_index:  # Evita erro de índice
                                            attributes.append(None)
                                        attributes[field_index] = layer.name()
                     
                                        nova.setAttributes(attributes)
                                        provider_output_layer.addFeature(nova)
                                        
                                        
                        else:
                            geometria_2=Camada.geometry()
                            polygons_2=geometria_2.asPolygon()
                            for polygon_2 in polygons_2:
                                for ring_1 in polygon_2:
                                        nova=QgsFeature(output_layer.fields())
                                        geometra_2=QgsGeometry.fromPointXY(ring_1)
                                        nova.setGeometry(geometra_2)
                                        attributes = Camada.attributes()
                                        while len(attributes) <= field_index:  # Evita erro de índice
                                            attributes.append(None)
                                        attributes[field_index] = layer.name()
                     
                                        nova.setAttributes(attributes)
                                        provider_output_layer.addFeature(nova)
                                        
                                   
                   
                else:
                    for feicao in layer.getFeatures():
                        geo=feicao.geometry()
                        
                        if geo.isMultipart():
                            geome=geo.asMultiPolyline()    
                            for feicao_2 in geome:
                                for feicao_3 in feicao_2:

                                    nova=QgsFeature(output_layer.fields())
                                    geometra=QgsGeometry.fromPointXY(feicao_3)
                                    nova.setGeometry(geometra)
                                    attributes = feicao.attributes()
                                    while len(attributes) <= field_index:  # Evita erro de índice
                                        attributes.append(None)
                                    attributes[field_index] = layer.name()
                         
                                    nova.setAttributes(attributes)
                                    provider_output_layer.addFeature(nova)
                                    
                        else:
                            geome=geo.asPolyline()    
                            for feicao_4 in geome:        
                                nova=QgsFeature()
                                
                                geometra=QgsGeometry.fromPointXY(feicao_4)
                                nova.setGeometry(geometra)
                                attributes = feicao.attributes()
                                while len(attributes) <= field_index:  # Evita erro de índice
                                    attributes.append(None)
                                attributes[field_index] = layer.name()
                         
                                nova.setAttributes(attributes)
                                provider_output_layer.addFeature(nova)
        except Exception as erro:
            if feedback.isCanceled():
                return {}
            else:
                raise erro                            
                        
        output_layer.commitChanges()
        try:
            dan=processing.run("native:extractbylocation",
            {'INPUT':pseu_ofici,
            'INTERSECT':output_layer,
            'PREDICATE':[2],
            'OUTPUT':'memory:'},
            context=context, feedback=feedback, is_child_algorithm=True)            
            nao_pseu_ofici=QgsProcessingUtils.mapLayerFromString(dan['OUTPUT'], context)

          
            
            (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context, nao_pseu_ofici.fields(), nao_pseu_ofici.wkbType(), nao_pseu_ofici.sourceCrs())
            
            #(sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context, duplicate_layer.fields(), duplicate_layer.wkbType(), duplicate_layer.sourceCrs())

                
            for feature in nao_pseu_ofici.getFeatures():
                sink.addFeature(feature, QgsFeatureSink.FastInsert)
        except Exception as erro:
            if feedback.isCanceled():
                return {}
            else:
                raise erro 
        try:            
            dan_2=processing.run("native:intersection", {
            'INPUT': pseu_ofici,
            'OVERLAY': output_layer,
            'INPUT_FIELDS': [], # Selecione aqui os campos do dangle que quer manter
            'OVERLAY_FIELDS': [], # Selecione os campos da camada de sobreposição que quer adicionar
            'OUTPUT': 'TEMPORARY_OUTPUT'},
             context=context, feedback=feedback, is_child_algorithm=True)            
            pseu_ofici_final=QgsProcessingUtils.mapLayerFromString(dan_2['OUTPUT'], context)



            (sink2, dest_id2) = self.parameterAsSink(parameters, self.OUTPUT2, context, pseu_ofici_final.fields(), pseu_ofici_final.wkbType(), pseu_ofici_final.sourceCrs())
            for feature in pseu_ofici_final.getFeatures():
                sink2.addFeature(feature, QgsFeatureSink.FastInsert)
        except Exception as erro:
            if feedback.isCanceled():
                return {}
            else:
                raise erro             
        
        return{'OUTPUT':dest_id,'OUTPUT2':dest_id2}       

            

        
        
        
    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Pseudo-node Analysis'

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
        return Pseudo_node_Analysis()