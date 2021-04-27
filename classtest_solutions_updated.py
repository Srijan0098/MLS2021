# -*- coding: utf-8 -*-
"""classtest_solutions_updated.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1-1APmVHrkjPyusJQLEvVZfRMtP11tbXQ

# Importing necessary libraries
"""

import torch
import numpy as np
from torch import nn
import torch.nn.functional as F
import helper
import os
import pandas as pd
import cv2
import csv
import torchvision.transforms as transforms
from torch.utils.data.sampler import SubsetRandomSampler
from PIL import Image

"""# Getting the data in the directory and switching to GPU"""

!git clone https://github.com/YoongiKim/CIFAR-10-images

# check if CUDA is available
train_on_gpu = torch.cuda.is_available()

if not train_on_gpu:
    print('CUDA is not available.  Training on CPU ...')
else:
    print('CUDA is available!  Training on GPU ...')

!wget https://raw.githubusercontent.com/udacity/deep-learning-v2-pytorch/3bd7dea850e936d8cb44adda8200e4e2b5d627e3/intro-to-pytorch/helper.py
import importlib
importlib.reload(helper)

# number of subprocesses to use for data loading
num_workers = 0
# how many samples per batch to load
batch_size = 20
# percentage of training set to use as validation
valid_size = 0.2

"""# Data transformations to facilitate data augmentation and normalization """

def do_your_transform(X):
  train_transforms = transforms.Compose([transforms.RandomRotation(30),
                                         transforms.RandomHorizontalFlip(),
                                         transforms.ToTensor(),
                                         transforms.Normalize([0.5, 0.5, 0.5], 
                                                              [0.5, 0.5, 0.5])])

  X1 = train_transforms(X)
  return X1

"""# Creating dataframe from images and labels"""

# train set

ptrain=[]
ctrain=[]
for folder_name in os.listdir("CIFAR-10-images/train/"):
  for files in os.listdir("CIFAR-10-images/train/"+folder_name):
    if files.split(".")[-1].lower() in {"jpeg", "jpg", "png"}:
        path='CIFAR-10-images/train/'+folder_name+'/'+files
        clss=folder_name
        ptrain.append(path)
        ctrain.append(clss)

# test set

ptest=[]
ctest=[]
for folder_name in os.listdir("CIFAR-10-images/test/"):
  for files in os.listdir("CIFAR-10-images/test/"+folder_name):
    if files.split(".")[-1].lower() in {"jpeg", "jpg", "png"}:
        path='CIFAR-10-images/test/'+folder_name+'/'+files
        clss=folder_name
        ptest.append(path)
        ctest.append(clss)

dataframe_train = pd.DataFrame({'path':ptrain,'class':ctrain})
dataframe_test = pd.DataFrame({'path':ptest,'class':ctest})

dataframe_train

dataframe_test

"""# Data to csv"""

dataframe_train.to_csv('train_data.csv',index=False)
dataframe_test.to_csv('test_data.csv',index=False)

"""# Custom dataloader"""

class MyDataset():
  
  def __init__(self,image_set,labels_reference,argument=True):
    df = pd.read_csv(image_set)
    self.imgfiles=list(df.iloc[:,0])
    self.classlabels=list(df.iloc[:,1])
    self.argument=argument
    self.ref=labels_reference 

  def __len__(self):
    return len(self.imgfiles)

  def __getitem__(self,idx):
    img=cv2.imread(self.imgfiles[idx])
    #X=np.asarray(img,dtype=np.)
    #print(X.shape)
    if self.argument:
      img = Image.fromarray(img)
      img=do_your_transform(img)
    Y=self.ref[self.classlabels[idx]]
    return img,Y

labels_dict = {'airplane':0, 'automobile':1, 'bird':2, 'cat':3, 'deer':4 , 'dog':5, 'frog':6, 'horse':7, 'ship':8, 'truck':9}
train_data = MyDataset('train_data.csv',labels_dict)
test_data = MyDataset('test_data.csv',labels_dict )

# training indices that will be used for validation
num_train = len(train_data)
indices = list(range(num_train))
np.random.shuffle(indices)
split = int(np.floor(valid_size * num_train))
train_idx, valid_idx = indices[split:], indices[:split]

# define samplers for obtaining training and validation batches
train_sampler = SubsetRandomSampler(train_idx)
valid_sampler = SubsetRandomSampler(valid_idx)

