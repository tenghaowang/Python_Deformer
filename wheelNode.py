import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import math

nodeName='wheelNode'
nodeId = OpenMaya.MTypeId (0x1000fff)


class wheelNode(OpenMayaMPx.MPxNode):
	#define attribute handle
	inRadius=OpenMaya.MObject()
	inTranslate=OpenMaya.MObject()
	outRotate=OpenMaya.MObject()

	def __init__(self):
		OpenMayaMPx.MPxNode.__init__(self)

	def compute(self,plug,dataBlock):
		'''
		rotate = translate/(2*3.14*radius) * -360
		'''
		if plug == wheelNode.outRotate:
			dataHandleRadius = dataBlock.inputValue(wheelNode.inRadius)
			dataHandleTranslate=dataBlock.inputValue(wheelNode.inTranslate)
			
			inRadiusVal=dataHandleRadius.asFloat()
			inTranslateVal=dataHandleTranslate.asFloat()

			outRotateVal = float (inTranslateVal) / float (2 * 3.14 * inRadiusVal) * -360

			dataHandleRotate = dataBlock.outputValue(wheelNode.outRotate)

			dataHandleRotate. setFloat(outRotateVal)

			dataBlock.setClean(plug)

		else:

			return "UnKnown"




#create a pointer to our Node class
def nodeCreator():
	return OpenMayaMPx.asMPxPtr(wheelNode())


def nodeInitializer():
	#creating functionset for numeric attributes
	mFnAttr = OpenMaya.MFnNumericAttribute()

	#create attributes

	wheelNode.inTranslate = mFnAttr.create('translate', 't', OpenMaya.MFnNumericData.kFloat,0.0)
	mFnAttr.setReadable(True)
	mFnAttr.setWritable(True)
	mFnAttr.setStorable(True)
	mFnAttr.setKeyable(True)

	wheelNode.inRadius=mFnAttr.create('radius', 'r', OpenMaya.MFnNumericData.kFloat,0.0)
	mFnAttr.setReadable(True)
	mFnAttr.setWritable(True)
	mFnAttr.setStorable(True)
	mFnAttr.setKeyable(True)

	#default data, do not need to define the default value
	wheelNode.outRotate=mFnAttr.create('rotate','rot',OpenMaya.MFnNumericData.kFloat)
	mFnAttr.setReadable(True)
	mFnAttr.setWritable(False)
	mFnAttr.setStorable(False)
	mFnAttr.setKeyable(False)

	#attaching attribute to the node
	wheelNode.addAttribute(wheelNode.inRadius)
	wheelNode.addAttribute(wheelNode.inTranslate)
	wheelNode.addAttribute(wheelNode.outRotate)


	# Design circuitry -- set dirty?
	wheelNode.attributeAffects(wheelNode.inRadius, wheelNode.outRotate)
	wheelNode.attributeAffects(wheelNode.inTranslate,wheelNode.outRotate)


def initializePlugin(mObject):
    mplugin = OpenMayaMPx.MFnPlugin(mObject)
    try:
        mplugin.registerNode(nodeName, nodeId, nodeCreator, nodeInitializer)
    except:
        sys.stderr.write('Failed to register Node: %s/n'  %commandName)


def uninitializePlugin(mObject):
    mplugin = OpenMayaMPx.MFnPlugin(mObject)
    try:
        mplugin.deregisterCommand(nodeName)
    except:
        sys.stderr.write('Failed to deregister Node: %s/n'  %commandName)


