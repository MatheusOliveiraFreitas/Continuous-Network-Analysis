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
                       QgsProcessingFeatureSourceDefinition,
                       QgsProcessingParameterField)
from qgis import processing
from qgis.core import QgsProject
from qgis.core import QgsCoordinateReferenceSystem, QgsProject, QgsWkbTypes,QgsFeatureRequest,QgsVectorLayer, QgsVectorFileWriter,QgsFeature,QgsProcessingUtils

class ConectividadeAlgorithm(QgsProcessingAlgorithm):
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
    OUTPUT2= 'OUTPUT2'



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

        
        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Excerpt Disconnected')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT2,
                self.tr('Connected section')
            )
        )
    def shortHelpString(self):
        #DEscrever oque ele faz nada muito grande so falar que ele detecta uma descontinuidade de um atribuo 
        return self.tr("English:\nPerforms a series of procedures to verify the topological connectivity of a line layer from an initial layer (which must have intersection and/or overlap with at least one section of the network). At the end of the process, the plugin can generate two files:\n*Excerpt Disconnected: The sections of the network that are not topologically connected to the initial layer, that is, the disconnected sections.\n*Connected Section: The sections of the network that are topologically connected to the initial layer.\n Português:\nRealiza uma série de procedimentos para verificar a conectividade topológica de uma camada de linhas a partir de uma camada inicial (que deve obrigatoriamente ter interseção e/ou sobreposição com pelo menos um trecho da rede). Ao final do processo, o plugin poderar gerar dois arquivos:\n*Excerpt Disconnected:Os trechos da rede que não estão conectados topologicamente com a camada inicial, ou seja, os trechos desconectados.\n*Connected Section: Os trechos da rede que estão conectados topologicamente com a camada inicial.")


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

        if feedback.isCanceled():
            return {}  

        calcu=processing.run("native:fieldcalculator", {'INPUT':parameters['INPUT'],
        'FIELD_NAME':'id_70',
        'FIELD_TYPE':0,
        'FIELD_LENGTH':0,
        'FIELD_PRECISION':0,
        'FORMULA':'@id',
        'OUTPUT':'memory:'},context=context, feedback=feedback, is_child_algorithm=True)        
        calcu_ofici=QgsProcessingUtils.mapLayerFromString(calcu['OUTPUT'], context)
        if feedback.isCanceled():
            return {} 
        linha=processing.run("native:extractvertices", {'INPUT':calcu_ofici,
        'OUTPUT':'memory:'},context=context, feedback=feedback, is_child_algorithm=True)      
        linha_ofic=QgsProcessingUtils.mapLayerFromString(linha['OUTPUT'], context)
        if feedback.isCanceled():
            return {} 
        
        disso=processing.run("native:dissolve", {'INPUT':linha_ofic,
        'FIELD':['id_70'],
        'SEPARATE_DISJOINT':False,
        'OUTPUT':'memory:'},context=context, feedback=feedback, is_child_algorithm=True) 
        disso_ofic=QgsProcessingUtils.mapLayerFromString(disso['OUTPUT'], context)
        if feedback.isCanceled():
            return {}         
        #QgsProject.instance().addMapLayer(linha['OUTPUT'])
        
        processing.run("native:selectbylocation", {'INPUT':disso_ofic,
        'PREDICATE':[0],
        'INTERSECT':parameters['INPUT_2'],
        'METHOD':0},context=context, feedback=feedback, is_child_algorithm=True) 
        if feedback.isCanceled():
            return {}             
            
        disso_ofic.setName('BBBBBBBBBBBBBBBBBBBBBBBBBB')    
        QgsProject.instance().addMapLayer(disso_ofic)        
        
        while True:
            if feedback.isCanceled():
                return {} 
            num_selected_features_1 = disso_ofic.selectedFeatureCount()
            
            processing.run("qgis:selectbylocation", {'INPUT' : disso_ofic,
            'INTERSECT' :  QgsProcessingFeatureSourceDefinition('BBBBBBBBBBBBBBBBBBBBBBBBBB',
            selectedFeaturesOnly=True, featureLimit=-1, geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),
            'METHOD' : 0,
            'PREDICATE' : [0],
            'OUTPUT': 'memory:'})
            
            num_selected_features = disso_ofic.selectedFeatureCount()
            if num_selected_features_1==num_selected_features:
                c=processing.run("native:saveselectedfeatures", {'INPUT':disso_ofic,                
                'OUTPUT':'memory:'},context=context, feedback=feedback, is_child_algorithm=True)
                c_ofic=QgsProcessingUtils.mapLayerFromString(c['OUTPUT'], context)
                #QgsProject.instance().addMapLayer(c['OUTPUT'])
                break
                
        deletar=QgsProject.instance().mapLayersByName('BBBBBBBBBBBBBBBBBBBBBBBBBB')    
        QgsProject.instance().removeMapLayer(deletar[0])
        demi=processing.run("native:extractbylocation",
        {'INPUT':disso_ofic,
        'INTERSECT':c_ofic,
        'PREDICATE':[2],
        'OUTPUT':'memory:'},context=context, feedback=feedback, is_child_algorithm=True) 
        demi_ofic=QgsProcessingUtils.mapLayerFromString(demi['OUTPUT'], context)
        if feedback.isCanceled():
            return {} 
        
        desco=processing.run("native:extractbylocation",
        {'INPUT':parameters['INPUT'],
        'INTERSECT':demi_ofic,
        'PREDICATE':[0],
        'OUTPUT':'memory:'},context=context, feedback=feedback, is_child_algorithm=True) 
        desco_ofic=QgsProcessingUtils.mapLayerFromString(desco['OUTPUT'], context)
        if feedback.isCanceled():
            return {}         
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context, desco_ofic.fields(), desco_ofic.wkbType(), desco_ofic.sourceCrs())

            
        for feature in desco_ofic.getFeatures():
            geometria = feature.geometry()
            Feicao = QgsFeature()
            Feicao.setGeometry(geometria)
            Feicao.setAttributes(feature.attributes())
            sink.addFeature(Feicao)

            
        demi_cone=processing.run("native:extractbylocation",
        {'INPUT':disso_ofic,
        'INTERSECT':c_ofic,
        'PREDICATE':[0],
        'OUTPUT':'memory:'},context=context, feedback=feedback, is_child_algorithm=True) 
        demi_cone_ofic=QgsProcessingUtils.mapLayerFromString(demi_cone['OUTPUT'], context)
        if feedback.isCanceled():
            return {}                 

        
        desco_coe=processing.run("native:extractbylocation",
        {'INPUT':parameters['INPUT'],
        'INTERSECT':demi_cone_ofic,
        'PREDICATE':[0],
        'OUTPUT':'memory:'},context=context, feedback=feedback, is_child_algorithm=True)  
        desco_coe_ofic=QgsProcessingUtils.mapLayerFromString(desco_coe['OUTPUT'], context)
        if feedback.isCanceled():
            return {}         
        (sink2, dest_id2) = self.parameterAsSink(parameters, self.OUTPUT2, context, desco_coe_ofic.fields(), desco_coe_ofic.wkbType(), desco_coe_ofic.sourceCrs())
        for feature in desco_coe_ofic.getFeatures():
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
        return 'Disconnected Network Segments'

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
        return ConectividadeAlgorithm()