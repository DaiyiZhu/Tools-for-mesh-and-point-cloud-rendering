# from os import read
from glob import glob
import os 
from pathlib import Path
import vtk

from vtkmodules.vtkIOGeometry import (
    vtkBYUReader,
    vtkOBJReader,
    vtkSTLReader
)
# from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor 
from vtkmodules.vtkIOLegacy import vtkPolyDataReader
from vtkmodules.vtkIOPLY import vtkPLYReader
from vtkmodules.vtkIOXML import vtkXMLPolyDataReader
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import (
    vtkLookupTable,
    vtkMinimalStandardRandomSequence,
    vtkPoints,
    vtkUnsignedCharArray
)
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkFiltersCore import vtkDelaunay2D
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)
import sys
import random
from PyQt5.QtWidgets import QApplication
import argparse

class VtkPointCloud:
    def __init__(self, zMin=-10.0, zMax=10.0, maxNumPoints=1e6, flag='r'):
        self.maxNumPoints = maxNumPoints
        self.flag = flag
        self.vtkPolyData = vtk.vtkPolyData()
        self.colors = vtkNamedColors()
        self.Colors = vtkUnsignedCharArray()
        self.Colors.SetNumberOfComponents(3)
        self.Colors.SetName("Colors")
        self.clearPoints()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(self.vtkPolyData)
        mapper.SetColorModeToDefault()
        mapper.SetScalarRange(zMin, zMax)
        mapper.SetScalarVisibility(1)
        self.vtkActor = vtk.vtkActor()
        self.vtkActor.SetMapper(mapper)

    def addPoint(self, point):
        if self.vtkPoints.GetNumberOfPoints() < self.maxNumPoints:
            pointId = self.vtkPoints.InsertNextPoint(point[:])
            self.vtkDepth.InsertNextValue(point[2])
            self.vtkCells.InsertNextCell(1)
            self.vtkCells.InsertCellPoint(pointId)
            if self.flag == 'r':
                self.Colors.InsertNextTuple3(255, 0, 0)
            else:
                self.Colors.InsertNextTuple3(0, 255, 0)

        else:
            r = random.randint(0, self.maxNumPoints)
            self.vtkPoints.SetPoint(r, point[:])
        self.vtkCells.Modified()
        self.vtkPoints.Modified()
        self.vtkDepth.Modified()

    def clearPoints(self):

        self.vtkPoints = vtk.vtkPoints()
        self.vtkCells = vtk.vtkCellArray()
        self.vtkDepth = vtk.vtkDoubleArray()
        self.vtkDepth.SetName('DepthArray')
        self.vtkPolyData.SetPoints(self.vtkPoints)
        self.vtkPolyData.SetVerts(self.vtkCells)
        self.vtkPolyData.GetPointData().SetScalars(self.vtkDepth)
        self.vtkPolyData.GetPointData().SetActiveScalars('DepthArray')
        self.vtkPolyData.GetPointData().SetScalars(self.Colors)
# list_files = glob(os.path.join("../mesh_lod_2_new/", "*"))

# cnt = 0


with open('./all-test.txt', 'r') as f:
  point_cloud_paths = f.readlines()

parser = argparse.ArgumentParser()
parser.add_argument("--num_type", type=str, default="100", help="")
# parser.add_argument("--type", type=str, default="point", help="mesh or point")
args = parser.parse_args()
# print(opt)


cnt = 0
num_id = [13, 14, 18, 19, 21, 36, 45, 65, 69, \
          72, 85, 105, 119, 215, 261, 287, 334, 340, 341, 376]