# prepare data loaders (combine dataset and sampler)
trainloader = torch.utils.data.DataLoader(train_data, batch_size=batch_size,
    sampler=train_sampler, num_workers=num_workers)
validloader = torch.utils.data.DataLoader(train_data, batch_size=batch_size, 
    sampler=valid_sampler, num_workers=num_workers)
testloader = torch.utils.data.DataLoader(test_data, batch_size=batch_size, 
    num_workers=num_workers)

"""# Building the model"""

class ConvNet(nn.Module):
    def __init__(self):
        super().__init__()
        # convolutional layer (sees 32x32x3 image tensor)
        self.conv1 = nn.Conv2d(3, 16, 3, padding=1)
        # convolutional layer (sees 16x16x16 tensor)
        self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
        # convolutional layer (sees 8x8x32 tensor)
        self.conv3 = nn.Conv2d(32, 64, 3, padding=1)
        # max pooling layer
        self.pool = nn.MaxPool2d(2, 2)
        # linear layer (64 * 4 * 4 -> 500)
        self.fc1 = nn.Linear(64 * 4 * 4, 500)
        # linear layer (500 -> 10)
        self.fc2 = nn.Linear(500, 10)
        # dropout layer (p=0.25)
        self.dropout = nn.Dropout(0.25)

    def forward(self, x):
        # add sequence of convolutional and max pooling layers
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))
        # flatten image input
        x = x.view(-1, 64 * 4 * 4)
        # add dropout layer
        x = self.dropout(x)
        # add 1st hidden layer, with relu activation function
        x = F.relu(self.fc1(x))
        # add dropout layer
        x = self.dropout(x)
        # add 2nd hidden layer, with relu activation function
        x = self.fc2(x)
        return x

import torch.optim as optim

# specify loss function (categorical cross-entropy)
model = ConvNet()
criterion = nn.CrossEntropyLoss()

# specify optimizer
optimizer = optim.Adam(model.parameters(), lr=0.004)

if train_on_gpu:
    model.cuda()

print(model)

"""# Training the model"""

# number of epochs to train the model
n_epochs = 30

valid_loss_min = np.Inf # track change in validation loss

for epoch in range(1, n_epochs+1):

    # keep track of training and validation loss
    train_loss = 0.0
    valid_loss = 0.0
    
    
    model.train()
    for batch_idx, (data, target) in enumerate(trainloader):
        # move tensors to GPU if CUDA is available
        if train_on_gpu:
            data, target = data.cuda(), target.cuda()
        # clear the gradients of all optimized variables
        optimizer.zero_grad()
        #print(data.shape)
        # forward pass: compute predicted outputs by passing inputs to the model
        output = model(data)
        #print(output.shape)
        top_p,top_class=output.topk(1,dim=1)
        equalstry=top_class==target
        equals=top_class==target.view(*top_class.shape)
        accuracy=torch.mean(equals.type(torch.FloatTensor))


        print(f'Accuracy: {accuracy.item()*100}%')

        # calculate the batch loss
        loss = criterion(output, target)
        # backward pass: compute gradient of the loss with respect to model parameters
        loss.backward()
        # perform a single optimization step (parameter update)
        optimizer.step()
        # update training loss
        train_loss += loss.item()*data.size(0)

"""# Validation"""

model.eval()
for batch_idx, (data, target) in enumerate(validloader):

        # move tensors to GPU if CUDA is available
    print(type(data))
    if train_on_gpu:
        data, target = data.cuda(), target.cuda()
        # forward pass: compute predicted outputs by passing inputs to the model
    output = model(data)
      #print(output.shape)
        # calculate the batch loss
    loss = criterion(output, target)
        # update average validation loss 
    valid_loss += loss.item()*data.size(0)
    
    # calculate average losses
    train_loss = train_loss/len(trainloader.sampler)
    valid_loss = valid_loss/len(validloader.sampler)
        
    # print training/validation statistics 
    print('Epoch: {} \tTraining Loss: {:.6f} \tValidation Loss: {:.6f}'.format(
        epoch, train_loss, valid_loss))
    
    # save model if validation loss has decreased
    if valid_loss <= valid_loss_min:
        print('Validation loss decreased ({:.6f} --> {:.6f}).  Saving model ...'.format(
        valid_loss_min,
        valid_loss))
        torch.save(model.state_dict(), 'model_augmented.pt')
        valid_loss_min = valid_loss



