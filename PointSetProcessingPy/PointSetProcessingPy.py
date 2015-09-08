import os
import unittest
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *

import logging

############################################################ PointSetProcessingPy 
class PointSetProcessingPy(ScriptedLoadableModule):
  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "PointSetProcessing" 
    self.parent.categories = ["Filtering"]
    self.parent.dependencies = []
    self.parent.contributors = ["Mikael Brudfors (brudfors@gmail.com)"] 
    self.parent.helpText = """
    This module reconstructs a surface from unorganized points. For more information see: https://github.com/brudfors/SlicerPointSetProcessing
    """
    self.parent.acknowledgementText = """
    Supported by projects IPT-2012-0401-300000, TEC2013-48251-C2-1-R, DTS14/00192 and FEDER funds. 
""" # replace with organization, grant and thanks.

############################################################ PointSetProcessingPyWidget 
class PointSetProcessingPyWidget(ScriptedLoadableModuleWidget):
  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)
    pointSetProcessingCollapsibleButton = ctk.ctkCollapsibleButton()
    pointSetProcessingCollapsibleButton.text = "Surface Reconstruction from Unorganized Points"
    self.layout.addWidget(pointSetProcessingCollapsibleButton)
    pointSetProcessingFormLayout = qt.QFormLayout(pointSetProcessingCollapsibleButton)

    # Input
    self.inputSelector = slicer.qMRMLNodeComboBox()
    self.inputSelector.nodeTypes = ( ("vtkMRMLModelNode"), "" )
    self.inputSelector.selectNodeUponCreation = True
    self.inputSelector.addEnabled = False
    self.inputSelector.removeEnabled = False
    self.inputSelector.noneEnabled = False
    self.inputSelector.showHidden = False
    self.inputSelector.showChildNodeTypes = False
    self.inputSelector.setMRMLScene( slicer.mrmlScene )
    self.inputSelector.setToolTip( "Pick the input to the algorithm." )
    pointSetProcessingFormLayout.addRow("Input Model: ", self.inputSelector)

    # Runtime
    self.runtimeGroupBox = ctk.ctkCollapsibleGroupBox()
    self.runtimeGroupBox.setTitle("Runtime")
    runtimeFormLayout = qt.QFormLayout(self.runtimeGroupBox)
    pointSetProcessingFormLayout.addRow(self.runtimeGroupBox)
    
    self.runtimeLabel = qt.QLabel()
    self.runtimeLabel.setText("... s.")
    self.runtimeLabel.setWordWrap(True)
    self.runtimeLabel.setStyleSheet("QLabel { background-color : black; \
                                           color : #66FF00; \
                                           height : 60px; \
                                           border-style: outset; \
                                           border-width: 5px; \
                                           border-radius: 10px; \
                                           font: bold 14px; \
                                           padding: 0px;\
                                           font-family : SimSun; \
                                           qproperty-alignment: AlignCenter}")
    runtimeFormLayout.addRow(self.runtimeLabel)
    
    # Compute Normals
    self.normalsGroupBox = ctk.ctkCollapsibleGroupBox()
    self.normalsGroupBox.setTitle("Compute Normals")
    normalsFormLayout = qt.QFormLayout(self.normalsGroupBox)
    pointSetProcessingFormLayout.addRow(self.normalsGroupBox)
    
    self.parametersNormalsOutputGroupBox = qt.QGroupBox()
    self.parametersNormalsOutputGroupBox.setTitle("Parameters")
    parametersNormalsOutputFormLayout = qt.QFormLayout(self.parametersNormalsOutputGroupBox)
    normalsFormLayout.addRow(self.parametersNormalsOutputGroupBox)

    self.modeTypeComboBox = qt.QComboBox()
    self.modeTypeComboBox.addItem('Fixed')  
    self.modeTypeComboBox.addItem('Radius')
    self.modeTypeComboBox.setCurrentIndex(1)
    self.modeTypeComboBox.setToolTip('')    
    parametersNormalsOutputFormLayout.addRow('Mode Type: ', self.modeTypeComboBox)
    
    self.numberOfNeighborsSlider = ctk.ctkSliderWidget()
    self.numberOfNeighborsSlider.setDecimals(0)
    self.numberOfNeighborsSlider.singleStep = 1
    self.numberOfNeighborsSlider.minimum = 1
    self.numberOfNeighborsSlider.maximum = 20
    self.numberOfNeighborsSlider.value = 4
    self.numberOfNeighborsSlider.setToolTip('')
    self.numberOfNeighborsSlider.enabled = False
    parametersNormalsOutputFormLayout.addRow('Fixed Neighbors: ', self.numberOfNeighborsSlider)
    
    self.radiusSlider = ctk.ctkSliderWidget()
    self.radiusSlider.setDecimals(2)
    self.radiusSlider.singleStep = 0.01
    self.radiusSlider.minimum = 1
    self.radiusSlider.maximum = 10
    self.radiusSlider.value = 1.0
    self.radiusSlider.setToolTip('')
    parametersNormalsOutputFormLayout.addRow('Radius: ', self.radiusSlider)
    
    self.graphTypeComboBox = qt.QComboBox()
    self.graphTypeComboBox.addItem('Riemann')  
    self.graphTypeComboBox.addItem('KNN')
    self.graphTypeComboBox.setCurrentIndex(1)
    self.graphTypeComboBox.setToolTip('')    
    parametersNormalsOutputFormLayout.addRow('Graph Type: ', self.graphTypeComboBox)
    
    self.knnSlider = ctk.ctkSliderWidget()
    self.knnSlider.setDecimals(0)
    self.knnSlider.singleStep = 1
    self.knnSlider.minimum = 1
    self.knnSlider.maximum = 20
    self.knnSlider.value = 5
    self.knnSlider.setToolTip('')
    parametersNormalsOutputFormLayout.addRow('K-Nearest Neighbors: ', self.knnSlider)
           
    self.computeNormalsButton = qt.QPushButton("Apply")
    self.computeNormalsButton.enabled = False
    self.computeNormalsButton.checkable = True
    normalsFormLayout.addRow(self.computeNormalsButton)
    
    self.normalsVisibleCheckBox = qt.QCheckBox('Normals Visible: ')
    self.normalsVisibleCheckBox.checked = True
    self.normalsVisibleCheckBox.enabled = True
    normalsFormLayout.addRow(self.normalsVisibleCheckBox)
    
    # Compute Surface
    self.surfaceGroupBox = ctk.ctkCollapsibleGroupBox()
    self.surfaceGroupBox.setTitle("Compute Surface")
    surfaceFormLayout = qt.QFormLayout(self.surfaceGroupBox)
    pointSetProcessingFormLayout.addRow(self.surfaceGroupBox)
    
    self.parametersPoissonOutputGroupBox = qt.QGroupBox()
    self.parametersPoissonOutputGroupBox.setTitle("Parameters")
    parametersPoissonOutputFormLayout = qt.QFormLayout(self.parametersPoissonOutputGroupBox)
    surfaceFormLayout.addRow(self.parametersPoissonOutputGroupBox)
    
    self.depthSlider = ctk.ctkSliderWidget()
    self.depthSlider.setDecimals(0)
    self.depthSlider.singleStep = 1
    self.depthSlider.minimum = 1
    self.depthSlider.maximum = 20
    self.depthSlider.value = 8
    self.depthSlider.setToolTip('This integer controls the reconstruction depth; the maximum depth of the tree that will be used for surface reconstruction. Running at depth d corresponds to solving on a voxel grid whose resolution is no larger than 2^d x 2^d x 2^d. Note that since the reconstructor adapts the octree to the sampling density, the specified reconstruction depth is only an upper bound.')
    parametersPoissonOutputFormLayout.addRow('Depth: ', self.depthSlider)
    
    self.scaleSlider = ctk.ctkSliderWidget()
    self.scaleSlider.setDecimals(2)
    self.scaleSlider.singleStep = 0.01
    self.scaleSlider.minimum = 1
    self.scaleSlider.maximum = 10
    self.scaleSlider.value = 1.25
    self.scaleSlider.setToolTip('This floating point value specifies the ratio between the diameter of the cube used for reconstruction and the diameter of the samples bounding cube.')
    parametersPoissonOutputFormLayout.addRow('Scale: ', self.scaleSlider)    
    
    self.solverDivideSlider = ctk.ctkSliderWidget()
    self.solverDivideSlider.setDecimals(0)
    self.solverDivideSlider.singleStep = 1
    self.solverDivideSlider.minimum = 1
    self.solverDivideSlider.maximum = 20
    self.solverDivideSlider.value = 8
    self.solverDivideSlider.setToolTip('Solver subdivision depth; This integer argument specifies the depth at which a block Gauss-Seidel solver is used to solve the Laplacian equation. Using this parameter helps reduce the memory overhead at the cost of a small increase in reconstruction time. (In practice, we have found that for reconstructions of depth 9 or higher a subdivide depth of 7 or 8 can greatly reduce the memory usage.)')
    parametersPoissonOutputFormLayout.addRow('Solver Divide: ', self.solverDivideSlider)   
    
    self.isoDivideSlider = ctk.ctkSliderWidget()
    self.isoDivideSlider.setDecimals(0)
    self.isoDivideSlider.singleStep = 1
    self.isoDivideSlider.minimum = 1
    self.isoDivideSlider.maximum = 20
    self.isoDivideSlider.value = 8
    self.isoDivideSlider.setToolTip('Iso-surface extraction subdivision depth; This integer argument specifies the depth at which a block isosurface extractor should be used to extract the iso-surface. Using this parameter helps reduce the memory overhead at the cost of a small increase in extraction time. (In practice, we have found that for reconstructions of depth 9 or higher a subdivide depth of 7 or 8 can greatly reduce the memory usage.)')
    parametersPoissonOutputFormLayout.addRow('Iso Divide: ', self.isoDivideSlider)   
 
    self.samplesPerNodeSlider = ctk.ctkSliderWidget()
    self.samplesPerNodeSlider.setDecimals(2)
    self.samplesPerNodeSlider.singleStep = 0.1
    self.samplesPerNodeSlider.minimum = 1
    self.samplesPerNodeSlider.maximum = 30
    self.samplesPerNodeSlider.value = 1.0
    self.samplesPerNodeSlider.setToolTip('Minimum number of samples; This floating point value specifies the minimum number of sample points that should fall within an octree node as the octree construction is adapted to sampling density. For noise-free samples, small values in the range [1.0 - 5.0] can be used. For more noisy samples, larger values in the range [15.0 - 20.0] may be needed to provide a smoother, noise-reduced, reconstruction.')
    parametersPoissonOutputFormLayout.addRow('Samples per Node: ', self.samplesPerNodeSlider)   
    
    self.confidenceComboBox = qt.QComboBox()
    self.confidenceComboBox.addItem('False')
    self.confidenceComboBox.addItem('True')  
    self.confidenceComboBox.setToolTip('Enabling tells the reconstructor to use the size of the normals as confidence information. When the flag is not enabled, all normals are normalized to have unit-length prior to reconstruction.')    
    parametersPoissonOutputFormLayout.addRow('Confidence: ', self.confidenceComboBox)
   
    self.verboseComboBox = qt.QComboBox()
    self.verboseComboBox.addItem('False')
    self.verboseComboBox.addItem('True')  
    self.verboseComboBox.setToolTip('Enabling this flag provides a more verbose description of the running times and memory usages of individual components of the surface reconstructor.')    
    parametersPoissonOutputFormLayout.addRow('Verbose: ', self.verboseComboBox)
    
    self.computeSurfaceButton = qt.QPushButton("Apply")
    self.computeSurfaceButton.enabled = False
    self.computeSurfaceButton.checkable = True
    surfaceFormLayout.addRow(self.computeSurfaceButton)    
        
    self.surfaceVisibleCheckBox = qt.QCheckBox('Surface Visible: ')
    self.surfaceVisibleCheckBox.checked = True
    self.surfaceVisibleCheckBox.enabled = True
    normalsFormLayout.addRow(self.surfaceVisibleCheckBox)
    
    # connections
    self.computeNormalsButton.connect('clicked(bool)', self.onComputeNormals)
    self.computeSurfaceButton.connect('clicked(bool)', self.onComputeSurface)
    self.inputSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.onSelect)
    self.graphTypeComboBox.connect('currentIndexChanged(const QString &)', self.onGraphTypeChanged)
    self.modeTypeComboBox.connect('currentIndexChanged(const QString &)', self.onModeTypeChanged)
    self.surfaceVisibleCheckBox.connect('stateChanged(int)', self.onSurfaceVisible)
    self.normalsVisibleCheckBox.connect('stateChanged(int)', self.onNormalsVisible)
            
    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh 
    self.onSelect()
        
    lm=slicer.app.layoutManager()
    lm.setLayout(4) # One 3D-view    

  def onSurfaceVisible(self, checked):
    logic = PointSetProcessingPyLogic()
    logic.surfaceVisible(checked)
 
  def onNormalsVisible(self, checked):
    logic = PointSetProcessingPyLogic()
    logic.normalsVisible(checked)
    
  def onGraphTypeChanged(self, type):
    if type == 'KNN':
      self.knnSlider.enabled = True
    elif type == 'Riemann':
      self.knnSlider.enabled = False

  def onModeTypeChanged(self, type):
    if type == 'Radius':
      self.radiusSlider.enabled = True
      self.numberOfNeighborsSlider.enabled = False
    elif type == 'Fixed':
      self.radiusSlider.enabled = False
      self.numberOfNeighborsSlider.enabled = True
      
  def onSelect(self):
    self.computeNormalsButton.enabled = self.inputSelector.currentNode()
    self.computeSurfaceButton.enabled = self.inputSelector.currentNode()

  def onComputeNormals(self):
    if self.computeNormalsButton.checked:
      logic = PointSetProcessingPyLogic()
      logic.computeNormals(self.inputSelector.currentNode(), self.modeTypeComboBox.currentIndex, self.numberOfNeighborsSlider.value, self.radiusSlider.value, self.knnSlider.value, self.graphTypeComboBox.currentIndex, self.runtimeLabel)
      self.computeNormalsButton.checked = False   
      
  def onComputeSurface(self):
    if self.computeSurfaceButton.checked:
      logic = PointSetProcessingPyLogic()
      logic.computeSurface(self.inputSelector.currentNode(), self.depthSlider.value, self.scaleSlider.value, self.solverDivideSlider.value, self.isoDivideSlider.value, self.samplesPerNodeSlider.value, self.confidenceComboBox.currentIndex, self.verboseComboBox.currentIndex, self.runtimeLabel)
      self.computeSurfaceButton.checked = False         

