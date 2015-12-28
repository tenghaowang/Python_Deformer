import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds
import math
import sys

#customize VoxelizerNode
#plugin information
nodeName = 'voxelizerNode'
nodeID = OpenMaya.MTypeId (0x1003fff)


class voxel(object):
    def __init__(self):
        # instance variable unique to each instance
    	self.voxelCenterPositions=[]
    	self.voxelColor=[]

def createMeshContainer():
	mDagNode = OpenMaya.MFnDagNode()
	mTransform = OpenMaya.MObject()
	mGroup = mDagNode.create('transform','voxelGeom')
	mDependNode = OpenMaya.MFnDependencyNode(mGroup)
	#print mDependNode.name()
	return mDependNode.name()

#use maya API to generate the polycube primitives 
def createPolyCube(meshContainer, cubeWidth, voxelCenterPosition):
		mDagNode = OpenMaya.MFnDagNode()
		myCube=cmds.polyCube(w=cubeWidth,h=cubeWidth,d=cubeWidth)
		cmds.move(voxelCenterPosition.x, voxelCenterPosition.y, voxelCenterPosition.z, myCube)
		cmds.parent(myCube[0], meshContainer)


#The code below is to manully generate the polycube primitive
def createVoxelMesh(meshContainer, voxelCenterPosition,cubeWidth):
	numVoxels = len(voxelCenterPosition)
	numVertices = 8			#number of vertices
	numPolygons = 6 		#number of polygons
	numVerticesPerPolygon = 4     #number of vertices per polygon
	numNormalsPerVoxel = numVerticesPerPolygon * numPolygons #24 number of vertex normals
	numPolygonConnectsPerVoxel = numPolygons * numVerticesPerPolygon #24 number of polygon connects
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
	totalPolygonConnects = numPolygonConnectsPerVoxel * numVoxels
	polygonConnects = OpenMaya.MIntArray()

	#set shared Normals for these vertices
	totalNormals = numNormalsPerVoxel * numVoxels
	vertexNormals = OpenMaya.MVectorArray()

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
		#print polygonCounts.length()
		#Update polygonCounts for VoxelMesh
		for j in range (numPolygons):
			polygonCounts.append(numVerticesPerPolygon)
		#Update polygonConnects for VoxelMesh
		#print polygonConnects.length()
		polygonConnectsList = [	0,1,3,2,
								1,5,7,3,
								4,6,7,5,
								2,6,4,0,
								0,4,5,1,
								2,3,7,6]
		#print numPolygonConnectsPerVoxel
		for j in range (numPolygonConnectsPerVoxel):
			polygonConnects.append(polygonConnectsList[j] + i * numVertices)
		#Update vertexNormals for VoxelMesh

		vertexNormalsList = [	OpenMaya.MVector(-1.0,0.0,0.0),   		#vertex normal on face (0,1,3,2) #0
								OpenMaya.MVector(-1.0,0.0,0.0),		#vertex normal on face (0,1,3,2) #1
								OpenMaya.MVector(-1.0,0.0,0.0),		#vertex normal on face (0,1,3,2) #7
								OpenMaya.MVector(-1.0,0.0,0.0),		#vertex normal on face (0,1,3,2) #3

								OpenMaya.MVector(0.0,0.0,1.0),   		#vertex normal on face (1,5,7,3) #1
								OpenMaya.MVector(0.0,0.0,1.0),			#vertex normal on face (1,5,7,3) #5
								OpenMaya.MVector(0.0,0.0,1.0),			#vertex normal on face (1,5,7,3) #7 
								OpenMaya.MVector(0.0,0.0,1.0),			#vertex normal on face (1,5,7,3) #3

								OpenMaya.MVector(1.0,0.0,0.0),   		#vertex normal on face (4,6,7,5) #4
								OpenMaya.MVector(1.0,0.0,0.0),			#vertex normal on face (4,6,7,5) #6
								OpenMaya.MVector(1.0,0.0,0.0),			#vertex normal on face (4,6,7,5) #7
								OpenMaya.MVector(1.0,0.0,0.0),			#vertex normal on face (4,6,7,5) #5

								OpenMaya.MVector(0.0,0.0,-1.0),   		#vertex normal on face (2,6,4,0) #2
								OpenMaya.MVector(0.0,0.0,-1.0),		#vertex normal on face (2,6,4,0) #6
								OpenMaya.MVector(0.0,0.0,-1.0),		#vertex normal on face (2,6,4,0) #4
								OpenMaya.MVector(0.0,0.0,-1.0),		#vertex normal on face (2,6,4,0) #0

								OpenMaya.MVector(0.0,-1.0,0.0),   		#vertex normal on face (0,4,5,1) #0 
								OpenMaya.MVector(0.0,-1.0,0.0),		#vertex normal on face (0,4,5,1) #4
								OpenMaya.MVector(0.0,-1.0,0.0),		#vertex normal on face (0,4,5,1) #5
								OpenMaya.MVector(0.0,-1.0,0.0),		#vertex normal on face (0,4,5,1) #1

								OpenMaya.MVector(0.0,1.0,0.0),   		#vertex normal on face (2,3,7,6) #2
								OpenMaya.MVector(0.0,1.0,0.0),			#vertex normal on face (2,3,7,6) #3
								OpenMaya.MVector(0.0,1.0,0.0),			#vertex normal on face (2,3,7,6) #7
								OpenMaya.MVector(0.0,1.0,0.0)			#vertex normal on face (2,3,7,6) #6
							]			
		for j in range (numNormalsPerVoxel):
			vertexNormals.append(vertexNormalsList[j])


	mFnMesh = OpenMaya.MFnMesh()
	'''
	uArray = OpenMaya.MFloatArray()
	uArray.setLength(14)
	vArray = OpenMaya.MFloatArray()
	vArray.setLength(14)
	uList = [0.375, 0.625, 0.375, 0.625, 0.375, 0.625, 0.375, 0.625, 0.375, 0.625, 0.875, 0.875, 0.125, 0.125]
	vList = [0.0, 0.0, 0.25, 0.25, 0.5, 0.5, 0.75, 0.75, 1.0, 1.0, 0.0, 0.25, 0.0, 0.25]
	for i in range (14):
		uArray.set(uList[i],i)
	for i in range (14):
		vArray.set(vList[i],i)
	'''
	#shapeNode
	mMeshShape = mFnMesh.create (totalVertices, totalPolygons, vertexArray, polygonCounts, polygonConnects)
	mDagNode = OpenMaya.MFnDagNode(mMeshShape)
	#print mDagNode.name()
	mDagPath = OpenMaya.MDagPath()
	mDagNode = OpenMaya.MFnDagNode(mDagNode.child(0))
	#print mDagNode.name()
	mDagNode.getPath(mDagPath)
	mCubeMesh = OpenMaya.MFnMesh(mDagPath)

	#assign Normal to the Cubes:

	facelist = OpenMaya.MIntArray()
	for i in range(totalPolygons):
		facelist.append(i)
	#confused how to use setFaceVertexNormals
	#rewrite the function for setFaceVertexNormals based on setFaceVertexNormal
	#by query the facelist
	#support hard edge!
	'''
	for i in range (facelist.length()):
		for j in range (numVerticesPerPolygon):
			index = numVerticesPerPolygon * i + j
			mCubeMesh.setFaceVertexNormal(vertexNormals[index], i, polygonConnects[index])
	'''
	#--[retrive initialShadingGroup]--#
	mSelectionList = OpenMaya.MSelectionList()
	mSelectionList.add("initialShadingGroup")
	
	mObject_initShdGrp= OpenMaya.MObject()
	mSelectionList.getDependNode(0,mObject_initShdGrp) 
	mFnDependencyNode_initialShadingGroup = OpenMaya.MFnDependencyNode(mObject_initShdGrp)
	#mFnDependencyNode_initialShadingGroup.setObject(mObject_initShdGrp) 
	#name = mFnDependencyNode_initialShadingGroup.name() # Result: initialShadingGroup, so it ok so far
	fnSet = OpenMaya.MFnSet(mObject_initShdGrp)
	fnSet.addMember(mMeshShape)
	#cmds.sets(mShapeDagNode.name(), e=True,forceElement='initialShadingGroup')


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

