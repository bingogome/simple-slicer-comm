import vtk, qt, ctk, slicer
import socket, math
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import time
import math

#
# Connections
#

APPLICATION_CATEGORY = "SimpleSlicerComm"
DATA_HOLDER_NAME = "data_temp"

class Connections(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Connections"  # TODO: make this more human readable by adding spaces
    self.parent.categories = [APPLICATION_CATEGORY]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["Yihao Liu (Johns Hopkins University)"]  # TODO: replace with "Firstname Lastname (Organization)"
    # TODO: update with short description of the module and a link to online module documentation
    self.parent.helpText = """
This is an example of scripted loadable module for connections using UDP. 
"""
    # TODO: replace with organization, grant and thanks
    self.parent.acknowledgementText = """
To be updated
"""

#
# ConnectionsWidget
#

class ConnectionsModuleDataHolder():
  """
  A data class to hold the data needed for this module
  """

  def __init__(self):
    """
    Init class
    """

    # temp data init (uses mrml table for simplicity)
    self._mrml_temp_data = []
    self._temp_data_num = 2
    # Document what are these used for:
    # self._mrml_temp_data[0] is the received data buffer
    # self._mrml_temp_data[0] is the sending buffer

    # May need more than one
    for i in range(self._temp_data_num):
      self._mrml_temp_data.append(slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode"))
    for i in self._mrml_temp_data:
      i.SetHideFromEditors(True)
      i.GetLocked=True

  def clear(self):
    """
    Clear data
    """

    # data clear
    for i in self._mrml_temp_data:
      slicer.mrmlScene.RemoveNode(i)

class ConnectionsModuleSocketHolder():
  """
  A class to hold the sockets needed for this module
  """

  def __init__(self):
    """
    Init class
    """

    # port init
    self._sock_ip = "localhost"
    self._flag_receiving = False
    self._flag_disconnected = True # ports are disconnected
    self._sock_receive = None
    self._sock_send = None

  def setup(self):
    self._sock_receive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self._sock_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # set buffer size to 1 if want data to be time sensitive
    self._sock_receive.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1)

  def clear(self):
    """
    Clear data and ports
    """
    # port clear
    self._flag_disconnected = True
    self._flag_receiving = False

    if self._sock_receive:
      self._sock_receive.close()
    if self._sock_send:
      self._sock_send.close()

class ConnectionsWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent=None):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)  # needed for parameter node observation
    self.logic = None
    self._parameterNode = None
    self._updatingGUIFromParameterNode = False
    self._data = ConnectionsModuleDataHolder()
    self._socks = ConnectionsModuleSocketHolder()

  def setup(self):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.setup(self)

    # Load widget from .ui file (created by Qt Designer).
    # Additional widgets can be instantiated manually and added to self.layout.
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/Connections.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
    # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
    # "setMRMLScene(vtkMRMLScene*)" slot.
    uiWidget.setMRMLScene(slicer.mrmlScene)

    # Create logic class. Logic implements all computations that should be possible to run
    # in batch mode, without a graphical user interface.
    self.logic = ConnectionsLogic()

    # Connections

    # These connections ensure that we update parameter node when scene is closed
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

    # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
    # (in the selected parameter node).
    self.ui.receive_port_widget.connect("textChanged(QString)", self.updateParameterNodeFromGUI)
    self.ui.send_port_widget.connect("textChanged(QString)", self.updateParameterNodeFromGUI)

    # Buttons
    # TODO connect
    self.ui.connect_button.connect('clicked(bool)', self.onConnectButton)
    self.ui.disconnect_button.connect('clicked(bool)', self.onDisconnectButton)

    # Make sure parameter node is initialized (needed for module reload)
    self.initializeParameterNode()

  def cleanup(self):
    """
    Called when the application closes and the module widget is destroyed.
    """
    self.removeObservers()
    self._data.clear()
    self._socks.clear()

  def enter(self):
    """
    Called each time the user opens this module.
    """
    # Make sure parameter node exists and observed
    self.initializeParameterNode()

  def exit(self):
    """
    Called each time the user opens a different module.
    """
    # Do not react to parameter node changes (GUI wlil be updated when the user enters into the module)
    self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

  def onSceneStartClose(self, caller, event):
    """
    Called just before the scene is closed.
    """
    # Parameter node will be reset, do not use it anymore
    self.setParameterNode(None)

  def onSceneEndClose(self, caller, event):
    """
    Called just after the scene is closed.
    """
    # If this module is shown while the scene is closed then recreate a new parameter node immediately
    if self.parent.isEntered:
      self.initializeParameterNode()

  def initializeParameterNode(self):
    """
    Ensure parameter node exists and observed.
    """
    # Parameter node stores all user choices in parameter values, node selections, etc.
    # so that when the scene is saved and reloaded, these settings are restored.

    self.setParameterNode(self.logic.getParameterNode())

  def setParameterNode(self, inputParameterNode):
    """
    Set and observe parameter node.
    Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
    """

    if inputParameterNode:
      self.logic.setDefaultParameters(inputParameterNode)

    # Unobserve previously selected parameter node and add an observer to the newly selected.
    # Changes of parameter node are observed so that whenever parameters are changed by a script or any other module
    # those are reflected immediately in the GUI.
    if self._parameterNode is not None:
      self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
    self._parameterNode = inputParameterNode
    if self._parameterNode is not None:
      self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

    # Initial GUI update
    self.updateGUIFromParameterNode()

  def updateGUIFromParameterNode(self, caller=None, event=None):
    """
    This method is called whenever parameter node is changed.
    The module GUI is updated to show the current state of the parameter node.
    """

    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return

    # Make sure GUI changes do not call updateParameterNodeFromGUI (it could cause infinite loop)
    self._updatingGUIFromParameterNode = True

    # Update node selectors and sliders
    self.ui.receive_port_widget.text = str(self._parameterNode.GetParameter("ReceivePort"))
    self.ui.send_port_widget.text = str(self._parameterNode.GetParameter("SendPort"))

    # Update buttons states and tooltips
    if self._parameterNode.GetParameter("ReceivePort") \
        and self._parameterNode.GetParameter("SendPort") \
        and self._socks._flag_disconnected:
      self.ui.connect_button.toolTip = "Connect"
      self.ui.connect_button.enabled = True
    else:
      self.ui.connect_button.toolTip = "Select ports"
      self.ui.connect_button.enabled = False

    if not self._socks._flag_disconnected:
      self.ui.disconnect_button.enabled = True
    else:
      self.ui.disconnect_button.enabled = False

    # All the GUI updates are done
    self._updatingGUIFromParameterNode = False

  def updateParameterNodeFromGUI(self, caller=None, event=None):
    """
    This method is called when the user makes any change in the GUI.
    The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
    """

    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return

    wasModified = self._parameterNode.StartModify()  # Modify all properties in a single batch

    self._parameterNode.SetParameter("ReceivePort", int(self.ui.receive_port_widget.text))
    self._parameterNode.SetParameter("SendPort", int(self.ui.send_port_widget.text))

    self._parameterNode.EndModify(wasModified)

  def onConnectButton(self):
    self._socks.setup()
    self._socks._sock_receive.bind((self._socks._sock_ip, int(self._parameterNode.GetParameter("ReceivePort"))))
    # self._socks._sock_receive.settimeout(0.1/1000)
    self._socks._sock_receive.setblocking(0)
    self._socks._flag_receiving = True
    self._socks._flag_disconnected = False

    self.ui.connect_button.enabled = False
    self.ui.disconnect_button.enabled = True

    print("Ports Connected")

    self.transformMatrix, self.transformNode = self.logic.testInitTransf()

    self.runningSockets()

  def onDisconnectButton(self):
    self._socks._flag_receiving = False
    self._socks._flag_disconnected = True
    self.ui.disconnect_button.enabled = False
    self.ui.connect_button.enabled = True
    print("Ports Disconnected")
    self._socks.clear()

  def runningSockets(self):
    # print("Ports Start Receiving and Sending Buffered Data")
    if self._socks._flag_receiving:
      try:
        # data = self._socks._sock_receive.recvfrom(216)
        data = self._socks._sock_receive.recv(216)
        self.logic.handleReceivedData(data, self.transformMatrix,self.transformNode)
        qt.QTimer.singleShot(1, self.runningSockets)
      except:
        qt.QTimer.singleShot(1, self.runningSockets)

      