############################################################ PointSetProcessingPyLogic 
class PointSetProcessingPyLogic(ScriptedLoadableModuleLogic):

  def computeNormals(self, inputModelNode, mode = 1, numberOfNeighbors = 4, radius = 1.0, kNearestNeighbors = 5, graphType = 1, runtimeLabel = None):
    outputModelNode = slicer.util.getNode('ComputedNormals')
    if not outputModelNode:
      outputModelNode = self.createOutputModelNode('ComputedNormals', [0, 1, 0])  
    runtime = slicer.modules.pointsetprocessingcpp.logic().ComputeNormals(inputModelNode, outputModelNode, int(mode), int(numberOfNeighbors), float(radius), int(kNearestNeighbors), int(graphType), True)
    if runtimeLabel:
      runtimeLabel.setText('Normals computed in  %.2f' % runtime + ' s.')
    return True
   
  def computeSurface(self, inputModelNode, depth = 8, scale = 1.25, solverDivide = 8, isoDivide = 8, samplesPerNode = 1.0, confidence = 0, verbose = 0, runtimeLabel = None):
    outputModelNode = slicer.util.getNode('ComputedSurface', [1, 0, 0])
    if not outputModelNode:
      outputModelNode = self.createOutputModelNode('ComputedSurface')
    runtime = slicer.modules.pointsetprocessingcpp.logic().ComputeSurface(inputModelNode, outputModelNode, int(depth), float(scale), int(solverDivide), int(isoDivide), float(samplesPerNode), int(confidence), int(verbose))
    if runtimeLabel:
      runtimeLabel.setText('Surface computed in %.2f' % runtime + ' s.')
    return True

  def surfaceVisible(self, visible):
    modelNode = slicer.util.getNode('ComputedSurface')
    if modelNode:  
      modelNode.GetModelDisplayNode().SetVisibility(visible)
 
  def normalsVisible(self, visible):
    modelNode = slicer.util.getNode('ComputedNormals')
    if modelNode:  
      modelNode.GetModelDisplayNode().SetVisibility(visible)
    
  def createOutputModelNode(self, name, color):
    scene = slicer.mrmlScene
    outputModelNode = slicer.vtkMRMLModelNode()
    outputModelNode.SetScene(scene)
    outputModelNode.SetName(name)
    modelDisplay = slicer.vtkMRMLModelDisplayNode()
    modelDisplay.SetColor(color)
    modelDisplay.SetScene(scene)
    scene.AddNode(modelDisplay)
    outputModelNode.SetAndObserveDisplayNodeID(modelDisplay.GetID())
    scene.AddNode(outputModelNode)  
    return outputModelNode
    
############################################################ PointSetProcessingPyTest    
class PointSetProcessingPyTest(ScriptedLoadableModuleTest):

  def setUp(self):
    slicer.mrmlScene.Clear(0)
    layoutManager = slicer.app.layoutManager()
    layoutManager.setLayout(4)
    
  def runTest(self):
    self.setUp()
    self.test_Module()

  def test_Module(self):
    self.delayDisplay("Testing module")
    pointSetProcessingPyModuleDirectoryPath = slicer.modules.pointsetprocessingpy.path.replace("PointSetProcessingPy.py", "")
    slicer.util.loadModel(pointSetProcessingPyModuleDirectoryPath + '../Data/SpherePoints.vtp', 'SpherePoints')
    inputModelNode = slicer.util.getNode('SpherePoints')
    logic = PointSetProcessingPyLogic()
    self.assertTrue(logic.computeNormals(inputModelNode))        
    self.assertTrue(logic.computeSurface(inputModelNode))        
    self.delayDisplay('Testing module passed!')    
