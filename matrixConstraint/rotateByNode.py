import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

nodeName = 'RotateByNode'
nodeId = OpenMaya.MTypeId(0x1000fff)


class RotateByNode(OpenMayaMPx.MPxNode):
    # define attribute handle
    inRotate = OpenMaya.MObject()
    inMatrix = OpenMaya.MObject()
    outMatrix = OpenMaya.MObject()

    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    def compute(self, plug, dataBlock):

        if plug == RotateByNode.outMatrix:

            dataHandleJointOrient = dataBlock.inputValue(RotateByNode.inRotate)
            # input rotate is defined in radians
            inputRotate = dataHandleJointOrient.asDouble3()

            dataHandleInMatrix = dataBlock.inputValue(RotateByNode.inMatrix)
            inMatrix = dataHandleInMatrix.asMatrix()
            matrixList = [[OpenMaya.MScriptUtil.getDoubleArrayItem(inMatrix[row], col) for col in range(4)] for row in range(4)]
            print 'in Matrix'
            print matrixList
            # This is our rotation order
            rotOrder = OpenMaya.MEulerRotation.kXYZ

            # Create the MEulerRotation
            inputEuler = OpenMaya.MEulerRotation(inputRotate[0], inputRotate[1], inputRotate[2], rotOrder)

            # Get the quaternion equivalent
            inputQuaternion = inputEuler.asQuaternion()
            inputQuaternionInvert = inputQuaternion.inverse()
            # inverse the quaternion
            worldTransformMatrix = OpenMaya.MTransformationMatrix(inMatrix)

            # get out matrix
            outTransformMatrix = worldTransformMatrix.rotateBy(inputQuaternionInvert, OpenMaya.MSpace.kTransform)
            outMatrix = outTransformMatrix.asMatrix()
            matrixList = [[OpenMaya.MScriptUtil.getDoubleArrayItem(outMatrix[row], col) for col in range(4)] for row in range(4)]
            print 'out Matrix:'
            print matrixList
            dataHandleOutMatrix = dataBlock.outputValue(RotateByNode.outMatrix)

            dataHandleOutMatrix.setMMatrix(outMatrix)

            dataBlock.setClean(plug)

        else:

            return "UnKnown"


def nodeCreator():
    # create a pointer to our Node class
    return OpenMayaMPx.asMPxPtr(RotateByNode())


def nodeInitializer():
    # creating functionset for numeric attributes
    mFnAttr = OpenMaya.MFnNumericAttribute()
    uFnAttr = OpenMaya.MFnUnitAttribute()
    xFnAttr = OpenMaya.MFnMatrixAttribute()
    # # create attributes

    inRotateX = uFnAttr.create('inRotateX', 'irx', OpenMaya.MFnUnitAttribute.kAngle, 0.0)
    uFnAttr.setReadable(True)
    uFnAttr.setWritable(True)
    uFnAttr.setStorable(True)
    uFnAttr.setKeyable(True)

    inRotateY = uFnAttr.create('inRotateY', 'iry', OpenMaya.MFnUnitAttribute.kAngle, 0.0)
    uFnAttr.setReadable(True)
    uFnAttr.setWritable(True)
    uFnAttr.setStorable(True)
    uFnAttr.setKeyable(True)

    inRotateZ = uFnAttr.create('inRotateZ', 'irz', OpenMaya.MFnUnitAttribute.kAngle, 0.0)
    uFnAttr.setReadable(True)
    uFnAttr.setWritable(True)
    uFnAttr.setStorable(True)
    uFnAttr.setKeyable(True)

    RotateByNode.inRotate = mFnAttr.create('inRotate', 'ir', inRotateX, inRotateY, inRotateZ)

    RotateByNode.inMatrix = xFnAttr.create('inMatrix', 'im', OpenMaya.MFnMatrixAttribute.kDouble)
    xFnAttr.setReadable(True)
    xFnAttr.setWritable(True)
    xFnAttr.setKeyable(True)
    xFnAttr.setStorable(True)

    RotateByNode.outMatrix = xFnAttr.create('outMatrix', 'om', OpenMaya.MFnMatrixAttribute.kDouble)
    xFnAttr.setReadable(True)
    xFnAttr.setWritable(False)
    xFnAttr.setStorable(True)

    # attaching attribute to the node
    RotateByNode.addAttribute(RotateByNode.inRotate)
    RotateByNode.addAttribute(RotateByNode.inMatrix)

    RotateByNode.addAttribute(RotateByNode.outMatrix)
    # RotateByNode.addAttribute(RotateByNode.outTranslate)

    # Design circuitry -- set dirty?
    RotateByNode.attributeAffects(RotateByNode.inRotate, RotateByNode.outMatrix)
    RotateByNode.attributeAffects(RotateByNode.inMatrix, RotateByNode.outMatrix)


def initializePlugin(mObject):
    mplugin = OpenMayaMPx.MFnPlugin(mObject)
    try:
        mplugin.registerNode(nodeName, nodeId, nodeCreator, nodeInitializer)
    except:
        sys.stderr.write('Failed to deregister node' + nodeName)


def uninitializePlugin(mObject):
    mplugin = OpenMayaMPx.MFnPlugin(mObject)
    try:
        mplugin.deregisterCommand(nodeName)
    except:
        sys.stderr.write('Failed to deregister node' + nodeName)