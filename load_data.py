import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import torch
import torch
from torch import nn
import torch.nn.functional as F
from torch.optim import Adam
from torch.nn import CrossEntropyLoss
from torchsummary import summary
from tqdm import tqdm
import random
import model_architecture

def load():
    col_names = ["Date","Time","Tag Comment","Motor Vol Flow","Motor Flow In","Motor Flow Out","Motor Surf top","Motor Surf Side","Temp Pt100 RTD winding U", \
                "Temp Pt100 RTD winding V", "Temp Pt100 RTD winding W", "Temp PTC thermistor winding", "Temp Feed-through plate", \
                "Lead intersection", "Temp Cable gland", "Temp Terminal box seal", "Temp Terminal", "Temp Ambient", "Frequency", "Voltage", \
                "Current", "Power factor", "Input power", "Output power", "Torque", "Speed", "Slip"]
    df = pd.read_excel('./HDE-INT-MOT-20221028-01_HT8_03_N85z-4_OC2_50Hz_70C_R_000759_221107_100743.GEV.xlsx',header=32)
    df.columns = col_names
    df = df.drop([0],axis=0)
    df = df.drop(["Tag Comment","Date","Temp PTC thermistor winding"],axis=1)
    df["Time"] = list(np.arange(19206))
    df = df[df["Frequency"]!="INVALID"]
    print(df.shape)

    df_p = df
    X = df_p.to_numpy(dtype=np.float16)
    X = torch.Tensor(X)
    Y = torch.stack([torch.ones(19204),torch.zeros(19204),torch.zeros(19204)]).view(19204,3)
    X_p = X

    def augment_data(X):
        count_1 = 0
        count_2 = 0
        count_3 = 0
        new_xs = []
        new_ys = []
        for x in X:
            xs = []
            for i in range(0,len(x)):
                n = x[i]
                if i == 13:
                    n = n + random.uniform(0,1)
                elif i == 19:
                    n = n + random.uniform(0,1)
                else:
                    n = n + random.uniform(0,10)
                xs.append(n)
            # get Y values
            if xs[13] > 82.0 or xs[19] > 271:
                new_ys.append([0,0,1])
                count_1+=1
            elif xs[13] > 76.0 or xs[19] > 260.0:
                new_ys.append([0,1,0])
                count_2+=1
            else:
                new_ys.append([1,0,0])
                count_3+=1
            new_xs.append(xs)
        new_xs = torch.Tensor(np.array(new_xs))
        new_ys = torch.Tensor(np.array(new_ys))
        print(count_1,count_2,count_3)
        return new_xs, new_ys

    for i in range(0,2):
        xs, ys = augment_data(X_p)
        X = torch.cat((X,xs),0)
        Y = torch.cat((Y,ys),0)
        print(X.shape)
    print(X.shape)
    print(Y.shape)
    return X,Y