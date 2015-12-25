import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds
import math
import random

nodeName='RippleDeformer'
nodeId = OpenMaya.MTypeId (0x1003fff)

class rippleDeformer (OpenMayaMPx.MPxDeformerNode):
	'''
	Commands ---> MPxCommand
	Node     ---> MPxNode
	Deformer ---> MPxDeformerNode
	'''
	amplitude = OpenMaya.MObject()
	displacement=OpenMaya.MObject()
	matrix = OpenMaya.MObject()

	def __init__(self):
		OpenMayaMPx.MPxDeformerNode.__init__(self)

	def deform (self, dataBlock,geoIterator, matrix, geometryIndex):
		input = OpenMayaMPx.cvar.MPxDeformerNode_input
		# attach a handle to input Array Attribute
		# prevent recomputation
		dataHandleInputArray = dataBlock.outputArrayValue(input)
		#jump to particular element
		dataHandleInputArray.jumpToElement (geometryIndex)
		#attach a handle to specific data block
		dataHandleInputElement = dataHandleInputArray.outputValue()
		#reach to the child
		inputGeom = OpenMayaMPx.cvar.MPxDeformerNode_inputGeom
		dataHandleInputGeom = dataHandleInputElement.child (inputGeom)
		inMesh = dataHandleInputGeom.asMesh()

		#envelope
		envolope = OpenMayaMPx.cvar.MPxDeformerNode_envelope
		dataHandleEnvelope = dataBlock.inputValue(envolope)
		envolopeValue = dataHandleEnvelope.asFloat()
		#amplitude
		dataHandleAmplitude = dataBlock.inputValue (rippleDeformer.amplitude)
		amplitudeValue = dataHandleAmplitude.asFloat()
		#displace
		dataHandleDisplace = dataBlock.inputValue (rippleDeformer.displacement)
		displaceValue = dataHandleDisplace.asFloat()
		#matrix
		dataHandleMatrix = dataBlock.inputValue (rippleDeformer.matrix)
		MatrixValue = dataHandleMatrix.asMatrix()
		#read translation from Matrix
		mTransMatrix = OpenMaya.MTransformationMatrix(MatrixValue)
		translationValue = mTransMatrix.getTranslation(OpenMaya.MSpace.kObject)
		
		#mEulerRot = OpenMaya.MVector()
		#mEulerRot = mTransMatrix.eulerRotation().asVector()

		mFloatVectorArray_Normal = OpenMaya.MFloatVectorArray()
		inMeshMfn = OpenMaya.MFnMesh (inMesh)
		inMeshMfn.getVertexNormals(False,mFloatVectorArray_Normal,OpenMaya.MSpace.kObject)
		#create colorSet
		inMeshMfn.createColorSetDataMesh('vertexColorSet')
		inMeshMfn.setIsColorClamped('vertexColorSet',True)
		mPointArray_meshVert = OpenMaya.MPointArray()
		mColorArray_meshVert = OpenMaya.MColorArray()
		mVertexArray_meshVert = OpenMaya.MIntArray()
		while (not geoIterator.isDone()):
			pointPosition = geoIterator.position()
			weight=self.weightValue(dataBlock,geometryIndex,geoIterator.index())
			#inMeshMfn.setVertexColor(pointColor, geoIterator.index(),None,OpenMaya.MFnMesh.kRGBA)
			pointPosition.x= pointPosition.x + math.sin (geoIterator.index() + displaceValue + translationValue[0] ) * amplitudeValue * envolopeValue * mFloatVectorArray_Normal[geoIterator.index()].x*weight
			pointPosition.y= pointPosition.y + math.sin (geoIterator.index() + displaceValue + translationValue[0] ) * amplitudeValue * envolopeValue * mFloatVectorArray_Normal[geoIterator.index()].y*weight
			pointPosition.z= pointPosition.z + math.sin (geoIterator.index() + displaceValue + translationValue[0] ) * amplitudeValue * envolopeValue * mFloatVectorArray_Normal[geoIterator.index()].z*weight
			mPointArray_meshVert.append(pointPosition)
			#paint vertex color
			Color_R = math.sin (geoIterator.index() + displaceValue) * amplitudeValue
			Color_G = math.cos (geoIterator.index()+ displaceValue) * amplitudeValue
			Color_B = math.sin (geoIterator.index()- displaceValue) * amplitudeValue
			pointColor=OpenMaya.MColor (Color_R, Color_G, Color_B, 1.0)
			mColorArray_meshVert.append(pointColor)
			mVertexArray_meshVert.append (geoIterator.index())
			geoIterator.next()

		#optimize performance
		geoIterator.setAllPositions(mPointArray_meshVert)
		inMeshMfn.setVertexColors(mColorArray_meshVert,mVertexArray_meshVert,None,OpenMaya.MFnMesh.kRGBA)
		#set current colorset
		#inMeshMfn.setCurrentColorSetDataMesh('vertexColorSet')
		if (not cmds.polyColorSet(ccs=True, q=True)=='vertexColorSet'):
			cmds.polyColorSet (ccs=True, cs='vertexColorSet')

	def accessoryNodeSetup (self, dagModifier):
		#create Accessory Object
		mObjLocator = dagModifier.createNode ('locator')
		#establish Connection
		mFnDependLocator = OpenMaya.MFnDependencyNode (mObjLocator)
		mFnDependLocator.setName('rippleHandle')
		mPlugWorld = mFnDependLocator.findPlug("worldMatrix")
		mobj_WorldAttr = mPlugWorld.attribute()
		try:
			status = dagModifier.connect(mObjLocator, mobj_WorldAttr, self.thisMObject(), rippleDeformer.matrix)
			print 'connect sucssefully'
		except:
			sys.stderr.write ('failed to build the connections!')


	def accessoryAttribute(self):
		return rippleDeformer.matrix


