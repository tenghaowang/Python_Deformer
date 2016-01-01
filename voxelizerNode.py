#Created By RyanWang
#@Used for convert any geometry to voxel
#support color mapping
#still working on animation mapping
#feel free to contact me @ tenghaow@andrew.cmu.edu

import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds
import math
import sys

#customize VoxelizerNode
#plugin information
nodeName = 'voxelizerNode'        					#node name
nodeID = OpenMaya.MTypeId (0x1005fff)				#A unique ID associated to this node type

defaultVoxelWidth = 1.0
defaultVoxelGap = 0.1

class voxel(object):
    def __init__(self):
        # instance variable unique to each instance
    	self.voxelCenterPositions=[]
    	self.uvCoordArray=[]

class voxelizerNode (OpenMayaMPx.MPxNode):

	#define attribute handle
	voxelWidth = OpenMaya.MObject()
	voxelGap = OpenMaya.MObject()
	voxelMessage = OpenMaya.MObject()
	vertexColor = OpenMaya.MObject()
	inputMesh = OpenMaya.MObject()
	outputMesh = OpenMaya.MObject()

	def __init__(self):
		'''constructor(call the base class's constructor)'''
		OpenMayaMPx.MPxNode.__init__(self)

	def compute (self, pPlug, pDataBlock):
		if (pPlug == voxelizerNode.outputMesh):
			#query the incoming mesh's shader for later color mapping
			'''
			inPlug = OpenMaya.MPlug(self.thisMObject(),voxelizerNode.inputMesh)
			connections = OpenMaya.MPlugArray()
			inPlug.connectedTo(connections, True, False)
			mDependNode = OpenMaya.MFnDependencyNode (connections[0].node())
			mSelectionList = OpenMaya.MSelectionList()
			mSelectionList.add(mDependNode.name())
			mDagPath =OpenMaya.MDagPath()
			mSelectionList.getDagPath(0,mDagPath)
			mFnMesh = OpenMaya.MFnMesh(mDagPath)
			'''
			#use message node to pass the file name
			vertexColPlug = OpenMaya.MPlug(self.thisMObject(), voxelizerNode.vertexColor)
			connections = OpenMaya.MPlugArray()
			vertexColPlug.connectedTo(connections, True, False)
			if connections.length() > 0:
				mDependNode = OpenMaya.MFnDependencyNode (connections[0].node())
				texNodeName = mDependNode.name()
				print 'vertex mapping'
			else:
				texNodeName = False
				print 'no vertex color mapping '
			#This method will only work with a MFnMesh function set which has been initialized with an MFn::kMesh.
			#texNodeName = self.meshTextureNode(mFnMesh) # 'file1' #
			#get custom input node attributes and values
			voxelWidthHandle = pDataBlock.inputValue(voxelizerNode.voxelWidth)
			voxelWidthValue = voxelWidthHandle.asFloat()

			voxelGapHandle = pDataBlock.inputValue(voxelizerNode.voxelGap)
			voxelGapValue = voxelGapHandle.asFloat()

			inputMeshHandle = pDataBlock.inputValue(voxelizerNode.inputMesh)
			inputMeshObj = inputMeshHandle.asMesh()
			#inputMeshObj ---> kMeshData not KMesh
			mFnMesh = OpenMaya.MFnMesh(inputMeshObj)
			#compute the bounding box for the mesh's vertices
			BBox = OpenMaya.MBoundingBox()
			BBox = self.getBoundingBox(mFnMesh)
			voxelData = voxel()
			#meshContainer = OpenMaya.MObject()
			meshDataFn = OpenMaya.MFnMeshData()
			outputMeshData = meshDataFn.create()

			voxelDistance = voxelGapValue + voxelWidthValue
			voxelData = self.getVoxels(voxelDistance, BBox, mFnMesh)
			voxelCenterPositions =voxelData.voxelCenterPositions
			uvArray = voxelData.uvCoordArray
			#create a cube polygon for each voxel and populate the outputMeshData Object

			outputMeshData = self.createVoxelMesh(voxelCenterPositions, uvArray, texNodeName,voxelWidthValue, outputMeshData)
			#set the output data
			outputMeshHandle = pDataBlock.outputValue(voxelizerNode.outputMesh)
			outputMeshHandle.setMObject(outputMeshData)
			pDataBlock.setClean(pPlug)

		else:
			return 'UnKnown'