def getVoxels (meshContainer, mVoxelDistance, mBBox, mMeshObj):
	'''
	iterate all the points inside the bounding box and do the
	intersection test with the mesh
	odd intersection times: inside the mesh
	else: outside the mesh
	onlu create voxel inside the mesh
	'''
	voxelCenterPositions=[]
	mHalfVoxelDistance = mVoxelDistance/2

	mMidPoint = OpenMaya.MPoint()
	mMidPoint.x = (mBBox.min().x + mBBox.max().x)/2
	mMidPoint.y = (mBBox.min().y + mBBox.max().y)/2
	mMidPoint.z = (mBBox.min().z + mBBox.max().z)/2

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
						#createVoxelMesh(meshContainer,raySource,0.49)
						voxelCenterPositions.append(raySource)
		#print len(voxelCenterPositions)
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
					#createVoxelMesh(meshContainer,raySource,0.49)
					voxelCenterPositions.append(raySource)
	'''
	print len(voxelCenterPositions)
	voxelData =voxel()
	voxelData.voxelCenterPositions = voxelCenterPositions
	return voxelData



def getBoundingBox (mMeshObj):

	mPointArray = OpenMaya.MPointArray ()
	mMeshObj.getPoints (mPointArray, OpenMaya.MSpace.kTransform)
	BBox = OpenMaya.MBoundingBox()
	for i in range(mPointArray.length()):
		BBox.expand (mPointArray[i])
	return BBox 


mSelectionlist = OpenMaya.MSelectionList()
OpenMaya.MGlobal.getActiveSelectionList(mSelectionlist)
mDagPath = OpenMaya.MDagPath()
selectObj = OpenMaya.MObject()

if mSelectionlist.length() > 0:
	print 'select something'
	mSelectionlist.getDependNode(0,selectObj)
	mSelectionlist.getDagPath(0,mDagPath)

	mFnMesh = OpenMaya.MFnMesh(mDagPath)
	BBox = OpenMaya.MBoundingBox()
	BBox = getBoundingBox (mFnMesh) 
	voxelData = voxel()
	meshContainer = OpenMaya.MObject()
	#meshContainer = createMeshContainer()
	voxelData = getVoxels (meshContainer,0.21, BBox, mFnMesh)
	voxelCenterPositions = voxelData.voxelCenterPositions
	#for i in range(len(voxelCenterPositions)):
	createVoxelMesh(meshContainer,voxelCenterPositions,0.2)

else:
	print 'no mesh is selected'






