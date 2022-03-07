# !/usr/bin/env python
# -*- coding: utf-8 -*-

from types import BuiltinFunctionType
from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QPushButton, QWidget, QVBoxLayout, QGridLayout, QStackedLayout
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from numpy import positive, random, select
import matplotlib.pyplot as plt
import open3d as o3d
import pandas as pd
import numpy as np
import ipdb
from glob import glob
import os
from os import read
from pathlib import Path

from vtkmodules.vtkIOGeometry import (
    vtkBYUReader,
    vtkOBJReader,
    vtkSTLReader
)
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

class QDoublePushButton(QPushButton):
    doubleClicked = pyqtSignal()
    clicked = pyqtSignal()

    def __init__(self, label, *args, **kwargs):
        QPushButton.__init__(self, *args, **kwargs)
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.clicked.emit)
        self.label = label
        super().clicked.connect(self.checkDoubleClick)

    @pyqtSlot()
    def checkDoubleClick(self):
        if self.timer.isActive():
            self.doubleClicked.emit()
            self.timer.stop()
        else:
            self.timer.start(250)


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


def vis_mesh(mesh_path):
    reader = vtkOBJReader()
    reader.SetFileName(mesh_path)
    reader.Update()
    outputPolyData= reader.GetOutput()
    # outputPolyData = ReadPolyData('/Users/zhudaiyi/project/mesh_display/mesh_lod_2_new/mesh_53475934.obj')

    mapper = vtkPolyDataMapper()
    mapper.SetInputData(outputPolyData)
    # self._mesh.SetMapper(mapper)
    actor = vtkActor()
    actor.SetMapper(mapper)
    # self._mesh.SetMapper(mapper)
    renderer = vtkRenderer()
    return renderer, actor