#'''
#Reference for connectionMade and connectionBroken
#http://mayastation.typepad.com/maya-station/2012/03/working-with-internal-data-using-setinternalvalueincontext.html
#'''
	def connectionMade(self, pPlug, otherPlug, asSrc):
		if (pPlug ==voxelizerNode.inputMesh):
			print 'detect inputMesh Conncetion'
		return OpenMayaMPx.MPxNode.connectionMade(self, pPlug, otherPlug, asSrc)

	#use maya API to generate the polycube primitives 
	def createPolyCube(self, meshContainer, cubeWidth, voxelCenterPosition):
			mDagNode = OpenMaya.MFnDagNode()
			myCube=cmds.polyCube(w=cubeWidth,h=cubeWidth,d=cubeWidth)
			cmds.move(voxelCenterPosition.x, voxelCenterPosition.y, voxelCenterPosition.z, myCube)
			cmds.parent(myCube[0], meshContainer)


	#The code below is to manully generate the polycube primitive
	def createVoxelMesh(self, voxelCenterPosition,uvArray,texNodeName,cubeWidth,outputMeshData):
		numVoxels = len(voxelCenterPosition)
		numVertices = 8														#number of vertices
		numPolygons = 6 													#number of polygons
		numVerticesPerPolygon = 4     										#number of vertices per polygon
		numNormalsPerVoxel = numVerticesPerPolygon * numPolygons 			#24 number of vertex normals
		numPolygonConnectsPerVoxel = numPolygons * numVerticesPerPolygon 	#24 number of polygon connects
		cubeHalfWidth = cubeWidth/2
		#initialize all the params in the MFnMesh.create()
		#vertexArray: point array, This should include all the vertices in the mesh and no eatras
		totalVertices = numVertices * numVoxels
		vertexArray =OpenMaya.MFloatPointArray()
		#polygonCounts array of vertex counts for each polygon
		#for the cube would have 6 faces, each of which had 4 verts, so the polygonCounts would be [4,4,4,4,4,4]
		totalPolygons = numPolygons * numVoxels
		polygonCounts = OpenMaya.MIntArray()
		#polygonConnects 
		#array of vertex connections for each polygon
		polygonConnects = OpenMaya.MIntArray()
		#set shared Normals for these vertices
		vertexNormals = OpenMaya.MVectorArray()
		#vertexColorArray
		vertexColorArray = OpenMaya.MColorArray()
		#vertexColorIndexArray
		vertexIndexArray = OpenMaya.MIntArray()
		#PolygonIDArray
		faceList = OpenMaya.MIntArray()

		for i in range (numVoxels):
			pVoxelCenterPosition = voxelCenterPosition[i]
			#Update VertexArray for VoxelMesh
			vertexList = [	OpenMaya.MFloatPoint(pVoxelCenterPosition.x-cubeHalfWidth, pVoxelCenterPosition.y-cubeHalfWidth, pVoxelCenterPosition.z-cubeHalfWidth), #vertex 0 
							OpenMaya.MFloatPoint(pVoxelCenterPosition.x-cubeHalfWidth, pVoxelCenterPosition.y-cubeHalfWidth, pVoxelCenterPosition.z+cubeHalfWidth), #vertex 1
							OpenMaya.MFloatPoint(pVoxelCenterPosition.x-cubeHalfWidth, pVoxelCenterPosition.y+cubeHalfWidth, pVoxelCenterPosition.z-cubeHalfWidth), #vertex 2
							OpenMaya.MFloatPoint(pVoxelCenterPosition.x-cubeHalfWidth, pVoxelCenterPosition.y+cubeHalfWidth, pVoxelCenterPosition.z+cubeHalfWidth), #vertex 3
							OpenMaya.MFloatPoint(pVoxelCenterPosition.x+cubeHalfWidth, pVoxelCenterPosition.y-cubeHalfWidth, pVoxelCenterPosition.z-cubeHalfWidth), #vertex 4
							OpenMaya.MFloatPoint(pVoxelCenterPosition.x+cubeHalfWidth, pVoxelCenterPosition.y-cubeHalfWidth, pVoxelCenterPosition.z+cubeHalfWidth), #vertex 5
							OpenMaya.MFloatPoint(pVoxelCenterPosition.x+cubeHalfWidth, pVoxelCenterPosition.y+cubeHalfWidth, pVoxelCenterPosition.z-cubeHalfWidth), #vertex 6
							OpenMaya.MFloatPoint(pVoxelCenterPosition.x+cubeHalfWidth, pVoxelCenterPosition.y+cubeHalfWidth, pVoxelCenterPosition.z+cubeHalfWidth), #vertex 7
						 ]

			for j in range (numVertices):
				vertexArray.append(vertexList[j])
				#here need to assign vertex color
				if texNodeName:
					vertexColor = cmds.colorAtPoint(texNodeName, o='RGB', u=uvArray[i][0], v=uvArray[i][1])
					mColor = OpenMaya.MColor(vertexColor[0],vertexColor[1],vertexColor[2],1.0)
					vertexColorArray.append(mColor)
					vertexIndexArray.append(i * numVertices + j)
				#print vertexColor

			#Update polygonCounts for VoxelMesh
			for j in range (numPolygons):
				polygonCounts.append(numVerticesPerPolygon)
				faceList.append(i*numPolygons+j)
			#Update polygonConnects for VoxelMesh
			#Update vertexNormals for VoxelMesh
			polygonConnectsList = [	0,1,3,2,
									1,5,7,3,
									4,6,7,5,
									2,6,4,0,
									0,4,5,1,
									2,3,7,6]

			vertexNormalsList = [	OpenMaya.MVector(-1.0,0.0,0.0),   		#vertex normal on face (0,1,3,2) #0
									OpenMaya.MVector(-1.0,0.0,0.0),			#vertex normal on face (0,1,3,2) #1
									OpenMaya.MVector(-1.0,0.0,0.0),			#vertex normal on face (0,1,3,2) #7
									OpenMaya.MVector(-1.0,0.0,0.0),			#vertex normal on face (0,1,3,2) #3

									OpenMaya.MVector(0.0,0.0,1.0),   		#vertex normal on face (1,5,7,3) #1
									OpenMaya.MVector(0.0,0.0,1.0),			#vertex normal on face (1,5,7,3) #5
									OpenMaya.MVector(0.0,0.0,1.0),			#vertex normal on face (1,5,7,3) #7 
									OpenMaya.MVector(0.0,0.0,1.0),			#vertex normal on face (1,5,7,3) #3

									OpenMaya.MVector(1.0,0.0,0.0),   		#vertex normal on face (4,6,7,5) #4
									OpenMaya.MVector(1.0,0.0,0.0),			#vertex normal on face (4,6,7,5) #6
									OpenMaya.MVector(1.0,0.0,0.0),			#vertex normal on face (4,6,7,5) #7
									OpenMaya.MVector(1.0,0.0,0.0),			#vertex normal on face (4,6,7,5) #5

									OpenMaya.MVector(0.0,0.0,-1.0),   		#vertex normal on face (2,6,4,0) #2
									OpenMaya.MVector(0.0,0.0,-1.0),			#vertex normal on face (2,6,4,0) #6
									OpenMaya.MVector(0.0,0.0,-1.0),			#vertex normal on face (2,6,4,0) #4
									OpenMaya.MVector(0.0,0.0,-1.0),			#vertex normal on face (2,6,4,0) #0

									OpenMaya.MVector(0.0,-1.0,0.0),   		#vertex normal on face (0,4,5,1) #0 
									OpenMaya.MVector(0.0,-1.0,0.0),			#vertex normal on face (0,4,5,1) #4
									OpenMaya.MVector(0.0,-1.0,0.0),			#vertex normal on face (0,4,5,1) #5
									OpenMaya.MVector(0.0,-1.0,0.0),			#vertex normal on face (0,4,5,1) #1

									OpenMaya.MVector(0.0,1.0,0.0),   		#vertex normal on face (2,3,7,6) #2
									OpenMaya.MVector(0.0,1.0,0.0),			#vertex normal on face (2,3,7,6) #3
									OpenMaya.MVector(0.0,1.0,0.0),			#vertex normal on face (2,3,7,6) #7
									OpenMaya.MVector(0.0,1.0,0.0)			#vertex normal on face (2,3,7,6) #6
								]			
			for j in range (numNormalsPerVoxel):
				vertexNormals.append(vertexNormalsList[j])
				polygonConnects.append(polygonConnectsList[j] + i * numVertices)
			#for j in range (numPolygonConnectsPerVoxel):



		mFnMesh = OpenMaya.MFnMesh()
		#shapeNode
		mMeshShape = mFnMesh.create (totalVertices, totalPolygons, vertexArray, polygonCounts, polygonConnects,outputMeshData)
		#mMeshShape --> kMeshGeom
		mCubeMesh = OpenMaya.MFnMesh(mMeshShape)
		'''
		#assign Normal to the Cubes:

		#confused how to use setFaceVertexNormals
		#rewrite the function for setFaceVertexNormals based on setFaceVertexNormal
		#by query the facelist
		#support hard edge!

		for i in range (faceList.length()):
			for j in range (numVerticesPerPolygon):
				index = numVerticesPerPolygon * i + j
				mCubeMesh.setFaceVertexNormal(vertexNormals[index], i, polygonConnects[index])
		'''
		#'''
		#setVertexColor
		if texNodeName:
			mCubeMesh.createColorSetDataMesh('vertexColorSet')
			mCubeMesh.setVertexColors(vertexColorArray, vertexIndexArray, None, OpenMaya.MFnMesh.kRGBA)
		#'''

		return outputMeshData


	def getVoxels (self, mVoxelDistance, mBBox, mMeshObj):
		'''
		iterate all the points inside the bounding box and do the
		intersection test with the mesh
		odd intersection times: inside the mesh
		else: outside the mesh
		onlu create voxel inside the mesh
		'''
		voxelCenterPositions=[]
		uvArray = []
		util = OpenMaya.MScriptUtil()

		mHalfVoxelDistance = mVoxelDistance/2

		mMidPoint = OpenMaya.MPoint()
		mMidPoint.x = (mBBox.min().x + mBBox.max().x)/2
		mMidPoint.y = (mBBox.min().y + mBBox.max().y)/2
		mMidPoint.z = (mBBox.min().z + mBBox.max().z)/2

		#write customized float iterator		
		def floatRange(start, stop, step):
			s=start
			if s <stop:
				while (s < stop) :
					yield s
					s = s + step
			else:
				while (s>stop):
					yield s
					s = s - step

		# iterate all the points inside the BoundingBox
		# iterate from the MidPoint
		# searching algorithm
		def searchArea(startPoint, endPoint, step , rayDirection, voxelCenterPositions):
			for point_Zcoord in floatRange (startPoint.z, endPoint.z, step):
				for point_Xcoord in floatRange (startPoint.x, endPoint.x, step):
					for point_Ycoord in floatRange (startPoint.y, endPoint.y, step):
						#create ray source and direction
						raySource = OpenMaya.MFloatPoint(point_Xcoord,point_Ycoord,point_Zcoord)
						#rayDirection = OpenMaya.MFloatVector(0,0,-1)
						hitPointArray = OpenMaya.MFloatPointArray()
						hitRayParams = OpenMaya.MFloatArray()
						tolerance = 1e-6
						mMeshObj.allIntersections( raySource,   	   	#raySource
												   rayDirection,	   	#rayDirection
												   None,			   	#faceIds do not need to filter the face
												   None,			   	#triDis do not need to filter the tris
												   False,				# do not need to sort the IDs
												   OpenMaya.MSpace.kTransform,	#ray source and direction are specified in the mesh local coordinates
												   float(9999),			#the range of the ray
												   False,				#do not need to test both directions	
												   None,				#do not need accelParams
												   False,				#do not need to sort hits
												   hitPointArray,		#return the hit point array
												   hitRayParams,		#return hit point distance params
												   None,				#do not need hit faces ids
												   None,				#do not need hit tris ids
												   None,				#do not need barycentric coordinates of faces
												   None,				#do not need barycentric coordinates of tris
												   tolerance            #hit tolerance
													)

						#add the inside raysouce into list for voxel placement
						if (hitPointArray.length()%2 == 1):
							voxelCenterPositions.append(raySource)
							#also need to query the intersection geometry color
							#find nearest intersection point
							#http://www.chadvernon.com/blog/resources/maya-api-programming/mscriptutil/
							#Since the Maya API is designed as a C++ library, it has many pointers and references 
							#that are passed into and returned from various functions. 
							uvPoint = util.asFloat2Ptr()
							mPoint = OpenMaya.MPoint(raySource)
							mMeshObj.getUVAtPoint (mPoint, uvPoint)
							u = util.getFloat2ArrayItem (uvPoint,0,0)
							v = util.getFloat2ArrayItem (uvPoint,0,1)
							uv = [u,v]
							uvArray.append(uv)						

		#populate raysource Positions
		xmin = mBBox.min().x
		ymin = mBBox.min().y
		zmin = mBBox.min().z
		xmax = mBBox.max().x
		ymax = mBBox.max().y
		zmax = mBBox.max().z
		mBBoxPoints = [ OpenMaya.MPoint(xmin, ymin, zmin),
						OpenMaya.MPoint(xmin, ymin, zmax),
						OpenMaya.MPoint(xmin, ymax, zmin),
						OpenMaya.MPoint(xmin, ymax, zmax),
						OpenMaya.MPoint(xmax, ymin, zmin),
						OpenMaya.MPoint(xmax, ymin, zmax),
						OpenMaya.MPoint(xmax, ymax, zmin),
						OpenMaya.MPoint(xmax, ymax, zmax)
						]
		#search all the area inside the bounding box from center
		#'''
		rayDirection = OpenMaya.MFloatVector(-1,0,0)
		searchArea(mMidPoint, mBBoxPoints[0], mVoxelDistance, rayDirection, voxelCenterPositions)

		mNewPoint = OpenMaya.MPoint()
		mNewPoint.x = mMidPoint.x
		mNewPoint.y = mMidPoint.y 
		mNewPoint.z = mMidPoint.z + mVoxelDistance
		searchArea(mNewPoint, mBBoxPoints[1], mVoxelDistance, rayDirection, voxelCenterPositions)

		mNewPoint = OpenMaya.MPoint()
		mNewPoint.x = mMidPoint.x 
		mNewPoint.y = mMidPoint.y +mVoxelDistance
		mNewPoint.z = mMidPoint.z 
		searchArea(mNewPoint, mBBoxPoints[2], mVoxelDistance, rayDirection, voxelCenterPositions)

		mNewPoint = OpenMaya.MPoint()
		mNewPoint.x = mMidPoint.x 
		mNewPoint.y = mMidPoint.y + mVoxelDistance
		mNewPoint.z = mMidPoint.z + mVoxelDistance
		searchArea(mNewPoint, mBBoxPoints[3], mVoxelDistance, rayDirection, voxelCenterPositions)


		rayDirection = OpenMaya.MFloatVector(1,0,0)
		mNewPoint = OpenMaya.MPoint()
		mNewPoint.x = mMidPoint.x + mVoxelDistance
		mNewPoint.y = mMidPoint.y 
		mNewPoint.z = mMidPoint.z 
		searchArea(mNewPoint, mBBoxPoints[4], mVoxelDistance, rayDirection, voxelCenterPositions)

		mNewPoint = OpenMaya.MPoint()
		mNewPoint.x = mMidPoint.x + mVoxelDistance
		mNewPoint.y = mMidPoint.y
		mNewPoint.z = mMidPoint.z + mVoxelDistance
		searchArea(mNewPoint, mBBoxPoints[5], mVoxelDistance, rayDirection, voxelCenterPositions)

		mNewPoint = OpenMaya.MPoint()
		mNewPoint.x = mMidPoint.x + mVoxelDistance
		mNewPoint.y = mMidPoint.y + mVoxelDistance
		mNewPoint.z = mMidPoint.z
		searchArea(mNewPoint, mBBoxPoints[6], mVoxelDistance, rayDirection, voxelCenterPositions)

		mNewPoint = OpenMaya.MPoint()
		mNewPoint.x = mMidPoint.x + mVoxelDistance
		mNewPoint.y = mMidPoint.y + mVoxelDistance
		mNewPoint.z = mMidPoint.z + mVoxelDistance
		searchArea(mNewPoint, mBBoxPoints[7], mVoxelDistance, rayDirection, voxelCenterPositions)
		#'''

		'''
		for point_Zcoord in floatRange (mMinPoint.z, mMaxPoint.z, mVoxelDistance):
			for point_Xcoord in floatRange (mMinPoint.x, mMaxPoint.x, mVoxelDistance):
				for point_Ycoord in floatRange (mMinPoint.y, mMaxPoint.y, mVoxelDistance):
					#create ray source and direction
					raySource = OpenMaya.MFloatPoint(point_Xcoord,point_Ycoord,point_Zcoord)
					rayDirection = OpenMaya.MFloatVector(0,0,-1)
					hitPointArray = OpenMaya.MFloatPointArray()
					tolerance = 1e-6
					mMeshObj.allIntersections( raySource,   	   	#raySource
											   rayDirection,	   	#rayDirection
											   None,			   	#faceIds do not need to filter the face
											   None,			   	#triDis do not need to filter the tris
											   False,				# do not need to sort the IDs
											   OpenMaya.MSpace.kTransform,	#ray source and direction are specified in the mesh local coordinates
											   float(9999),			#the range of the ray
											   False,				#do not need to test both directions	
											   None,				#do not need accelParams
											   False,				#do not need to sort hits
											   hitPointArray,		#return the hit point array
											   None,				#do not need the hit point distance params
											   None,				#do not need hit faces ids
											   None,				#do not need hit tris ids
											   None,				#do not need barycentric coordinates of faces
											   None,				#do not need barycentric coordinates of tris
											   tolerance            #hit tolerance
												)
					if (hitPointArray.length()%2 == 1):
						voxelCenterPositions.append(raySource)
		'''
		voxelData =voxel()
		voxelData.voxelCenterPositions = voxelCenterPositions
		voxelData.uvCoordArray = uvArray
		return voxelData



	def getBoundingBox (self, mMeshObj):

		mPointArray = OpenMaya.MPointArray ()
		mMeshObj.getPoints (mPointArray, OpenMaya.MSpace.kTransform)
		BBox = OpenMaya.MBoundingBox()
		for i in range(mPointArray.length()):
			BBox.expand (mPointArray[i])
		print BBox.min().x
		print BBox.max().x
		return BBox 
	#-----
	#This method will only work with a MFnMesh function set which has been initialized with an MFn::kMesh.
	#-----
	def meshTextureNode(self, mMeshObj):
		shaders = OpenMaya.MObjectArray()
		indices = OpenMaya.MIntArray()
		mMeshObj.getConnectedShaders(0,shaders,indices)
		#here I only consider the geometry applied simple one shader
		#default lamber1
		shaderGroup = OpenMaya.MFnDependencyNode(shaders[0])
		shaderPlug = OpenMaya.MPlug()
		shaderPlug = shaderGroup.findPlug('surfaceShader')
		connections = OpenMaya.MPlugArray()
		shaderPlug.connectedTo(connections, True, False)
		if connections.length() > 0:
			#go to read shader body
			#consider LambertShader
			LambertShader = OpenMaya.MFnLambertShader (connections[0].node())
			#print LambertShader.name()
			mColorInput = LambertShader.findPlug('color')
			fileOutput = OpenMaya.MPlugArray()
			mColorInput.connectedTo(fileOutput, True, False)

			if fileOutput.length()>0:
				dependNode = OpenMaya.MFnDependencyNode(fileOutput[0].node())
				print "find file input"
				return dependNode.name()
			else:
				print 'there is no texture(lambert) bind to the mesh'
				return False



