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
from qgis.core import QgsCoordinateReferenceSystem, QgsProject, QgsWkbTypes, QgsVectorFileWriter,QgsVectorLayer,QgsField,QgsFeature,QgsProcessingUtils
from qgis.PyQt.QtCore import QVariant
class DANGOS_NAO_DANGOS(QgsProcessingAlgorithm):
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
                self.tr('DANGLES_Overlapping')
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT2,
                self.tr('DANGLES_Non_Overlap')
            )
        )
        
    def shortHelpString(self):
        #DEscrever oque ele faz nada muito grande so falar que ele detecta uma descontinuidade de um atribuo 
        return self.tr("English:\nIdentifies dangles (line sections that do not connect to other lines) in a vector network layer and checks the overlap of these dangles with several layers selected by the user.\n Thus, two files can be generated;\n*DANGLES_Non_Overlap which are the loose ends that do not overlap and/or intersect with the selected layers.\n*DANGLES_Overlapping which are the loose ends (Dangles) that do overlap and/or intersect.\n\n Portuquês:\nIdentifica dangles (trechos de linha que não se conectam a outras linhas) em uma camada de rede vetorial e verifica a sobreposição desses dangles com várias camadas selecionadas pelo usuário.\n Assim podendo gerar dois arquivos;\n*DANGLES_Non_Overlap que são as pontas soltas que não tem sobreposição e/ou interseção com as camadas selecionadas.\n*DANGLES_Overlapping que são as pontas soltas(Dangles) que tem sobreposição e/ou interseção.")


    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))



        try:
            nasc=processing.run("Continuous_Network_Analysis:Identify Dangles", {'INPUT':parameters['INPUT'],
            'OUTPUT':'memory:'}, context=context, feedback=feedback, is_child_algorithm=True)
            
            nas_ofici=QgsProcessingUtils.mapLayerFromString(nasc['OUTPUT'], context)
            
            nas_ofici.startEditing()
            nasc_provider = nas_ofici.dataProvider()

            index_status = nasc_provider.hasSpatialIndex()            
            if index_status== 1:
                #feedback.pushInfo('Sem indice espacial')
                processing.run("native:createspatialindex", 
                {'INPUT': nas_ofici}, 
                context=context, feedback=feedback, is_child_algorithm=True)
            
            nasc_provider.addAttributes([QgsField("layer_overlap", QVariant.String, len=100)])
            nas_ofici.updateFields()            
            
        except Exception as erro:
            if feedback.isCanceled():
                return {}
            else:
                raise erro
 
        selected_indices = self.parameterAsEnums(parameters, self.LAYERS, context)
        selected_layer_names = [self.parameterDefinition(self.LAYERS).options()[i] for i in selected_indices]
        #feedback.pushInfo(f'Selected Layer: {selected_layer_name}')
       

        layers = [layer for layer in QgsProject.instance().mapLayers().values() if layer.name() in selected_layer_names]
         

        
        #Gerando as camadas de Saida
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            nas_ofici.fields(), # Preserva os mesmos campos da camada de entrada
            QgsWkbTypes.Point, # A saída será de pontos
            source.sourceCrs() # Usa o mesmo CRS da camada de entrada
        )    
        (sink_2, dest_id_2) = self.parameterAsSink(
            parameters,
            self.OUTPUT2,
            context,
            source.fields(), # Preserva os mesmos campos da camada de entrada
            QgsWkbTypes.Point, # A saída será de pontos
            source.sourceCrs() # Usa o mesmo CRS da camada de entrada
        )    

    
        lista_de_pontos=[]
        lista_de_poligonos=[]
        lista_de_Linhas=[]
        buffers_merge_final = [] 
        try:
            for layer in layers:
                tipo = layer.wkbType()

                    
                if tipo in [QgsWkbTypes.LineString, QgsWkbTypes.MultiLineString]:
                    
                    lista_de_Linhas.append(layer)
                    
                elif tipo in [QgsWkbTypes.Point, QgsWkbTypes.MultiPoint]:
                    lista_de_pontos.append(layer)
                    
                elif tipo in [QgsWkbTypes.Polygon, QgsWkbTypes.MultiPolygon]:
                    lista_de_poligonos.append(layer)
                    
            if lista_de_pontos:
                #Mesclar todas as camadas do tipo ponto
                merge_point_result = processing.run(
                "native:mergevectorlayers",
                {'LAYERS': lista_de_pontos, 'OUTPUT': 'memory:'}, context=context, feedback=feedback, is_child_algorithm=True)
                merge_point_result_ofic=QgsProcessingUtils.mapLayerFromString(merge_point_result['OUTPUT'], context)
                
                #Fazer o buffer do merge do tipo ponto
                buffer_point = processing.run("native:buffer",
                {'INPUT': merge_point_result_ofic, 'DISTANCE': 0.000001, 'DISSOLVE': False, 'OUTPUT': 'memory:'}, context=context, feedback=feedback, is_child_algorithm=True)
                buffer_point_ofic=QgsProcessingUtils.mapLayerFromString(buffer_point['OUTPUT'], context)
                
                #Adicionar em uma lista 
                buffers_merge_final.append(buffer_point_ofic)
                
            if lista_de_Linhas:
                #Mesclar todas as camadas do tipo ponto
                merge_Linha_result = processing.run(
                "native:mergevectorlayers",
                {'LAYERS': lista_de_Linhas, 'OUTPUT': 'memory:'}, context=context, feedback=feedback, is_child_algorithm=True)
                merge_Linha_result_ofic=QgsProcessingUtils.mapLayerFromString(merge_Linha_result['OUTPUT'], context)
                
                #Fazer o buffer do merge do tipo Linha
                buffer_Linha = processing.run("native:buffer",
                {'INPUT': merge_Linha_result_ofic, 'DISTANCE': 0.000001, 'DISSOLVE': False, 'OUTPUT': 'memory:'}, context=context, feedback=feedback, is_child_algorithm=True)
                buffer_Linha_ofic=QgsProcessingUtils.mapLayerFromString(buffer_Linha['OUTPUT'], context)
                
                #Adicionar em uma lista 
                buffers_merge_final.append(buffer_Linha_ofic)
                
            if lista_de_poligonos:
                #Mesclar todas as camadas do tipo poligonos
                merge_Poligono_result = processing.run(
                "native:mergevectorlayers",
                {'LAYERS': lista_de_poligonos, 'OUTPUT': 'TEMPORARY_OUTPUT'}, context=context, feedback=feedback, is_child_algorithm=True)
                merge_Poligono_result_ofic=QgsProcessingUtils.mapLayerFromString(merge_Poligono_result['OUTPUT'], context)
                
                #Nao precisa de um buffer para o poligono se torna um poligono
                buffers_merge_final.append(merge_Poligono_result_ofic)
        except Exception as erro:
            if feedback.isCanceled():
                return {}
            else:
                raise erro
    
        try:
            Juntar = processing.run(
            "native:mergevectorlayers",
            {'LAYERS': buffers_merge_final,
            'OUTPUT': 'memory:'}, context=context, feedback=feedback, is_child_algorithm=True)
            Juntar_ofic=QgsProcessingUtils.mapLayerFromString(Juntar['OUTPUT'], context)
            
            Juntar_ofic_provider = Juntar_ofic.dataProvider()

            index_status_Juntar = Juntar_ofic_provider.hasSpatialIndex()            
            if index_status_Juntar== 1:
                #feedback.pushInfo('Sem indice espacial')
                processing.run("native:createspatialindex", 
                {'INPUT': Juntar_ofic}, 
                context=context, feedback=feedback, is_child_algorithm=True)           
            
            
            
            Campo_Layer_index_Prin = nas_ofici.fields().indexOf("layer_overlap") # Atualiza o índice do campo
     
            
            extrac_dango=processing.run("native:intersection", {
            'INPUT': nas_ofici,
            'OVERLAY': Juntar_ofic,
            'INPUT_FIELDS': [], # Selecione aqui os campos do dangle que quer manter
            'OVERLAY_FIELDS': [], # Selecione os campos da camada de sobreposição que quer adicionar
            'OUTPUT': 'TEMPORARY_OUTPUT'
            }, context=context, feedback=feedback, is_child_algorithm=True)  
            
           
            
            dango_ofici=QgsProcessingUtils.mapLayerFromString(extrac_dango['OUTPUT'], context)
            #QgsProject.instance().addMapLayer(dango_ofici)
            field_index = dango_ofici.fields().indexOf("layer")          
            
            for dango in dango_ofici.getFeatures():
                geometria_dango=dango.geometry()
                new_feature = QgsFeature()
                new_feature.setGeometry(geometria_dango)

                # copia atributos da camada principal
                attributes = dango.attributes()
                #Adcionar valor layer_overla/ Neste caso por exemplo eu já gerei a coluna então eu preciso pegar 2 indece o da camada principal
                #e falar qual indece tipo pega o atributo da coluna da camada secundaria seu indece é 3 e colocar na coluna principal com indice 10
                valor_sec = dango.attributes()[field_index]
                attributes[Campo_Layer_index_Prin] = valor_sec
                        
                new_feature.setAttributes(attributes)
                sink.addFeature(new_feature, QgsFeatureSink.FastInsert)

            extrac_nao_dango=processing.run("native:extractbylocation",
            {'INPUT':nas_ofici,
            'INTERSECT':Juntar_ofic,
            'PREDICATE':[2],
            'OUTPUT':'memory:' },
            context=context, feedback=feedback, is_child_algorithm=True)
            nao_dango_ofici=QgsProcessingUtils.mapLayerFromString(extrac_nao_dango['OUTPUT'], context)
            
            for feature in nao_dango_ofici.getFeatures():
                sink_2.addFeature(feature, QgsFeatureSink.FastInsert)
        except Exception as erro:
            if feedback.isCanceled():
                return {}
            else:
                raise erro               
            
            
        return {self.OUTPUT: dest_id, self.OUTPUT2:dest_id_2}

        
        
        
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