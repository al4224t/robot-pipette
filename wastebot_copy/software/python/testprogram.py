import os
import sys
import inspect
import time
import csv
import numpy as np
import datetime
import subprocess 

# OpenCV for image acquistion from webcan and subsequent analysis
#import cv2

# load Experiment1 procedures module, which will allow access to all general
# procedure functions and those from Experiment1
from procedures.procedures import Experiment1
from procedures.procedures import DummyExperiment
# add root path to access project modules
HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(HERE_PATH)

#allowed communication with R
#from scipy.integrate import odeint
#from matplotlib import pyplot as plt

#import for boxplot
import string
#import plotly.plotly as py
#import plotly.graph_objs as go

#from mpl_toolkits.mplot3d import Axes3D # for 3d plot
#% matplotlib inline
#import pandas as pd
#import seaborn as sns
#sns.set()
#sns.set_context("poster")
#sns.set_style("whitegrid")

## dynamic plot
#from ipywidgets import widgets, Button, Layout
#from IPython.display import display

## import packages to communicate with R
#from numpy import *
#import scipy as sp
#from pandas import *
#from rpy2.robjects.packages import importr
#import rpy2.robjects as ro
#import pandas.rpy.common as com

#%load_ext rpy2.ipython
#from rpy2.robjects import r, pandas2ri
#from rpy2 import robjects
#from rpy2.robjects.packages import importr

## import ggplot (python package)
#from ggplot import *

# import R packages

#d = {'package.dependencies': 'package_dot_dependencies',
#     'package_dependencies': 'package_uscore_dependencies'}

#from rpy2.robjects.packages import importr
#base = importr('base')
#utils = importr('utils')
#gc = importr('growthcurver')
#plyr = importr('plyr')
#ggplot2 = importr('ggplot2')
#reshape2 = importr('reshape2')
#dat_tab = importr('data.table')
#stats = importr('stats', robject_translations = d)
#from rpy2.robjects import pandas2ri
#pandas2ri.activate()

###########################

# create general procedures object, no need to link configfiles
# this initializes all parts of the robot
exp1 = DummyExperiment(robot_configfile="robot/robot_config.json")

# define initial position for X,Y,Z
init_x = 0
init_y = 0
init_z = 50
# pitch between wells cf. http://ibidi.com/xtproducts/en/ibidi-Labware/m-Plates/m-Plate-24-Well
well_pitch = 19.30 

###########
##################

#exp1.robot.move_to([0, 0, init_z])
#exp1.robot.move_to([0, 0, 100])
#exp1.robot.move_to([0, 0, 0])
#exp1.robot.p.aspirate(1000)
#time.sleep(15)
#exp1.robot.p.dispense(300)
#time.sleep(5)
#exp1.robot.p.dispense(300)
#time.sleep(5)
#exp1.robot.p.dispense(300)
#time.sleep(5)
#exp1.robot.p.home()

exp1.robot.s.rotate(720)
exp1.robot.s.speed(90)
exp1.robot.s.acceleration(90)
exp1.robot.s.rotate(720)
exp1.robot.s.speed(360)
exp1.robot.s.acceleration(360)
exp1.robot.s.rotate(800)
exp1.robot.s.zero()