def nodeCreator():
	#Create a pointer to voxelizer node class
	return OpenMayaMPx.asMPxPtr(voxelizerNode())

def nodeInitializer():
	#Defines the input and ouput attributes as static variables
	#in our class
	#creat functionsets
	numericAttrFn = OpenMaya.MFnNumericAttribute()
	typedAttrFn = OpenMaya.MFnTypedAttribute()
	messageAttrFn = OpenMaya.MFnMessageAttribute()
	#INPUT NODE ATTRIBUTES
	#creates attributes
	global defaultVoxelWidth
	voxelizerNode.voxelWidth = numericAttrFn.create('voxelWidth', 'vw', OpenMaya.MFnNumericData.kFloat, defaultVoxelWidth)
	numericAttrFn.setReadable(False)          #define input cannot be used as output
	numericAttrFn.setWritable(True)
	numericAttrFn.setStorable(True)
	numericAttrFn.setKeyable(True)
	numericAttrFn.setMin(0.1)
	voxelizerNode.addAttribute(voxelizerNode.voxelWidth)

	global defaultVoxelGap
	voxelizerNode.voxelGap = numericAttrFn.create('voxelGap', 'vg',OpenMaya.MFnNumericData.kFloat, defaultVoxelGap)
	numericAttrFn.setReadable(False)
	numericAttrFn.setWritable(True)
	numericAttrFn.setStorable(True)
	numericAttrFn.setKeyable(True)
	numericAttrFn.setMin(0)
	voxelizerNode.addAttribute(voxelizerNode.voxelGap)

	#need an message attribute to declare relationship
	voxelizerNode.voxelMessage = messageAttrFn.create('voxelMessage', 'vm')
	messageAttrFn.setReadable(False)
	messageAttrFn.setWritable(True)
	messageAttrFn.setStorable(True)
	messageAttrFn.setKeyable(False)
	voxelizerNode.addAttribute(voxelizerNode.voxelMessage)

	#try use color attributeto declare relationship and get texture node name
	voxelizerNode.vertexColor = numericAttrFn.createColor('vertexColor', 'vc')
	numericAttrFn.setReadable(False)
	numericAttrFn.setWritable(True)
	numericAttrFn.setStorable(True)
	voxelizerNode.addAttribute(voxelizerNode.vertexColor)

	#need an input mesh attribute
	voxelizerNode.inputMesh = typedAttrFn.create('inputMesh', 'im', OpenMaya.MFnData.kMesh)
	typedAttrFn.setReadable(False)
	typedAttrFn.setWritable(True)
	typedAttrFn.setStorable(True)
	voxelizerNode.addAttribute(voxelizerNode.inputMesh)

	#OUTPUT NODE ATTRIBUTE
	#creates attributes
	voxelizerNode.outputMesh = typedAttrFn.create('outputMesh', 'om', OpenMaya.MFnData.kMesh)
	typedAttrFn.setWritable(False)
	typedAttrFn.setReadable(True)
	typedAttrFn.setStorable(False)
	typedAttrFn.setKeyable(False)
	voxelizerNode.addAttribute(voxelizerNode.outputMesh)


	#set dirty
	voxelizerNode.attributeAffects(voxelizerNode.voxelWidth, voxelizerNode.outputMesh)
	voxelizerNode.attributeAffects(voxelizerNode.voxelGap, voxelizerNode.outputMesh)
	voxelizerNode.attributeAffects(voxelizerNode.vertexColor, voxelizerNode.outputMesh)
	voxelizerNode.attributeAffects(voxelizerNode.inputMesh, voxelizerNode.outputMesh)
	print 'setDirty'


def initializePlugin(mObject):
	'''Initialize the plugin'''
	mplugin = OpenMayaMPx.MFnPlugin(mObject, 'Ryan Wang','1.0')
	try:
		mplugin.registerNode(nodeName, nodeID, nodeCreator, nodeInitializer)
	except:
		sys.stderr.write('Failed to register node:' + nodeName)
		raise

def uninitializePlugin(mObject):
	'''uninitialize the plugin'''
	mplugin = OpenMayaMPx.MFnPlugin(mObject)
	try:
		mplugin.registerNode(nodeName)
	except:
		sys.stderr.write('Failed to deregister node' + nodeName)
		raise




