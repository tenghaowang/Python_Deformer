import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMayaFX as OpenMayaFX
import sys



commandName = 'vertexParticle'
kHelpFlag = '-h'
kLongHelpFlag = '-help'
kSparseFlag = '-s'
kSparseLongFlag = '-sparse'

helpMessage = ' This command is used to attach a particle on each vertex of a poly mesh'


class pluginCommand(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)
    sparse=None
    def argumentParser(self, argList):
        syntax = self.syntax()
        try:
            parsedArgments = OpenMaya.MArgDatabase(syntax,argList)
        except:
            return "UnKnown Syntax"
        # short flag
        if parsedArgments.isFlagSet(kSparseFlag):
            self.sparse = parsedArgments.flagArgumentDouble(kSparseFlag,0)
            return 
            # return OpenMaya.MStatus.KSuccess
        if parsedArgments.isFlagSet(kSparseLongFlag):
            self.sparse = parsedArgments.flagArgumentDouble(kSparseLongFlag,0)
            return 
            # return OpenMaya.MStatus.KSucce
        if parsedArgments.isFlagSet(kHelpFlag):
            self.setResult(helpMessage)
            print 'Helpmessage'
            return  
        if parsedArgments.isFlagSet(kSparseLongFlag):
            self.setResult(helpMessage)
            return

    def isUndoable(self):
        return True

    def undoIt(self):
        print 'undo'
        MDagMod = OpenMaya.MDagModifier()
        #need to delete parent Node
        mDagNode=OpenMaya.MFnDagNode(self.mObj_particle)
        MDagMod.deleteNode(mDagNode.parent(0))
        MDagMod.doIt()
        return 


    def redoIt(self):
        counter=0
        mSel=OpenMaya.MSelectionList()
        mDagPath=OpenMaya.MDagPath()
        mFnMesh=OpenMaya.MFnMesh()
        OpenMaya.MGlobal.getActiveSelectionList(mSel)
        if mSel.length()>0:
            try:
                mSel.getDagPath(0,mDagPath)
                mFnMesh.setObject(mDagPath)
            except:
                print "select a poly mesh"
                return 
        else:
            print 'select a poly mesh'
            return 

        mPointArray=OpenMaya.MPointArray()
        mFnMesh.getPoints(mPointArray,OpenMaya.MSpace.kWorld)
        print mFnMesh.name()
        print mPointArray.length()
        # create a particle system
        mFnParticle = OpenMayaFX.MFnParticleSystem()
        self.mObj_particle = mFnParticle.create()
        # fix some bug issue
        mFnParticle=OpenMayaFX.MFnParticleSystem(self.mObj_particle)
        for i in xrange(mPointArray.length()):
            if i%self.sparse==0:
                mFnParticle.emit(mPointArray[i])
                counter+=1
        print 'Total Points:' + str(counter)
        mFnParticle.saveInitialState()
        return

    def doIt(self, argList):
        self.argumentParser(argList)
        if self.sparse!=None:
            self.redoIt()


def cmdCreator():
    return OpenMayaMPx.asMPxPtr(pluginCommand())

def syntaxCreator():
    # create Msyntax object
    syntax= OpenMaya.MSyntax()

    # collect/add the flags
    syntax.addFlag(kHelpFlag,kLongHelpFlag)
    syntax.addFlag(kSparseFlag,kSparseLongFlag,OpenMaya.MSyntax.kDouble)

    # return syntax
    return syntax



def initializePlugin(mObject):
    mplugin = OpenMayaMPx.MFnPlugin(mObject)
    try:
        mplugin.registerCommand(commandName, cmdCreator,syntaxCreator)
    except:
        sys.stderr.write('Failed to register command: %s/n'  %commandName)


def uninitializePlugin(mObject):
    mplugin = OpenMayaMPx.MFnPlugin(mObject)
    try:
        mplugin.deregisterCommand(commandName)
    except:
        sys.stderr.write('Failed to deregisterCommand: %s/n'  %scommandName)


