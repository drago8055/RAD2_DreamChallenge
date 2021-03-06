# -*- coding: utf-8 -*-
"""regression_model_H.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1JWvBU_kEfJqRWiVjjm5RPsALxMMt9M90
"""

import numpy as np
import os
import json
import cv2
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Lasso
from sklearn.metrics import mean_squared_error
from skimage.feature import hog
from sklearn.externals import joblib

from google.colab import drive
drive.mount('/content/drive')

# from google.colab import drive
# drive.mount('/content/drive')

PATH_image = '/content/drive/My Drive/Independent-Prj/train/'
PATH_box_embedding = '/content/drive/My Drive/Independent-Prj/box_embeddings_H/'

def get_cordinates(shape, bb):
    cx = int(round(bb[0]*shape[1]))
    cy = int(round(bb[1]*shape[0]))
    w = int(round(bb[2]*shape[1]))
    h = int(round(bb[3]*shape[0]))
    xmin = int(cx-w/2)
    xmax = int(cx+w/2)
    ymin = int(cy-h/2)
    ymax = int(cy+h/2)
    return [xmin,ymin,xmax,ymax]

def illum_correct(image):
    lab = cv2.cvtColor(image,cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl_image = clahe.apply(l)
    img1 = cv2.merge((cl_image,a,b))
    output_image = cv2.cvtColor(img1, cv2.COLOR_LAB2RGB)
    return output_image

def preprocess_img(image):
    gamma=0.8
    image_on_denoise = cv2.fastNlMeansDenoisingColored(image,None,9,9,7,21)
    illum_correct_image=illum_correct(image_on_denoise)
    gamma_corrected = np.array(255*(illum_correct_image / 255) ** gamma, dtype = 'uint8')
    return gamma_corrected

def color_hog_f(image):
    R=image[:,:,2]
    G=image[:,:,1]
    B=image[:,:,0]
    hist_R =hog(R,orientations=9,pixels_per_cell=(8,8),cells_per_block=(3,3))
    hist_G=hog(G,orientations=9,pixels_per_cell=(8,8),cells_per_block=(3,3))
    hist_B=hog(B,orientations=9,pixels_per_cell=(8,8),cells_per_block=(3,3))
    temp1=[]
    temp2=[]
    temp3=[]
    for j in range(len(hist_R)):
        temp1.append(hist_R[j])
        temp2.append(hist_G[j])
        temp3.append(hist_B[j])
    return temp3+temp2+temp1

def feature_extraction(image):
    hog_f = color_hog_f(image)
    rgb_f = image.flatten()
    return rgb_f

#Object Labels for LH and RH
label_LH = ['LH_mcp_E__ip', 'LH_pip_E__2', 'LH_pip_E__3', 'LH_pip_E__4', 'LH_pip_E__5', 
             'LH_mcp_E__1', 'LH_mcp_E__2', 'LH_mcp_E__3', 'LH_mcp_E__4', 'LH_mcp_E__5', 'LH_wrist_E__mc1', 
             'LH_wrist_E__mul', 'LH_wrist_E__nav', 'LH_wrist_E__lunate', 'LH_wrist_E__radius', 'LH_wrist_E__ulna']

label_RH = ['RH_mcp_E__ip', 'RH_pip_E__2', 'RH_pip_E__3', 'RH_pip_E__4', 'RH_pip_E__5', 
             'RH_mcp_E__1', 'RH_mcp_E__2', 'RH_mcp_E__3', 'RH_mcp_E__4', 'RH_mcp_E__5', 'RH_wrist_E__mc1', 
             'RH_wrist_E__mul', 'RH_wrist_E__nav', 'RH_wrist_E__lunate', 'RH_wrist_E__radius', 'RH_wrist_E__ulna']

img_files = np.load('/content/drive/My Drive/Independent-Prj/image_ids_H.npy')
ids_LH = []
ids_RH = []
for f in img_files:
  if f[7] == 'L':
    ids_LH.append(f[:-4])
  elif f[7] == 'R':
    ids_RH.append(f[:-4])

#Prepare training images
train_images_LH = []
train_images_RH = []
for x in ids_LH:
      train_images_LH.append(x + ".jpg")
for x in ids_RH:
      train_images_RH.append(x + ".jpg")

y_train_all_LH = []
y_train_all_RH = []

df = pd.read_csv('/content/drive/My Drive/Independent-Prj/training.csv')
for x in ids_LH:
    val_1 =(df.loc[df['Patient_ID'] == x[:-3], label_LH]).values.tolist()
    y_train_all_LH.append(val_1)

for x in ids_RH:
    val_2 =(df.loc[df['Patient_ID'] == x[:-3], label_RH]).values.tolist()
    y_train_all_RH.append(val_2)

y_train_all_t_LH = []
y_train_all_t_RH = []
for x in y_train_all_LH:
    y_train_all_t_LH.append(x[0])
y_train_all_t_LH = np.array(y_train_all_t_LH)

for x in y_train_all_RH:
    y_train_all_t_RH.append(x[0])
y_train_all_t_RH = np.array(y_train_all_t_RH)

h = []
w = []
count = 0
outliers_train = []
x_train_LH = []
y_train_LH = []
crp_size = (32, 32)
for i in range(0,len(train_images_LH)):
  x_train_j_LH = []
  y_train_j_LH = []
  for joint in range(0,16):
      img = cv2.imread(PATH_image + train_images_LH[i])
      gray_img = cv2.imread(PATH_image + train_images_LH[i], 0)
      boxes = np.load(PATH_box_embedding + train_images_LH[i][:-4] + '.npy')
      newbb = boxes[joint]
      crop_img = img[newbb[1]:newbb[3], newbb[0]:newbb[2]]
      crop_img = cv2.resize(crop_img,crp_size)
      crop_img = feature_extraction(crop_img)
      x_train_j_LH.append(crop_img)
  if i%60 == 0:
    print("Id:",i,"...Done.")
  x_train_LH.append(x_train_j_LH)

# from google.colab import drive
# drive.mount('/content/drive')

h = []
w = []
count = 0
x_train_RH = []
crp_size = (32, 32)
outliers_RH = []
for i in range(0,len(train_images_RH)):
  x_train_j_RH = []
  for joint in range(0,16):
      img = cv2.imread(PATH_image + train_images_RH[i])
      gray_img = cv2.imread(PATH_image + train_images_RH[i], 0)
      boxes = np.load(PATH_box_embedding + train_images_RH[i][:-4] + '.npy')
      newbb = boxes[joint]
      crop_img = img[newbb[1]:newbb[3], newbb[0]:newbb[2]]
      r, c, ch = crop_img.shape
      if r < 32 or c < 32:
        outliers_RH.append([i, joint])
        x_train_j_RH.append([0]*3072)
      else:
        crop_img = cv2.resize(crop_img,crp_size)
        crop_img = feature_extraction(crop_img)
        x_train_j_RH.append(crop_img)
  if i%60 == 0:
    print("Id:",i,"...Done.")
  x_train_RH.append(x_train_j_RH)



np.shape(x_train_RH)

x_train = []
y_train = []
for idx in range(0, len(x_train_LH)):
  for joint in range(0,16):
    x_train.append(x_train_LH[idx][joint])
    y_train.append(y_train_all_t_LH[idx][joint])

for idx in range(0, len(x_train_RH)):
  for joint in range(0,16):
    if [idx, joint] not in outliers_RH:
      x_train.append(x_train_RH[idx][joint])
      y_train.append(y_train_all_t_RH[idx][joint])

idx_0 =[]
for i in range(0,len(y_train)):
  if y_train[i] == 0:
    idx_0.append(i)
np.random.shuffle(idx_0)
rmv_idx = idx_0[:9000]
x_train = np.array(x_train)
y_train = np.array(y_train)
x_train = np.delete(x_train, rmv_idx, 0)
y_train = np.delete(y_train, rmv_idx)

np.save("/content/drive/My Drive/Independent-Prj/x_train_h.npy", x_train)
np.save("/content/drive/My Drive/Independent-Prj/y_train_h.npy", y_train)

x_train = np.array(x_train)
y_train = np.array(y_train)
LR_model = Lasso().fit(x_train, y_train)

from sklearn.externals import joblib
joblib.dump(LR_model,'/content/drive/My Drive/Independent-Prj/models/lasso_reg_model_hand.pkl')

#Cross validation sets
x_train = np.load("/content/drive/My Drive/Independent-Prj/x_train_h.npy")
y_train = np.load("/content/drive/My Drive/Independent-Prj/y_train_h.npy")
x_train = x_train[:1200]
y_train = y_train[:1200]
x_cv_set = [x_train[:240], x_train[240:480], x_train[480:720], x_train[720:960]]
y_cv_set = [y_train[:240], y_train[240:480], y_train[480:720], y_train[720:960]]

#Create cross validation models
for i in range(0,len(x_cv_set)):
  LR_model = LinearRegression().fit(x_cv_set[i], y_cv_set[i])
  f_name = "cv_reg_model_hand_" + str(i) + ".pkl"
  joblib.dump(LR_model,'/content/drive/My Drive/Independent-Prj/models/' + f_name)