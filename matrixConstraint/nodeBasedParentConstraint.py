"""
http://bindpose.com/maya-matrix-based-functions-part-1-node-based-matrix-constraint/
"""

import pymel.core as pm


def nodeBasedParentConstraint(driverNode, drivenNode, maintainOffset=True):
    driverNodePN = pm.PyNode(driverNode)
    drivenNodePN = pm.PyNode(drivenNode)
    worldMatrix = driverNodePN.worldMatrix.get()
    print worldMatrix
    # create decompose matrix
    # parentMatrix = drivenNodePN.parentInverseMatrix.get().inverse()
    # localMatrix = worldMatrix * drivenNodePN.parentInverseMatrix.get()
    decomposeMatrixNode = pm.createNode('decomposeMatrix', name='{0}_DPM'.format(driverNode))
    # create mulMatrix
    multMatrixNode = pm.createNode('multMatrix', name='{0}_MM'.format(driverNode))

    if maintainOffset:
        offsetMatrix = drivenNodePN.worldMatrix.get() * driverNodePN.worldMatrix.get().inverse()
        multMatrixNode.matrixIn[0].set(offsetMatrix)

        driverNodePN.worldMatrix >> multMatrixNode.matrixIn[1]
        drivenNodePN.parentInverseMatrix >> multMatrixNode.matrixIn[2]
    else:
        driverNodePN.worldMatrix >> multMatrixNode.matrixIn[0]
        drivenNodePN.parentInverseMatrix >> multMatrixNode.matrixIn[1]

    multMatrixNode.matrixSum >> decomposeMatrixNode.inputMatrix

    decomposeMatrixNode.outputTranslate >> drivenNodePN.translate
    decomposeMatrixNode.outputRotate >> drivenNodePN.rotate


if __name__ == '__main__':
    nodeBasedParentConstraint('driverJnt', 'drivenJnt', maintainOffset=True)
