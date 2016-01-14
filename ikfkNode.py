import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaRender as OpenMayaRender
import maya.OpenMayaMPx as OpenMayaMPx

nodeName = 'IkFkNode'
nodeId = OpenMaya.MTypeId(0x1011fff)

class CVGNode(OpenMayaMPx.MPxNode):

	idCallback = []
	joint1 = OpenMaya.MObject()
	joint2 = OpenMaya.MObject()
	joint3 = OpenMaya.MObject()
	activeIKHandle = OpenMaya.MObject()
	activeIKEffector = OpenMaya.MObject()
	poleVectorController = OpenMaya.MObject()
	poleVector = OpenMaya.MObject()



	#constructor
	def __init__(self):
		OpenMayaMPx.MPxNode.__init__(self)
		#event Callback
		self.idCallback.append(OpenMaya.MEventMessage.addEventCallback('SelectionChanged', self.callbackFunc))

		#DGCallback
		self.idCallback.append(OpenMaya.MDGMessage.addNodeRemovedCallback(self.remove, 'dependNode'))

	def callbackFunc(self, *args):
		print 'callback'
		mSel = OpenMaya.MSelectionList()
		OpenMaya.MGlobal.getActiveSelectionList(mSel)
		mode = 'fk'
		MItselectionList = OpenMaya.MItSelectionList(mSel, OpenMaya.MFn.kDagNode)
		while (not MItselectionList.isDone()):
			mObj = OpenMaya.MObject()
			MItselectionList.getDependNode(mObj)
			#although ik effector is not selectable
			#if ik effector is selected
			#==============================================#
			#if mObj.apiType() == OpenMaya.MFn.kIkEffector:
				#activeIKEffector = mObj
				#mode = 'ik'
				#break
			#==============================================#
			#if ik handle is selected
			if mObj.apiType() == OpenMaya.MFn.kIkHandle:
				self.activeIKHandle = mObj
				mode ='ik'
				break
			#if pole vector controller is selected
			if mObj.apiType() ==OpenMaya.MFn.kTransform:
				mdependNode = OpenMaya.MFnDependencyNode(mObj)
				mPlugArray = OpenMaya.MPlugArray()
				mdependNode.getConnections(mPlugArray)
				for i  in range(mPlugArray.length()):
					mPlug = mPlugArray[i]
					mPlugArray1 = OpenMaya.MPlugArray()
					mPlug.connectedTo(mPlugArray1,False,True)
					#for i in range(mPlugArray1.length()):
					mPlug = mPlugArray1[0]
					if mPlug.node().apiType() == OpenMaya.MFn.kPoleVectorConstraint:
						self.poleVector = mPlug.node()
						self.poleVectorController = mObj
						#print 'find kPoleVectorConstraint'
						mode = 'ik'
						break
			MItselectionList.next()

		#if poleVector controller is found:
		if self.poleVectorController.apiType() == OpenMaya.MFn.kTransform and self.poleVector.apiType() == OpenMaya.MFn.kPoleVectorConstraint:
			poleVectorDependNode = OpenMaya.MFnDependencyNode(self.poleVector)
			mPlugArray = OpenMaya.MPlugArray()
			poleVectorDependNode.getConnections(mPlugArray)
			for i in range(mPlugArray.length()):
				mPlug = mPlugArray[i]
				mPlug.connectedTo(mPlugArray,True,False)
				if mPlugArray.length()>0:
					if mPlugArray[0].node().apiType() == OpenMaya.MFn.kIkHandle:
						self.activeIKHandle = mPlugArray[0].node()



		#if IKHandle is found:
		if self.activeIKHandle.apiType() == OpenMaya.MFn.kIkHandle:
			#find IKEffector based on IKHandle
			IKHandleDependNode = OpenMaya.MFnDependencyNode(self.activeIKHandle)
			connectedPlug = OpenMaya.MPlugArray()
			IKHandleDependNode.getConnections(connectedPlug)
			for i in range(connectedPlug.length()):
				mPlug = connectedPlug[i]
				otherPlug = OpenMaya.MPlugArray()
				mPlug.connectedTo(otherPlug,True,True)
				#find effector
				if otherPlug[0].node().apiType() == OpenMaya.MFn.kIkEffector:
					self.activeIKEffector = otherPlug[0].node()
				#find poleVectorConstraint
				if otherPlug[0].node().apiType() == OpenMaya.MFn.kPoleVectorConstraint:
					self.poleVector = otherPlug[0].node()
				#find the start joint ---> joint1
				if otherPlug[0].node().apiType() == OpenMaya.MFn.kJoint:
					self.joint1 = otherPlug[0].node()

			#if poleVectorConstaint is found:
			if self.poleVector.apiType() ==OpenMaya.MFn.kPoleVectorConstraint:
				poleVectorDependNode = OpenMaya.MFnDependencyNode(self.poleVector)
				poleVectorPlugs = OpenMaya.MPlugArray()
				poleVectorDependNode.getConnections(poleVectorPlugs)
				for i in range(poleVectorPlugs.length()):
					mPlug = poleVectorPlugs[i]
					otherPlug = OpenMaya.MPlugArray()
					mPlug.connectedTo(otherPlug,True,False)
					if otherPlug.length()>0:
						if otherPlug[0].node().apiType() == OpenMaya.MFn.kTransform:
							self.poleVectorController = otherPlug[0].node()
							break


			#if kIkEffector is found:
			if self.activeIKEffector.apiType() == OpenMaya.MFn.kIkEffector:
				#use to find joint 3
				#based on joint3 and joint 1 ----> joint 2
				effectorNode = OpenMaya.MFnDependencyNode(self.activeIKEffector)
				effectorPlug = OpenMaya.MPlugArray()
				effectorNode.getConnections(effectorPlug)
				for i in range(effectorPlug.length()):
					mPlug = effectorPlug[i]
					connectedPlug = OpenMaya.MPlugArray()
					mPlug.connectedTo(connectedPlug,True,False)
					if connectedPlug.length() > 0:
						if connectedPlug[0].node().apiType() == OpenMaya.MFn.kJoint:
							self.joint3 = connectedPlug[0].node()

				if self.joint1.apiType() == OpenMaya.MFn.kJoint and self.joint3.apiType() == OpenMaya.MFn.kJoint:
					#start joint and end joint are both found
					#next need to locate joint2
					joint1DependNode = OpenMaya.MFnDependencyNode(self.joint1)
					joint3DependNOde = OpenMaya.MFnDependencyNode(self.joint3)
					#find joint2 from joint3
					inverseScalePlug = joint3DependNOde.findPlug('inverseScale')
					otherPlug = OpenMaya.MPlugArray()
					inverseScalePlug.connectedTo(otherPlug,True, False)
					if otherPlug.length() > 0:
						self.joint2 = otherPlug[0].node()
					#double check joint2 from joint1
					scalePlug = joint1DependNode.findPlug('scale')
					scalePlug.connectedTo(otherPlug,False,True)
					for i in range(otherPlug.length()):
						if otherPlug[i].node() == self.joint2:
							print 'find joint2'
							self.joint2 = otherPlug[i].node()
					#=============================================================#
					#here we found all the items for ikfk switch
					if mode == 'fk':
						try:
							IKHandleDependNode = OpenMaya.MFnDependencyNode(self.activeIKHandle)
							ikBlendPlug = IKHandleDependNode.findPlug('ikBlend')
							ikBlendPlugAttr = ikBlendPlug.attribute()
							ikBlendAttribute = OpenMaya.MFnAttribute(ikBlendPlugAttr)
							ikBlendPlug.setInt(0)
							#ikBlendAttribute.setInt(0)
						except Exception,e:
							print e
							pass
					#mode ---> ik
					else:
						try:
							#get joint2 transform and poleVectorController transform
							if (self.joint2.apiType() == OpenMaya.MFn.kJoint):
								mFnTransform_poleVectorController = OpenMaya.MFnTransform(self.poleVectorController)
								mFnTransform_joint2 = OpenMaya.MFnTransform(self.joint2)

								mDagPath_joint2 = OpenMaya.MDagPath()
								mFnTransform_joint2.getPath(mDagPath_joint2)
								mFnTransform_joint2.setObject(mDagPath_joint2)

								mDagPath_poleVectorController = OpenMaya.MDagPath()
								mFnTransform_poleVectorController.getPath(mDagPath_poleVectorController)
								mFnTransform_poleVectorController.setObject(mDagPath_poleVectorController)
								#?Do not work with freeze translation...
								mFnTransform_poleVectorController.setTranslation(mFnTransform_joint2.getTranslation(OpenMaya.MSpace.kWorld), OpenMaya.MSpace.kWorld)
							
							IKHandleDependNode = OpenMaya.MFnDependencyNode(self.activeIKHandle)
							ikBlendPlug = IKHandleDependNode.findPlug('ikBlend')
							ikBlendPlug.setInt(1)
							#ikBlendAttribute.setInt(1)
						except Exception,e:
							print e
							pass

					#=============================================================#

		print self.joint1.apiTypeStr()
		print self.joint2.apiTypeStr()
		print self.joint3.apiTypeStr()
		print self.activeIKHandle.apiTypeStr()
		print self.activeIKEffector.apiTypeStr()
		print self.poleVectorController.apiTypeStr()
		print self.poleVector.apiTypeStr()
		print mode



	def remove(self, node, clientdata):
		mdependNode = OpenMaya.MFnDependencyNode(node)
		if node == self.thisMObject():
			for i in xrange(len(self.idCallback)):
				try:
					OpenMaya.MEventMessage.removeCallback(self.idCallback[i])
				except:
					pass
				try:
					OpenMaya.MDGMessage.removeCallback(self.idCallback[i])
				except:
					pass
				#clear callback list
				self.idCallback=[]
		else:
			return 'unknown'


	#virtual compute
	def compute(self, pPlug, pDataBlcok):
		return OpenMaya.kUnknownParameter


#create a pointer to our Node class
def nodeCreator():
	return OpenMayaMPx.asMPxPtr(CVGNode())


def nodeInitializer():
	pass


def initializePlugin(mObject):
    mplugin = OpenMayaMPx.MFnPlugin(mObject,'Ryan Wang', '1.0')
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