class VtkPointCloudCanvas(QWidget):
    def __init__(self, *args, **kwargs):
        super(VtkPointCloudCanvas, self).__init__(*args, **kwargs)

        self.desktop = QApplication.desktop()
        self.screenRect = self.desktop.screenGeometry()
        self.screenheight = self.screenRect.height()
        self.screenwidth = self.screenRect.width()
        print("窗口大小:", self.screenheight)
        print("窗口大小:", self.screenwidth)

        self.layout=QGridLayout(self)
        self.leftfuck=QWidget(self)     #空物体
        self.leftfuck.setFixedSize(self.screenwidth / 3, 200)

        self.rightfuck=QWidget(self)    #空物体

        self.right=QWidget(self)  

        self.left=QVBoxLayout(self)     #左侧菜单栏垂直布局
        self._layout=QVBoxLayout()      #右侧
        self._layout_1=QVBoxLayout() 
        self.grid = QGridLayout() 
        # self.grid = QVBoxLayout() 
        self.setLayout(self.grid) 
        # self.setLayout(self._layout)
        # self.addLayout
        self.txt_1 = vtk.vtkTextActor()
        self.txt_2 = vtk.vtkTextActor()
        self.txt_3 = vtk.vtkTextActor()
        self.txt_4 = vtk.vtkTextActor()
        self.key_leftTop = vtk.vtkTextActor()
        self.key_leftBottom = vtk.vtkTextActor()
        self.key_rightTop = vtk.vtkTextActor()
        self.key_rightBottom = vtk.vtkTextActor()

        self._vtk_widget = QVTKRenderWindowInteractor(self)
        self.grid.addWidget(self._vtk_widget, 0, 0)
        # self.move(1000, 1000)

        self._vtk_widget_base = QVTKRenderWindowInteractor(self)
        self.grid.addWidget(self._vtk_widget_base, 1, 0)


        # add for mesh
        # self.addLayout(self._layout_1)
        self._vtk_widget_mesh = QVTKRenderWindowInteractor(self)
        self.grid.addWidget(self._vtk_widget_mesh, 0, 1)

        self._vtk_widget_mesh_base = QVTKRenderWindowInteractor(self)
        self.grid.addWidget(self._vtk_widget_mesh_base, 1, 1)
        # ---------------------------------------------------------------
        self.setGeometry(0, 0, self.screenwidth , self.screenheight)



        self.data = None
        self.color = None
        self.prevBtn = None
        self.prevBtnBase = None
        

        ## add button 
        # csv_path = r"C:\Users\71011\Downloads\pos_key.csv"
        csv_path = "/Users/daiyi.zhu/project/vtk_show/mesh_display/pos_key.csv"
        # csv_path = ''
        self.drawTSNE(csv_path)

        self._render = vtk.vtkRenderer()
        self._vtk_widget.GetRenderWindow().AddRenderer(self._render)
        self._iren = self._vtk_widget.GetRenderWindow().GetInteractor()

        self._render_base = vtk.vtkRenderer()
        self._vtk_widget_base.GetRenderWindow().AddRenderer(self._render_base)
        self._iren_base = self._vtk_widget_base.GetRenderWindow().GetInteractor()
        
        #----------------------------------------------------------------------------
        self._render_mesh = vtk.vtkRenderer()


        self._vtk_widget_mesh.GetRenderWindow().AddRenderer(self._render_mesh)
        self._iren_mesh = self._vtk_widget_mesh.GetRenderWindow().GetInteractor()
        
        self._render_mesh_base = vtk.vtkRenderer()

        self._vtk_widget_mesh_base.GetRenderWindow().AddRenderer(self._render_mesh_base)
        self._iren_mesh_base = self._vtk_widget_mesh_base.GetRenderWindow().GetInteractor()
        #----------------------------------------------------------------------------


        self._point_cloud = VtkPointCloud()
        self._point_cloud_base = VtkPointCloud(flag='g')
        self._mesh = vtkRenderer()
        self._mesh_base = vtkRenderer()


        self._render.AddActor(self._point_cloud.vtkActor)
        self._render_base.AddActor(self._point_cloud_base.vtkActor)


        self.rightfuck.setLayout(self.grid)
        self.layout.addWidget(self.leftfuck,0,0)
        self.layout.addWidget(self.rightfuck,0,1,1,2)

        

        self.show()
        self._iren.Initialize()
        self._iren_base.Initialize()
        self._iren_mesh.Initialize()
        self._iren_mesh_base.Initialize()

    def addBtn(self, path, label, key ,x, y, w, h):
        btn1 = QDoublePushButton(label, path, self)
        print(label)
        btn1.setStyleSheet("background-color:rgb({},{},{})".format(self.color[label][0]*255, self.color[label][1]*255, self.color[label][2]*255))
        btn1.setGeometry(x,y,w,h)
    
        label_map = {0:5, 1:0, 2:2, 3:4, 4:3, 5:1}
        btn1.clicked.connect(lambda: self.drawPointCloud(path, label_map[label], key))
        btn1.doubleClicked.connect(lambda: self.drawPointCloud_base(path, label_map[label], key))

        point_id = path.split('/')[-1].split('.')[0].split('_')[1] + '.obj'
        
    def changeColor(self, object, r=1, g=0, b=0):
        if self.prevBtn:
            label = self.prevBtn.label
            # print(label)
            self.prevBtn.setStyleSheet("background-color:rgb({},{},{})".format(self.color[label][0]*255, self.color[label][1]*255, self.color[label][2]*255))
        object.setStyleSheet("background-color:rgb({},{},{})".format(r*255, g*255, b*255))
        
    def changeColorBase(self, object, r=0, g=1, b=0):
        if self.prevBtnBase:
            labels = self.prevBtnBase.label
            self.prevBtnBase.setStyleSheet("background-color:rgb({},{},{})".format(self.color[labels][0]*255, self.color[labels][1]*255, self.color[labels][2]*255))
        object.setStyleSheet("background-color:rgb({},{},{})".format(r*255, g*255, b*255))

    def drawPointCloud(self, file, label, key):
        point_id = file.split('/')[-1].split('.')[0].split('_')[1] + '.obj'
        mesh_path = "/Users/daiyi.zhu/project/vtk_show/mesh_display/mesh_lod_2_new/mesh_" + point_id

        self._point_cloud.clearPoints()
        bu = self.sender()
        if isinstance(bu, QPushButton):
            self.changeColor(bu)
            self.prevBtn = bu
            # self.lbl.setText('%s is pressed' % bu.text())
            f = open(bu.text(), 'r')
            lines = f.readlines()
            for line in lines:
                strpoint = line.strip().split(',')
                point = [float(i) for i in strpoint]
                self._point_cloud.addPoint(point)
            f.close()
            corr = self._vtk_widget.GetRenderWindow().GetSize()

            self.key_leftTop.SetInput(str(key))
            txtprop = self.key_leftTop.GetTextProperty()
            txtprop.SetFontFamilyToArial()
            txtprop.SetFontSize(int(30 / 1440 * self.screenwidth))
            txtprop.SetColor(1, 1, 0)
            self.key_leftTop.SetDisplayPosition(0, 0)
            self._render.AddActor(self.key_leftTop)

            self.txt_1.SetInput(str(label))
            txtprop = self.txt_1.GetTextProperty()
            txtprop.SetFontFamilyToArial()
            txtprop.SetFontSize(int(30 / 1440 * self.screenwidth))
            txtprop.SetColor(0, 1, 0)
            
            self.txt_1.SetDisplayPosition(int(corr[0] * 0.8), int(corr[1] * 0.8))
            # self.txt.SetDisplayPosition(int(100 / 1440 * self.screenwidth) , int(100 / 900 * self.screenheight))
            self._render.AddActor(self.txt_1)

            self._vtk_widget.GetRenderWindow().Render()
        else:
            pass
        if os.path.exists(mesh_path):
          renderer, actor = vis_mesh(mesh_path)
          
          self.key_rightTop.SetInput(str(key))
          txtprop = self.key_rightTop.GetTextProperty()
          txtprop.SetFontFamilyToArial()
          txtprop.SetFontSize(int(30 / 1440 * self.screenwidth))
          txtprop.SetColor(1, 1, 0)
          self.key_rightTop.SetDisplayPosition(0, 0)
          renderer.AddActor(self.key_rightTop)


          self.txt_3.SetInput(str(label))
          txtprop = self.txt_3.GetTextProperty()
          txtprop.SetFontFamilyToArial()
          # txtprop.SetFontSize(60)
          txtprop.SetFontSize(int(30 / 1440 * self.screenwidth))
          txtprop.SetColor(0, 1, 0)
          corr = self._vtk_widget.GetRenderWindow().GetSize()

          self.txt_3.SetDisplayPosition(int(corr[0] * 0.8), int(corr[1] * 0.8))

          self._vtk_widget_mesh.GetRenderWindow().AddRenderer(renderer)
          renderer.AddActor(actor)
          renderer.AddActor(self.txt_3)
          self._vtk_widget_mesh.GetRenderWindow().Render()
          self._vtk_widget_mesh.Start()
    
    def drawPointCloud_base(self, file, label, key):
        point_id = file.split('/')[-1].split('.')[0].split('_')[1] + '.obj'
        mesh_path = "/Users/daiyi.zhu/project/vtk_show/mesh_display/mesh_lod_2_new/mesh_" + point_id
        self._point_cloud_base.clearPoints()
        bu = self.sender()
        if isinstance(bu, QPushButton):
            self.changeColorBase(bu)
            self.prevBtnBase = bu
            # self.lbl.setText('%s is pressed' % bu.text())
            f = open(bu.text(), 'r')
            lines = f.readlines()
            for line in lines:
                strpoint = line.strip().split(',')
                point = [float(i) for i in strpoint]
                self._point_cloud_base.addPoint(point)
            f.close()

            self.key_leftBottom.SetInput(str(key))
            txtprop = self.key_leftBottom.GetTextProperty()
            txtprop.SetFontFamilyToArial()
            txtprop.SetFontSize(int(30 / 1440 * self.screenwidth))
            txtprop.SetColor(1, 1, 0)
            self.key_leftBottom.SetDisplayPosition(0, 0)
            self._render_base.AddActor(self.key_leftBottom)



            self.txt_2.SetInput(str(label))
            txtprop = self.txt_2.GetTextProperty()
            txtprop.SetFontFamilyToArial()
            # txtprop.SetFontSize()
            txtprop.SetFontSize(int(30 / 1440 * self.screenwidth))
            txtprop.SetColor(0, 1, 0)
            corr = self._vtk_widget.GetRenderWindow().GetSize()
            self.txt_2.SetDisplayPosition(int(corr[0] * 0.8), int(corr[1] * 0.8))
   
            self._render_base.AddActor(self.txt_2)

            self._vtk_widget_base.GetRenderWindow().Render()
        else:
            pass
        if os.path.exists(mesh_path):

            reader = vtkOBJReader()

            renderer, actor = vis_mesh(mesh_path)
            self.key_rightBottom.SetInput(str(key))
            txtprop = self.key_rightBottom.GetTextProperty()
            txtprop.SetFontFamilyToArial()
            txtprop.SetFontSize(int(30 / 1440 * self.screenwidth))
            txtprop.SetColor(1, 1, 0)
            self.key_rightBottom.SetDisplayPosition(0, 0)
            renderer.AddActor(self.key_rightBottom)



            self.txt_4.SetInput(str(label))
            txtprop = self.txt_4.GetTextProperty()
            txtprop.SetFontFamilyToArial()
            # txtprop.SetFontSize(60)
            txtprop.SetFontSize(int(30 / 1440 * self.screenwidth))
            txtprop.SetColor(0, 1, 0)
            corr = self._vtk_widget.GetRenderWindow().GetSize() 
            self.txt_4.SetDisplayPosition(int(corr[0] * 0.8), int(corr[1] * 0.8))

            self._vtk_widget_mesh_base.GetRenderWindow().AddRenderer(renderer)
            renderer.AddActor(actor)
            renderer.AddActor(self.txt_4)
            self._vtk_widget_mesh_base.GetRenderWindow().Render()
            self._vtk_widget_mesh_base.Start()
        
    def drawTSNE(self, csv_path, cluster_num=7):
        if self.data is None:
            self.data = pd.read_csv(csv_path)
        if self.color is None:
            colormap = [0.993248, 0.906157, 0.143936, 1.]
            colormaps = []
            for i in range(cluster_num):
                colormaps.append(colormap)
            colormaps = [
                [0.836826, 0.628025 ,0.750174, 1.],
                [0.567714, 0.972084, 0.447227, 1.],
                [0.661374, 0.057462, 0.454453, 1.],
                [0.554984, 0.541288, 0.409172, 1.],
                [0.641581, 0.571686, 0.939694, 1.],
                [0.265209, 0.583503, 0.614333, 1.],
                [0.690667, 0.600293, 0.204797, 1.],
            ]
            self.color = np.array(colormaps)
        mesh_list = glob(os.path.join("./mesh_lod_2_new", '*.obj'))
        for i in zip(self.data['0'], self.data['1'], self.data['key'], self.data['labels']):
            x, y, key, labels = i
            # label.append(labels)
            # ipdb.set_trace()
            # path = r"E:\google_segmeation\all_data_128nm_point_txt\cluster3\cluster3_{}.txt".format(key)
            
            path = "/Users/daiyi.zhu/project/vtk_show/mesh_display/point_cloud_data_256nm/all_data_256nm_point_txt/cluster3/cluster3_{}.txt".format(key)
            self.addBtn(path, labels, key, x * 400 / 900 * self.screenheight, y * 650 / 1440 * self.screenwidth, 10, 10)

if __name__ == '__main__':
    
    from PyQt5.QtWidgets import QApplication
    import sys
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    window = VtkPointCloudCanvas()

    sys.exit(app.exec_())