num_id = [x - 1 for x in num_id]
# idx = 0
# print(num_id)
for point_cloud_path in point_cloud_paths:
  if cnt not in num_id:
    print(cnt)
    cnt += 1
    continue
  vtk_point_cloud = VtkPointCloud(flag='g')
  point_cloud_path = '/Users/daiyi.zhu/project/vtk_show/mesh_display/point_cloud_data_256nm/all_data_256nm_point_txt/' + point_cloud_path.strip('\n') + '.txt'
  with open(point_cloud_path, 'r') as f:
    point_clouds = f.readlines()
  for point_cloud in point_clouds:
    point_str = point_cloud.strip('\n').split(',')
    point = [float(i) for i in point_str]
    vtk_point_cloud.addPoint(point)
  # cnt = num_id[idx]
  # cnt = idx
  file_name_graph = './debug/debug_num' + str(args.num_type) + '/' + str(cnt) + '_sphere.obj'
  reader_graph = vtkOBJReader()
  reader_graph.SetFileName(file_name_graph)
  reader_graph.Update()
  outputPolyData_graph= reader_graph.GetOutput()
  mapper_graph = vtkPolyDataMapper()
  mapper_graph.SetInputData(outputPolyData_graph)
  actor_graph = vtkActor()
  actor_graph.SetMapper(mapper_graph)
  renderer_graph = vtkRenderer()

  file_name_sphere = './debug/debug_num' + str(args.num_type) + '/' + str(cnt) + '_mesh_graph.obj'
  reader_sphere = vtkOBJReader()
  reader_sphere.SetFileName(file_name_sphere)
  reader_sphere.Update()
  outputPolyData_sphere= reader_sphere.GetOutput()
  mapper_sphere = vtkPolyDataMapper()
  mapper_sphere.SetInputData(outputPolyData_sphere)
  actor_sphere = vtkActor()
  actor_sphere.SetMapper(mapper_sphere)
  renderer_sphere = vtkRenderer()

  file_name_mesh = './debug/debug_num' + str(args.num_type) + '/' + str(cnt) + '_skel_face.obj'
  reader_mesh = vtkOBJReader()
  reader_mesh.SetFileName(file_name_mesh)
  reader_mesh.Update()
  outputPolyData_mesh = reader_mesh.GetOutput()
  mapper_mesh = vtkPolyDataMapper()
  mapper_mesh.SetInputData(outputPolyData_mesh)
  actor_mesh = vtkActor()
  actor_mesh.SetMapper(mapper_mesh)
  renderer_mesh = vtkRenderer()

  file_name_edge = './debug/debug_num' + str(args.num_type) + '/' + str(cnt) + '_skel_edge.obj'
  reader_edge = vtkOBJReader()
  reader_edge.SetFileName(file_name_edge)
  reader_edge.Update()
  outputPolyData_edge = reader_edge.GetOutput()
  mapper_edge = vtkPolyDataMapper()
  mapper_edge.SetInputData(outputPolyData_edge)
  actor_edge = vtkActor()
  actor_edge.SetMapper(mapper_edge)
  # renderer_edge = vtkRenderer()

  renderer = vtkRenderer()
  renderWindow = vtkRenderWindow()
  screenwidth,  screenheight =  renderWindow.GetScreenSize()
  renderWindow.SetSize(2000, 1000)
  # renderWindow.SetSize(screenwidth, screenheight)
  renderWindow.AddRenderer(renderer)
  renderWindow.AddRenderer(renderer_graph)
  renderWindow.AddRenderer(renderer_sphere)
  renderWindow.AddRenderer(renderer_mesh)
  # renderWindow.AddRenderer(renderer_edge)


  renderWindowInteractor = vtkRenderWindowInteractor()
  renderWindowInteractor.SetRenderWindow(renderWindow)


  renderer.AddActor(vtk_point_cloud.vtkActor)

  renderer_graph.AddActor(actor_graph)
  renderer_sphere.AddActor(actor_sphere)
  renderer_mesh.AddActor(actor_mesh)
  renderer_mesh.AddActor(actor_edge)





  renderer.SetViewport(0, 0, 0.25, 1)
  renderer_graph.SetViewport(0.25, 0, 0.5, 1)
  renderer_sphere.SetViewport(0.5, 0, 0.75, 1)
  # renderer_edge.SetViewport(0.75, 0, 1, 1)
  renderer_mesh.SetViewport(0.75, 0, 1, 1)
 

  renderWindow.Render()
  renderWindowInteractor.Start()
  cnt += 1