#
# ConnectionsLogic
#

class ConnectionsLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self):
    """
    Called when the logic class is instantiated. Can be used for initializing member variables.
    """
    ScriptedLoadableModuleLogic.__init__(self)

  def setDefaultParameters(self, parameterNode):
    """
    Initialize parameter node with default settings.
    """
    if not parameterNode.GetParameter("ReceivePort"):
      parameterNode.SetParameter("ReceivePort", "8059")
    if not parameterNode.GetParameter("SendPort"):
      parameterNode.SetParameter("SendPort", "8051")
      

  def testInitTransf(self):
    transformMatrix = vtk.vtkMatrix4x4()
    transformMatrix.SetElement(0,0,1)
    transformMatrix.SetElement(0,1,0)
    transformMatrix.SetElement(0,2,0)
    transformMatrix.SetElement(1,0,0)
    transformMatrix.SetElement(1,1,1)
    transformMatrix.SetElement(1,2,0)
    transformMatrix.SetElement(2,0,0)
    transformMatrix.SetElement(2,1,0)
    transformMatrix.SetElement(2,2,1)
    transformMatrix.SetElement(0,3,0)
    transformMatrix.SetElement(1,3,0)
    transformMatrix.SetElement(2,3,0)

    coilPose = slicer.mrmlScene.GetFirstNodeByName("coilpose.STL")
    transformNode = slicer.vtkMRMLTransformNode()
    slicer.mrmlScene.AddNode(transformNode)
    coilPose.SetAndObserveTransformNodeID(transformNode.GetID())
    transformNode.SetMatrixTransformToParent(transformMatrix)
    slicer.app.processEvents()
    return transformMatrix, transformNode


  def handleReceivedData(self, data, transformMatrix, transformNode):
    """
    Received data bytes and process it
    """

    data = data.decode("utf-8")
    if data.startswith("_transf___", 0,10):
      data = data[10:]
      p = data.split("_")
      pp = float(p[0])
      print(transformMatrix)
      transformMatrix.SetElement(1,3, math.sin(3 * pp)*10)
      transformMatrix.SetElement(2,3, math.sin(3 * pp)*10)
      transformNode.SetMatrixTransformToParent(transformMatrix)
      slicer.app.processEvents()
    
    