def deformerCreator():
	return OpenMayaMPx.asMPxPtr(rippleDeformer())


def nodeInitializer():
	'''
	create Attributes ---done
	attach Attributes --- done
	Design Circuitry ---done
	'''
	print 'initialize sucssefully!'
	#create attributes
	mFnAttr = OpenMaya.MFnNumericAttribute ()
	rippleDeformer.amplitude = mFnAttr.create ('amplitude', 'a', OpenMaya.MFnNumericData.kFloat,0.0)
	mFnAttr.setKeyable(True)
	mFnAttr.setMin (0.0)
	mFnAttr.setMax (1.0)

	rippleDeformer.displacement = mFnAttr.create ('displacement' , 'd', OpenMaya.MFnNumericData.kFloat,0.0)
	#default not keyable
	mFnAttr.setKeyable (True) 
	mFnAttr.setMin (-10.0)
	mFnAttr.setMax (10.0)
	#create Matrix Attribute
	MfnMatrixAttr = OpenMaya.MFnMatrixAttribute ()
	rippleDeformer.matrix = MfnMatrixAttr.create ('MatrixAttribute', 'matAttr')
	MfnMatrixAttr.setStorable (False)
	MfnMatrixAttr.setConnectable (True)

	#connect with Deformer Node
	rippleDeformer.addAttribute (rippleDeformer.matrix)
	#attach attributes
	rippleDeformer.addAttribute(rippleDeformer.amplitude)
	rippleDeformer.addAttribute(rippleDeformer.displacement)

	#SWIG - simplified wrapper interface generator
	outputGeom = OpenMayaMPx.cvar.MPxDeformerNode_outputGeom
	rippleDeformer.attributeAffects(rippleDeformer.amplitude, outputGeom)
	rippleDeformer.attributeAffects (rippleDeformer.displacement, outputGeom)
	rippleDeformer.attributeAffects (rippleDeformer.matrix, outputGeom)

def initializePlugin(mObject):
    mplugin = OpenMayaMPx.MFnPlugin(mObject, 'Ryan Wang', '1.0')
    try:
        mplugin.registerNode(nodeName, nodeId, deformerCreator, nodeInitializer, OpenMayaMPx.MPxNode.kDeformerNode) 
    except:
        sys.stderr.write('Failed to register Node: %s/n'  %nodeName)
        raise


def uninitializePlugin(mObject):
    mplugin = OpenMayaMPx.MFnPlugin(mObject)
    try:
        mplugin.deregisterCommand(nodeName)
    except:
        sys.stderr.write('Failed to deregister Node: %s/n'  %nodeName)
        raise
