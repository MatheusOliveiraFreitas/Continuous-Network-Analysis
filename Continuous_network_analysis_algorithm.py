# -*- coding: utf-8 -*-

"""
/***************************************************************************
 ContinuousNetworkAnalysis
                                 A QGIS plugin
 Vector network analysis procedures
Network connectivity
Locate sources (geometry independent)
Attribute discontinuity in a network (Attribute must be continuous)
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2024-07-30
        copyright            : (C) 2024 by Matheus Oliveira de Freitas
        email                : matheus18.1@yahoo.com.br
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Matheus Oliveira de Freitas'
__date__ = '2024-07-30'
__copyright__ = '(C) 2024 by Matheus Oliveira de Freitas'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterVectorDestination,
                       QgsProcessingParameterField)
from qgis import processing
from qgis.core import QgsProject
from qgis.core import QgsCoordinateReferenceSystem, QgsProject, QgsWkbTypes,QgsFeature,QgsVectorLayer

class ContinuousNetworkAnalysisAlgorithm(QgsProcessingAlgorithm):
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

    OUTPUT = 'OUTPUT'
    INPUT = 'INPUT'
    FIELD='FIELD'
    def initAlgorithm(self, config):
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
        #Campo
        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD,
                self.tr('Select the attribute column that cannot be stopped'),
                '',
                self.INPUT
            )
        )
        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Discontinuity')
            )
        )
    def shortHelpString(self):
        #DEscrever oque ele faz nada muito grande so falar que ele detecta uma descontinuidade de um atribuo 
        return self.tr("English:\n It performs a series of processes to identify discontinuities of a selected attribute within a line-type vector network and generates a file that points out the attribute discontinuities along the network.\nThe accuracy of the final result depends directly on the quality of the network flow — the better the flow, the greater the accuracy.\nPortuguês:\n Realiza uma série de processos para identificar descontinuidades de atributo selecionado dentro de uma rede vetorial do tipo linha e gera um arquivo que aponta as descontinuidades do atributo ao longo da rede.\nA precisão do resultado final depende diretamente da qualidade do fluxo da rede — quanto melhor o fluxo, maior será a precisão.")
        
        
    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        source = self.parameterAsSource(parameters, self.INPUT, context)
        field_name = self.parameterAsString(parameters, self.FIELD, context)



        a=parameters['FIELD']       
        
        quebra=processing.run("native:splitwithlines", {'INPUT':parameters['INPUT'],
        'LINES':parameters['INPUT'],
        'OUTPUT':'memory:'})
        
        nome=processing.run("native:extractbyexpression",
        {'INPUT': quebra['OUTPUT'],
        'EXPRESSION':f'{a} is not null',
        'OUTPUT':'memory:'})
        
        verti_0=processing.run("native:extractspecificvertices",{
        'INPUT':nome['OUTPUT'],
        'VERTICES':0,
        'OUTPUT':'memory:'})

        #Extrair o vertice -1 da camada quebrada a parti dos dissolvidos
        verti_1=processing.run("native:extractspecificvertices",{
        'INPUT':nome['OUTPUT'],
        'VERTICES':-1,
        'OUTPUT':'memory:'})

        #Mesclar (unir) os output dos vertices 0 e -1 
        mescla=processing.run("native:mergevectorlayers",{
        'LAYERS':[verti_0['OUTPUT'],verti_1['OUTPUT']],
        'OUTPUT':'memory:'})
     
        
        quebra=processing.run("native:splitwithlines", {'INPUT':parameters['INPUT'],
        'LINES':parameters['INPUT'],
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
              
        #QgsProject.instance().addMapLayer(remov['OUTPUT'])
        
        #PARTE 2 DO PROGRAMA'
        
        sem_nome=processing.run("native:extractbyexpression",
        {'INPUT': quebra['OUTPUT'],
        'EXPRESSION':f'"{a}" is NULL or "{a}"  =\' \'',
        'OUTPUT':'memory:'})

        verti_0_sem=processing.run("native:extractspecificvertices",{
        'INPUT':sem_nome['OUTPUT'],
        'VERTICES':0,
        'OUTPUT':'memory:'})
        #Extrair o vertice -1 da camada quebrada a parti dos dissolvidos
        verti_1_sem=processing.run("native:extractspecificvertices",{
        'INPUT':sem_nome['OUTPUT'],
        'VERTICES':-1,
        'OUTPUT':'memory:'})
        
        mescla_sem=processing.run("native:mergevectorlayers",{
        'LAYERS':[verti_0_sem['OUTPUT'],verti_1_sem['OUTPUT']],
        'OUTPUT':'memory:'})
            
        
        #Achar os vertices que sao nascentes, extrair por localizaca (desunidos),  pela os mescla depois e se tem sobreposicao quer dizer que nao é nascente
        nasc_sem1=processing.run("native:extractbylocation",
        {'INPUT':mescla_sem['OUTPUT'],
        'INTERSECT':remov['OUTPUT'],
        'PREDICATE':[0],
        'OUTPUT':'memory:'})
        #QgsProject.instance().addMapLayer(nasc_sem1['OUTPUT'])
        
                       
        
        #output = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
        
        local=processing.run("native:extractbyexpression",
        {'INPUT': nasc_sem1['OUTPUT'],
        'EXPRESSION':f'"{a}" is null',
        'OUTPUT':'memory:'})
        
        nasc_sem_Final=processing.run("native:deleteduplicategeometries", {'INPUT':local['OUTPUT'],
        'OUTPUT':'memory:'})
            
        ExtrairPorExpresso1=processing.run('native:extractbyexpression',{
            'EXPRESSION': '"nome" is not null',
            'INPUT': parameters['INPUT'],
            'FAIL_OUTPUT': 'memory:',
            'OUTPUT': 'memory:'})
        
        #outputs['ExtrairPorExpresso1'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)    
        
        ExtrairVrticesEspecficos1SemNome=processing.run('native:extractspecificvertices',{
            'INPUT': ExtrairPorExpresso1['FAIL_OUTPUT'],
            'VERTICES': '-1',
            'OUTPUT': 'memory:'})
        
        #outputs['ExtrairVrticesEspecficos1SemNome'] = processing.run('native:extractspecificvertices', alg_params, context=context, feedback=feedback, is_child_algorithm=True)


        # Extrair vértices específicos_sem_nome_0
        ExtrairVrticesEspecficos_sem_nome_0=processing.run('native:extractspecificvertices',{
            'INPUT': ExtrairPorExpresso1['FAIL_OUTPUT'],
            'VERTICES': '0',
            'OUTPUT':'memory:'})
        
        #outputs['ExtrairVrticesEspecficos_sem_nome_0'] = processing.run('native:extractspecificvertices', alg_params, context=context, feedback=feedback, is_child_algorithm=True)



        # Extrair vértices específicos_com_nome_-1
        ExtrairVrticesEspecficos_com_nome_1 =processing.run('native:extractspecificvertices',{
            'INPUT': ExtrairPorExpresso1['OUTPUT'],
            'VERTICES': '-1',
            'OUTPUT': 'memory:'})
        
        #outputs['ExtrairVrticesEspecficos_com_nome_1'] = processing.run('native:extractspecificvertices', alg_params, context=context, feedback=feedback, is_child_algorithm=True)


        # Extrair vértices específicos_com_nome_0
        ExtrairVrticesEspecficos_com_nome_0 =processing.run('native:extractspecificvertices', {
            'INPUT': ExtrairPorExpresso1['OUTPUT'],
            'VERTICES': '0',
            'OUTPUT': 'memory:'})
        
        #outputs['ExtrairVrticesEspecficos_com_nome_0'] = processing.run('native:extractspecificvertices', alg_params, context=context, feedback=feedback, is_child_algorithm=True)



        # Extrair por localização_Nascente
        ExtrairPorLocalizao_nascente=processing.run('native:extractbylocation', {
            'INPUT': ExtrairVrticesEspecficos_com_nome_0['OUTPUT'],
            'INTERSECT': ExtrairVrticesEspecficos_com_nome_1['OUTPUT'],
            'PREDICATE': [2],  
            'OUTPUT':'memory:'})
        
        #outputs['ExtrairPorLocalizao_nascente'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)



        # Interseção vert_-1_sem_nome_-1_com_nome
        InterseoVert_1_sem_nome_1_com_nome =processing.run('native:intersection', {
            'INPUT': ExtrairVrticesEspecficos1SemNome['OUTPUT'],
            'INPUT_FIELDS': [''],
            'OVERLAY': ExtrairVrticesEspecficos_com_nome_1['OUTPUT'],
            'OVERLAY_FIELDS': [''],
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT': 'memory:'})
        
        #outputs['InterseoVert_1_sem_nome_1_com_nome'] = processing.run('native:intersection', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        # Extrair por localização_1
        ExtrairPorLocalizao_1 =processing.run('native:extractbylocation', {
            'INPUT': ExtrairVrticesEspecficos_com_nome_1['OUTPUT'],
            'INTERSECT': ExtrairVrticesEspecficos_com_nome_0['OUTPUT'],
            'PREDICATE': [2],  
            'OUTPUT': 'memory:'})
        
        #outputs['ExtrairPorLocalizao_1'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)


        # Extrair por localização oi
        ExtrairPorLocalizaoOi =processing.run('native:extractbylocation', {
            'INPUT': ExtrairPorLocalizao_1['OUTPUT'],
            'INTERSECT':ExtrairPorLocalizao_nascente['OUTPUT'],
            'PREDICATE': [2],  # desunidos
            'OUTPUT': 'memory:'})
        
        #outputs['ExtrairPorLocalizaoOi'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)


        # Extrair por localizaçãover_-1_sem_nome_-1_com_nome_vs_0_com_nome
        ExtrairPorLocalizaover_1_sem_nome_1_com_nome_vs_0_com_nome =processing.run('native:extractbylocation', {
            'INPUT': InterseoVert_1_sem_nome_1_com_nome['OUTPUT'],
            'INTERSECT': ExtrairVrticesEspecficos_com_nome_0['OUTPUT'],
            'PREDICATE': [2],  # desunidos
            'OUTPUT': 'memory:'})
        

        # Extrair por localização06
        ExtrairPorLocalizao06 =processing.run('native:extractbylocation', {
            'INPUT':ExtrairPorLocalizaoOi['OUTPUT'],
            'INTERSECT': ExtrairVrticesEspecficos_com_nome_0['OUTPUT'],
            'PREDICATE': [2],  
            'OUTPUT': 'memory:'})
        
        #outputs['ExtrairPorLocalizao06'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)


        # Remover duplicatas pelo atributo-1-1+0
        RemoverDuplicatasPeloAtributo110=processing.run('native:removeduplicatesbyattribute', {
            'FIELDS': ['id'],
            'INPUT': ExtrairPorLocalizaover_1_sem_nome_1_com_nome_vs_0_com_nome['OUTPUT'],
            'DUPLICATES': 'memory:',
            'OUTPUT': 'memory:'})
        
        #outputs['RemoverDuplicatasPeloAtributo110'] = processing.run('native:removeduplicatesbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)



        # Extrair por localização_limpo_-1;-1
        ExtrairPorLocalizao_limpo_11 =processing.run('native:extractbylocation', {
            'INPUT': RemoverDuplicatasPeloAtributo110['OUTPUT'],
            'INTERSECT': RemoverDuplicatasPeloAtributo110['DUPLICATES'],
            'PREDICATE': [2],  # desunidos
            'OUTPUT':'memory:'})
        
        #outputs['ExtrairPorLocalizao_limpo_11'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)


        # Extrair por localização final
        ExtrairPorLocalizaoFinal =processing.run('native:extractbylocation', {
            'INPUT': ExtrairPorLocalizao06['OUTPUT'],
            'INTERSECT': ExtrairVrticesEspecficos_sem_nome_0['OUTPUT'],
            'PREDICATE': [0], 
            'OUTPUT': 'memory:'
        })
        #outputs['ExtrairPorLocalizaoFinal'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)



        # Remover duplicatas pelo atributo final2
        RemoverDuplicatasPeloAtributoFinal2=processing.run('native:removeduplicatesbyattribute', {
            'FIELDS': 'nome; vertex_pos',
            'INPUT': ExtrairPorLocalizaoFinal['OUTPUT'],
            'DUPLICATES':'memory:',
            'OUTPUT': 'memory:'
        })
        #outputs['RemoverDuplicatasPeloAtributoFinal2'] = processing.run('native:removeduplicatesbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)



        # Extrair por localização
        ExtrairPorLocalizao=processing.run('native:extractbylocation', {
            'INPUT': ExtrairPorLocalizaoFinal['OUTPUT'],
            'INTERSECT': RemoverDuplicatasPeloAtributoFinal2['DUPLICATES'],
            'PREDICATE': [2], 
            'OUTPUT': 'memory:'})
        #outputs['ExtrairPorLocalizao'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        # Amortecedor
        Amortecedor=processing.run('native:buffer', {
            'DISSOLVE': False,
            'DISTANCE': 1e-05,
            'END_CAP_STYLE': 0,  # Arredondado
            'INPUT': ExtrairPorLocalizaoFinal['OUTPUT'],
            'JOIN_STYLE': 0,  # Arredondado
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': 'memory:'
        })
        #outputs['Amortecedor'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        # Interseção 
        Interseo=processing.run('native:intersection', {
            'INPUT': ExtrairPorLocalizaoFinal['OUTPUT'],
            'INPUT_FIELDS': [''],
            'OVERLAY': Amortecedor['OUTPUT'],
            'OVERLAY_FIELDS': [''],
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT': 'memory:'
        })
        #outputs['Interseo'] = processing.run('native:intersection', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        # Contagem de pontos em polígono
        ContagemDePontosEmPolgono =processing.run('native:countpointsinpolygon', {
            'CLASSFIELD': '',
            'FIELD': 'NUMPOINTS',
            'POINTS': ExtrairPorLocalizaoFinal['OUTPUT'],
            'POLYGONS': Amortecedor['OUTPUT'],
            'WEIGHT': '',
            'OUTPUT': 'memory:'
        })
        #outputs['ContagemDePontosEmPolgono'] = processing.run('native:countpointsinpolygon', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        # 0Extrair por expressão 000000000000000000000000000000000000000000000000
        ExtrairPorExpresso000000000000000000000000000000000000000000000000 = processing.run('native:extractbyexpression',{
            'EXPRESSION': '"nome" !="nome_2"',
            'INPUT': Interseo['OUTPUT'],
            'OUTPUT': 'memory:'
        })
        #outputs['ExtrairPorExpresso000000000000000000000000000000000000000000000000'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        # Extrair por atributo_agora
        ExtrairPorAtributo_agora =processing.run('native:extractbyattribute', {
            'FIELD': 'NUMPOINTS',
            'INPUT': ContagemDePontosEmPolgono['OUTPUT'],
            'OPERATOR': 0,  # =
            'VALUE': '1',
            'OUTPUT': 'memory:'
        })
        #outputs['ExtrairPorAtributo_agora'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        # Extrair por localização_contagem
        ExtrairPorLocalizao_contagem = processing.run('native:extractbylocation',{
            'INPUT': ExtrairPorLocalizaoFinal['OUTPUT'],
            'INTERSECT': ExtrairPorAtributo_agora['OUTPUT'],
            'PREDICATE': [0], 
            'OUTPUT': 'memory:'})
        #outputs['ExtrairPorLocalizao_contagem'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)


        # Excluir geometrias duplicadas009
        ExcluirGeometriasDuplicadas009 =processing.run('native:deleteduplicategeometries', {
            'INPUT': ExtrairPorExpresso000000000000000000000000000000000000000000000000['OUTPUT'],
            'OUTPUT': 'memory:'
        })
        #outputs['ExcluirGeometriasDuplicadas009'] = processing.run('native:deleteduplicategeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)


        #MEsclar
        a01=processing.run("native:mergevectorlayers",{
        'LAYERS':[ExtrairPorLocalizao_contagem['OUTPUT'],ExcluirGeometriasDuplicadas009['OUTPUT']],
        'OUTPUT':'memory:'})
            
        #output = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
        fil_1=processing.run("native:mergevectorlayers",{
        'LAYERS':[a01['OUTPUT'],nasc_sem_Final['OUTPUT']],
        'OUTPUT':'memory:'})
        
        fil_2=processing.run('native:deleteduplicategeometries', {
            'INPUT': fil_1['OUTPUT'],
            'OUTPUT':'memory:'})
            
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context, fil_2['OUTPUT'].fields(), fil_2['OUTPUT'].wkbType(), fil_2['OUTPUT'].sourceCrs())

            
        for feature in fil_2['OUTPUT'].getFeatures():
            geom = feature.geometry()
            new_feature = QgsFeature()
            new_feature.setGeometry(geom)
            new_feature.setAttributes(feature.attributes())
            sink.addFeature(new_feature)            

        
        
        return {'OUTPUT':dest_id}    





    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Attribute Discontinuity Detector'

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
        return ContinuousNetworkAnalysisAlgorithm()
