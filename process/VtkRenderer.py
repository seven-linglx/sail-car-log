import vtk
from numpy import random
import numpy as np
import vtk.util.numpy_support as converter
import time

def get_vtk_cloud(xyz, intensity, zMin=-10.0,zMax=10.0):
  
  intensity = intensity.copy() # to prevent deallocation problems

  vtkPolyData = vtk.vtkPolyData()
  vtkPoints = vtk.vtkPoints()
  vtkCells = vtk.vtkCellArray()
  vtkDepth = vtk.vtkDoubleArray()
  vtkDepth.SetName('DepthArray')
  vtkPolyData.SetPoints(vtkPoints)
  vtkPolyData.SetVerts(vtkCells)
  vtkPolyData.GetPointData().SetScalars(vtkDepth)
  vtkPolyData.GetPointData().SetActiveScalars('DepthArray')

  num_points = xyz.shape[0]
  
  vtk_data = converter.numpy_to_vtk(xyz)
  vtkPoints.SetNumberOfPoints(num_points)
  vtkPoints.SetData(vtk_data)

  np_cells_A = np.ones(num_points,dtype=np.int64)
  np_cells_B = np.arange(0,num_points,dtype=np.int64)
  np_cells = np.empty(2*num_points,dtype=np.int64)
  np_cells[::2] = np_cells_A
  np_cells[1::2] = np_cells_B

  vtkCells.SetCells(num_points, converter.numpy_to_vtkIdTypeArray(np_cells, deep=1))

  vtkDepth.SetVoidArray(intensity, num_points, 1)

  mapper = vtk.vtkPolyDataMapper()
  mapper.SetInput(vtkPolyData)
  mapper.SetColorModeToDefault()
  mapper.SetScalarRange(zMin, zMax)
  mapper.SetScalarVisibility(1)
  vtkActor = vtk.vtkActor()
  vtkActor.SetMapper(mapper)

  return vtkActor


############# sample callback setup ###############
class vtkTimerCallback():
   def __init__(self):
     pass
 
   def execute(self,obj,event):
     t = time.time()
     data = 40*(random.random((60000,3))-0.5)
     pointCloud = get_vtk_cloud(data, data[:,2])
     iren = obj
     iren.GetRenderWindow().GetRenderers().GetFirstRenderer().RemoveActor(self.actor)
     iren.GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(pointCloud)
     iren.GetRenderWindow().Render()
     self.actor = pointCloud
     print time.time() - t

if __name__ == '__main__': 

  data = 40*(random.random((600,3))-0.5)
  pointCloud = get_vtk_cloud(data, data[:,2])

  # Renderer
  renderer = vtk.vtkRenderer()
  renderer.AddActor(pointCloud)
  renderer.SetBackground(0.0, 0.0, 0.)
  renderer.ResetCamera()
  
  # Render Window
  renderWindow = vtk.vtkRenderWindow()
  renderWindow.SetSize(600,600)
  renderWindow.AddRenderer(renderer)
  
  # Interactor
  renderWindowInteractor = vtk.vtkRenderWindowInteractor()
  renderWindowInteractor.SetRenderWindow(renderWindow)
  
  # Begin Interaction
  renderWindow.Render()
  renderWindowInteractor.Initialize()
  
  cb = vtkTimerCallback()
  cb.actor = pointCloud
  renderWindowInteractor.AddObserver('TimerEvent', cb.execute)
  timerId = renderWindowInteractor.CreateRepeatingTimer(50)
  
  renderWindowInteractor.Start()
