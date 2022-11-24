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

class FFNN(nn.Module):
    """
    Classifier detecting problems
    """

    def __init__(self):
        """
        Model Constructor, Initialize all the layers to be used
        """
        super(FFNN, self).__init__()
        self.fc1 = nn.Linear(24, 1024)
        self.fc2 = nn.Linear(1024, 256)
        self.fc3 = nn.Linear(256, 64)
        self.fc4 = nn.Linear(64, 3)
        self.sm = nn.Softmax(dim=1)

    def forward(self, x):
        """
        :param x: input data of this model
        :return: output data of this model
        """
        x = self.fc1(x)
        x = F.relu(x)
        x = self.fc2(x)
        x = F.relu(x)
        x = self.fc3(x)
        x = F.relu(x)
        x = self.fc4(x)
        x = self.sm(x)
        return x

class CNN(nn.Module):
    """
    CNN
    """

    def __init__(self):
        """
        Model Constructor, Initialize all the layers to be used
        """
        super(CNN, self).__init__()
        self.cnn = nn.Conv1d(in_channels=1, out_channels=20, kernel_size=12)
        self.fc = nn.Linear(260, 3)
        self.sm = nn.Softmax(dim=1)

    def forward(self, x):
        """
        :param x: input data of this model
        :return: output data of this model
        """
        x = self.cnn(x)
        x = F.relu(x)
        x = x.view(1,260)
        x = self.fc(x)
        x = self.sm(x)
        return x

class RNN(nn.Module):
    """
    LSTM
    """

    def __init__(self):
        """
        Model Constructor, Initialize all the layers to be used
        """
        super(RNN, self).__init__()
        self.lstm = nn.LSTM(input_size=24, hidden_size=128, num_layers=1)
        self.fc = nn.Linear(128, 3)
        self.sm = nn.Softmax(dim=1)

    def forward(self, x):
        """
        :param x: input data of this model
        :return: output data of this model
        """
        x, _ = self.lstm(x)
        x = F.relu(x)
        x = x.view(1,128)
        x = self.fc(x)
        x = self.sm(x)
        return x

class Ensemble(nn.Module):
    """
    Ensemble
    """

    def __init__(self):
        """
        Model Constructor, Initialize all the layers to be used
        """
        super(Ensemble, self).__init__()
        self.nn = FFNN()
        self.cnn = CNN()
        self.rnn = RNN()
        self.sm = nn.Softmax(dim=1)
        self.l1 = torch.nn.Parameter(torch.ones(1,1))
        self.l2 = torch.nn.Parameter(torch.ones(1,1))

    def forward(self, x):
        """
        :param x: input data of this model
        :return: output data of this model
        """
        x1 = self.nn(x)
        x2 = self.cnn(x)
        x3 = self.rnn(x)
        x = x1 + self.l1*x2 + self.l2*x3

        x = self.sm(x)
        return x

print(summary(Ensemble(),torch.zeros(1,24)))