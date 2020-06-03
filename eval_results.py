# -*- coding: utf-8 -*-
"""eval_results.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1bqviUkcttQemxy1ahjIqGPV1YFdVkdgI
"""

import os
import cv2
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error

all_joints = np.array(['LH_mcp_E__ip', 'LH_pip_E__2', 'LH_pip_E__3',
       'LH_pip_E__4', 'LH_pip_E__5', 'LH_mcp_E__1', 'LH_mcp_E__2',
       'LH_mcp_E__3', 'LH_mcp_E__4', 'LH_mcp_E__5', 'LH_wrist_E__mc1',
       'LH_wrist_E__mul', 'LH_wrist_E__nav', 'LH_wrist_E__lunate',
       'LH_wrist_E__radius', 'LH_wrist_E__ulna', 'RH_mcp_E__ip',
       'RH_pip_E__2', 'RH_pip_E__3', 'RH_pip_E__4', 'RH_pip_E__5',
       'RH_mcp_E__1', 'RH_mcp_E__2', 'RH_mcp_E__3', 'RH_mcp_E__4',
       'RH_mcp_E__5', 'RH_wrist_E__mc1', 'RH_wrist_E__mul',
       'RH_wrist_E__nav', 'RH_wrist_E__lunate', 'RH_wrist_E__radius',
       'RH_wrist_E__ulna', 'LF_mtp_E__ip', 'LF_mtp_E__1', 'LF_mtp_E__2',
       'LF_mtp_E__3', 'LF_mtp_E__4', 'LF_mtp_E__5', 'RF_mtp_E__ip',
       'RF_mtp_E__1', 'RF_mtp_E__2', 'RF_mtp_E__3', 'RF_mtp_E__4',
       'RF_mtp_E__5', 'LH_pip_J__2', 'LH_pip_J__3', 'LH_pip_J__4',
       'LH_pip_J__5', 'LH_mcp_J__1', 'LH_mcp_J__2', 'LH_mcp_J__3',
       'LH_mcp_J__4', 'LH_mcp_J__5', 'LH_wrist_J__cmc3',
       'LH_wrist_J__cmc4', 'LH_wrist_J__cmc5', 'LH_wrist_J__mna',
       'LH_wrist_J__capnlun', 'LH_wrist_J__radcar', 'RH_pip_J__2',
       'RH_pip_J__3', 'RH_pip_J__4', 'RH_pip_J__5', 'RH_mcp_J__1',
       'RH_mcp_J__2', 'RH_mcp_J__3', 'RH_mcp_J__4', 'RH_mcp_J__5',
       'RH_wrist_J__cmc3', 'RH_wrist_J__cmc4', 'RH_wrist_J__cmc5',
       'RH_wrist_J__mna', 'RH_wrist_J__capnlun', 'RH_wrist_J__radcar',
       'RF_mtp_J__ip', 'LF_mtp_J__1', 'LF_mtp_J__2', 'LF_mtp_J__3',
       'LF_mtp_J__4', 'LF_mtp_J__5', 'LF_mtp_J__ip', 'RF_mtp_J__1',
       'RF_mtp_J__2', 'RF_mtp_J__3', 'RF_mtp_J__4', 'RF_mtp_J__5'])

df_pred = pd.read_csv("/content/drive/My Drive/Independent-Prj/models/output/predictions.csv")
df_true = pd.read_csv("/content/drive/My Drive/Independent-Prj/training.csv")
patient_ids = np.array(df_pred["Patient_ID"])

rmse_per_patient = []
y_true_overall = []
for patient in patient_ids:
  y_true = np.array(df_true.loc[df_true["Patient_ID"] == patient, all_joints])
  y_pred = np.array(df_pred.loc[df_pred["Patient_ID"] == patient, all_joints])
  y_true_overall.append(np.array(df_true.loc[df_true["Patient_ID"] == patient, ["Overall_erosion"]]))
  mse = np.sqrt(mean_squared_error(y_true, y_pred))
  rmse_per_patient.append(mse)

eval_SC2 = np.mean(rmse_per_patient)
print("Avg of RMSE per Patient:",eval_SC2)

y_true_overall_t = []
for x in y_true_overall:
  y_true_overall_t.append(x[0][0])

y_pred_overall = np.array(df_pred["Overall_erosion"])
mae_SC1 = mean_absolute_error(y_true_overall_t, y_pred_overall)
print("Avg of MAE per Patient:", mae_SC1)