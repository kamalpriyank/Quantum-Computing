# -*- coding: utf-8 -*-
"""Quantum_ARP.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1oZLPbNWvyluRe8D4dP_wcT2qvBxzq44R

# ***Installing ALL Required Packages***
"""

# Installing Eequired External Packages
!pip install pennylane
! pip install -Uq kaggle
! pip install -Uq fastai==2.2.5
!pip install --upgrade torch
!pip install split-folders
!pip install ipyplot

"""# ***Importing All Necessary Packages***"""

import matplotlib.pyplot as plt
import seaborn as sns

import keras
from keras.models import Sequential
from keras.layers import Dense, Conv2D , MaxPooling2D , Dropout , BatchNormalization
from keras.layers import Flatten
from keras.preprocessing.image import ImageDataGenerator
from keras import models
from keras.callbacks import ModelCheckpoint, EarlyStopping
from sklearn.metrics import classification_report,confusion_matrix

import tensorflow as tf
import pandas as pd
import cv2
import os

import numpy as np
from tqdm import tqdm
from keras.preprocessing import image
from sklearn.model_selection import train_test_split
from keras.models import load_model
import pennylane as qml
from pennylane import numpy as np
from pennylane.templates import RandomLayers
import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics import confusion_matrix
from PIL import Image
from skimage import color
from skimage import io
import imblearn
from imblearn.over_sampling import SMOTE
from collections import Counter
import splitfolders
import ipyplot

"""## ***Uploading Kaggle.json file key to access kaggle API***"""

from google.colab import files 
files.upload()

! mkdir ~/.kaggle
! cp kaggle.json ~/.kaggle/
! chmod 600 ~/.kaggle/kaggle.json

"""## ***Downloading Planets dataset***"""

! kaggle datasets download nikitarom/planets-dataset

!unzip planets-dataset.zip

from fastai.vision.all import *
path = Path('./planet/planet')

"""## ***Data Pre-Processing***"""

labels = pd.read_csv(path/'train_classes.csv')

labels.tags = labels.tags.apply(lambda x: 'remove' if 'cloudy' in x else x)
labels.tags = labels.tags.apply(lambda x: 'remove' if 'partly_cloudy' in x else x)
labels.tags = labels.tags.apply(lambda x: 'remove' if 'haze' in x else x)

labels = labels[~labels['tags'].isin(['remove'])]

labels.tags = labels.tags.apply(lambda x: 'Detected_Deforestation' if 'agriculture' in x else x)
labels.tags = labels.tags.apply(lambda x: 'Detected_Deforestation' if 'selective_logging' in x else x)
labels.tags = labels.tags.apply(lambda x: 'Detected_Deforestation' if 'artisinal_mine' in x else x)
labels.tags = labels.tags.apply(lambda x: 'Detected_Deforestation' if 'conventional_mine' in x else x)
labels.tags = labels.tags.apply(lambda x: 'Detected_Deforestation' if 'cultivation' in x else x)
labels.tags = labels.tags.apply(lambda x: 'Detected_Deforestation' if 'road' in x else x)
labels.tags = labels.tags.apply(lambda x: 'Detected_Deforestation' if 'slash_burn' in x else x)

labels.tags = labels.tags.apply(lambda x: 'Forest' if 'clear' in x else x)
labels.tags = labels.tags.apply(lambda x: 'Forest' if 'primary' in x else x)
labels.tags = labels.tags.apply(lambda x: 'Forest' if 'water' in x else x)
labels.tags = labels.tags.apply(lambda x: 'Forest' if 'bare_ground' in x else x)
labels.tags = labels.tags.apply(lambda x: 'Forest' if 'blooming' in x else x)
labels.tags = labels.tags.apply(lambda x: 'Forest' if 'habitation' in x else x)

labels.nunique()

labels.info()



labels.tags[labels.tags == 'Detected_Deforestation'] = 1
labels.tags[labels.tags == 'Forest'] = 0
labels = labels.reset_index()
print(labels)

images = []
classes = []
im = []
lab = []
for i in tqdm(range(len(labels))):
    img = tf.keras.utils.load_img('/content/planet/planet/train-jpg/'+labels['image_name'][i]+'.jpg',target_size=(224,224))
    im.append(img)
    lab.append(labels['tags'][i])
    img = tf.keras.utils.img_to_array(img)
    img = img/255
    images.append(img)
    classes.append(labels['tags'][i])
    if len(images)==1000:
      break

ipyplot.plot_images(im,lab, max_images=12, img_width=150)

images = np.array(images)
images = images.astype(np.float32)

images.shape

classes = np.array(classes)
classes = classes.astype(np.float32)

classes.shape

classes = np.array(classes)
classes = classes.astype(np.float32)

images_Q = []
classes_Q = []
for i in tqdm(range(len(labels))):
    img = tf.keras.utils.load_img('/content/planet/planet/train-jpg/'+labels['image_name'][i]+'.jpg',target_size=(64,64))
    img = tf.keras.utils.img_to_array(img)
    img = img/255
    images_Q.append(img)
    classes_Q.append(labels['tags'][i])
    if len(images_Q)==1000:
      break

images_Q = np.array(images_Q)
images_Q = images_Q.astype(np.float32)
classes_Q = np.array(classes_Q)
classes_Q = classes_Q.astype(np.float32)

final_dataset = []
for img in images_Q:
  img = img[:,:,0]
  final_dataset.append(img)
final_dataset = np.array(final_dataset)

final_dataset.shape

plt.imshow(final_dataset[4])

"""# **Q - C Approach**

## ***Train-Test-Split for Classical Model***
"""

X_train, X_rem, y_train, y_rem = train_test_split(images, classes, random_state=64,test_size=0.5)
X_valid,X_test,y_valid,y_test = train_test_split(X_rem,y_rem,random_state=64,test_size =0.2)

# Before SMOTE
count = Counter(y_train)
print(count)

# Using SMOTE with sampling_strategy = 0.8 for over sampling
oversampling = SMOTE(sampling_strategy=0.8)
X_train,y_train = oversampling.fit_resample(X_train.reshape(X_train.shape[0], -1),y_train)
X_train = X_train.reshape(X_train.shape[0], 224, 224,3)

# After SMOTE
count = Counter(y_train)
print(count)

"""## ***Building CNN Model From Scratch***"""

from keras.layers import Flatten
model = Sequential()
model.add(Conv2D(filters=16, kernel_size=(3, 3),padding = "same",activation="relu", input_shape=X_train.shape[1:]))
model.add(MaxPooling2D(pool_size=2,strides=2))
model.add(Conv2D(filters=16, kernel_size=(3, 3),padding = "same",activation="relu"))
model.add(MaxPooling2D(pool_size=2,strides=2))
model.add(BatchNormalization())
model.add(Dropout(0.25))
model.add(Conv2D(filters=32, kernel_size=(3, 3),padding = "same", activation='relu'))
model.add(MaxPooling2D(pool_size=2,strides=2))
model.add(BatchNormalization())
model.add(Dropout(0.25))
model.add(Conv2D(filters=64, kernel_size=(3, 3),padding = "same", activation='relu'))
model.add(MaxPooling2D(pool_size=2,strides=2))
model.add(BatchNormalization())
model.add(Dropout(0.25))
model.add(Flatten())
model.add(Dense(64, activation='relu'))
model.add(BatchNormalization())
model.add(Dropout(0.25))
model.add(Dense(32, activation='relu'))
model.add(BatchNormalization())
model.add(Dropout(0.25))
model.add(Dense(16, activation='relu'))
model.add(BatchNormalization())
model.add(Dropout(0.25))
model.add(Dense(1, activation='sigmoid'))

model.summary()

"""### ***Compile & Fit the training data to the model***"""

model.compile(optimizer = 'adam' , loss = 'mse' , metrics = ['accuracy'])

Forest_def = model
save_model = ModelCheckpoint('Forest_Deforestation.h5', monitor='val_accuracy',verbose=1, save_best_only=True, save_weights_only=True)
es = EarlyStopping(monitor='val_loss', mode='min', verbose=1)
history = Forest_def.fit(X_train,y_train,epochs = 50,batch_size = 32, validation_data = (X_valid, y_valid), callbacks=[save_model])

"""### ***Calculating all Evaluation metrics***"""

# calculating Training and Testing accuracy
acc1 = Forest_def.evaluate(X_test, y_test, verbose=0)
acc2 = Forest_def.evaluate(X_train, y_train, verbose=0)
print("Training Accuracy: %.2f%%" % (acc2[1]*100))
print("Testing Accuracy: %.2f%%" % (acc1[1]*100))

# saving model history to a .nopy file using np.save
np.save('F_D.npy', Forest_def.history.history)
# loading the saved history from a .npy file using np.load
Forest_def_history = np.load('F_D.npy', allow_pickle='TRUE').item()

"""### ***Plotting the Loss, Accuracy, Val_Accuracy, Val_accuracy on a single chart***"""

# visualizing the loss,val_loss,accuracy and val_accuracy on a single graph
pd.DataFrame(history.history).plot()
plt.show()

# predicting probabilities for the test set
y_prob = Forest_def.predict(X_test, verbose=0)
# converting the probabilites into 1's and 0's
y_prob = (y_prob>0.5).astype(np.float32)
y_prob = y_prob[:, 0]

# calculating Precision, Recall, F1 Score and AUC
precision = precision_score(y_test, y_prob)
recall = recall_score(y_test, y_prob)
f1 = f1_score(y_test, y_prob)
auc = roc_auc_score(y_test, y_prob)
# getting a confusion matrix
confusion_m = confusion_matrix(y_test, y_prob)
# Printing all the Evalution Metrics
print(confusion_m)
print('Precision: %f' % precision)
print('Recall: %f' % recall)
print('F1 score: %f' % f1)
print('ROC AUC: %f' % auc)

names = ['TN','FP','FN','TP']
counts = ["{0:0.0f}".format(value) for value in confusion_m.flatten()]
percents = ["{0:.2%}".format(value) for value in confusion_m.flatten()/np.sum(confusion_m)]
lab = [f"{v1}\n{v2}\n{v3}" for v1, v2, v3 in
          zip(names,counts,percents)]
lab = np.asarray(lab).reshape(2,2)
sns.heatmap(confusion_m, annot=lab, fmt='', cmap='OrRd')
plt.show()

"""##***Hybrid Quantum Classical Model***

### ***Quantum Preprocessing of the Dataset***
"""

q_epochs = 30           # number of epochs for the quantum model
q_layers = 1            # number of layers
n = 1000                 # dataset size for quantum preprocessing
PREPROCESS = False      # If False, directly loads the data from the files, skipping the quatum preprocessing step
np.random.seed(0)       
tf.random.set_seed(0)

Q_final_dataset = final_dataset
Q_final_dataset = np.array(Q_final_dataset[..., tf.newaxis])
Q_labels = classes_Q

"""### ***Intializing The Quantum Device***"""

dev = qml.device("default.qubit", wires=4)
# Random circuit parameters
rand_params = np.random.uniform(high=2 * np.pi, size=(q_layers, 4))

@qml.qnode(dev)
def circuit(phi):
    # Encoding of 4 classical input values
    for j in range(4):
        qml.RY(np.pi * phi[j], wires=j)

    # Random quantum circuit
    RandomLayers(rand_params, wires=list(range(4)))

    # Measurement producing 4 classical output values
    return [qml.expval(qml.PauliZ(j)) for j in range(4)]

"""### ***Defining a quantum circuit as shown in Pennylane***"""

def quanv(image):
    output = np.zeros((32,32,4))
    # Looping over the certain pixel portions of a 224 X 224 forest image
    for j in range(0, 64, 2):
        for k in range(0, 64, 2):
            # processing a 224 X 224 image through a quantum circuit
            q_results = circuit([image[j, k, 0],image[j, k + 1, 0],image[j + 1, k, 0],image[j + 1, k + 1, 0]])
            # assigning values to four channels of the output image
            for c in range(4):
                output[j // 2, k // 2, c] = q_results[c]
    return output

# Path to save the pre-processed images
SAVE_PATH = "/content/"

# looping over the final dataset to preprocess images using quanv() function and appending each image to a list Q_images
if PREPROCESS == True:
    Q_images = []
    print("The images are being preprocessed with the quantum circuit built in the previous code cell")
    for idx, img in enumerate(Q_final_dataset):
        Q_images.append(quanv(img))
        # Converting list to numpy array
        # Saving
        np.save(SAVE_PATH + "Q_images.npy", Q_images)
else:       
   # Loading
   Q_images = np.load(SAVE_PATH + "Q_images.npy")

Q_images = np.asarray(Q_images)

fig, axes = plt.subplots(5, 4, figsize=(10, 10))
for a in range(4):
    if a != 0:
        axes[0, a].yaxis.set_visible(False)
    axes[0, a].imshow(Q_final_dataset[a, :, :, 0], cmap="gray")
    for b in range(4):
        if a != 0:
            axes[b, a].yaxis.set_visible(False)
        axes[b + 1, a].imshow(Q_images[a, :, :, b], cmap="gray")

axes[0, 0].set_ylabel("Input")
axes[1, 0].set_ylabel("Output Channel 1")
axes[2, 0].set_ylabel("Output Channel 2")
axes[3, 0].set_ylabel("Output Channel 3")
axes[4, 0].set_ylabel("Output Channel 4")

plt.tight_layout()
plt.show()

"""### ***Training Classical AI Model with Quantum Preprocessed Data***"""

Q_train, X_rem, Q_train_labels, y_rem = train_test_split(Q_images, Q_labels, random_state=64, test_size=0.5)
Q_valid,Q_test,Q_valid_labels,Q_test_labels = train_test_split(X_rem,y_rem,random_state=64,test_size =0.2)

# Using SMOTE with sampling_strategy = 0.8 for over sampling
oversampling = SMOTE(sampling_strategy=0.8)
Q_train,Q_train_labels = oversampling.fit_resample(Q_train.reshape(Q_train.shape[0], -1), Q_train_labels)
Q_train = Q_train.reshape(Q_train.shape[0], 32, 32, 4)

Q_train.shape

model = Sequential()
model.add(Conv2D(filters=16, kernel_size=(3, 3),padding = "same",activation="relu", input_shape=Q_train.shape[1:]))
model.add(MaxPooling2D(pool_size=2,strides=2))
model.add(Conv2D(filters=16, kernel_size=(3, 3),padding = "same",activation="relu"))
model.add(MaxPooling2D(pool_size=2,strides=2))
model.add(BatchNormalization())
model.add(Dropout(0.25))
model.add(Conv2D(filters=32, kernel_size=(3, 3),padding = "same", activation='relu'))
model.add(MaxPooling2D(pool_size=2,strides=2))
model.add(BatchNormalization())
model.add(Dropout(0.25))
model.add(Conv2D(filters=64, kernel_size=(3,3),padding = "same", activation='relu'))
model.add(MaxPooling2D(pool_size=2,strides=2))
model.add(BatchNormalization())
model.add(Dropout(0.25))
model.add(Flatten())
model.add(Dense(64, activation='relu'))
model.add(BatchNormalization())
model.add(Dropout(0.25))
model.add(Dense(32, activation='relu'))
model.add(BatchNormalization())
model.add(Dropout(0.25))
model.add(Dense(16, activation='relu'))
model.add(BatchNormalization())
model.add(Dropout(0.25))
model.add(Dense(1, activation='sigmoid'))

model.summary()

Q_Forest_def = model

Q_Forest_def.compile(optimizer = 'adam' , loss = 'mse' , metrics = ['accuracy'])

save_model = ModelCheckpoint('Forest_Deforestation_Quantum.h5', monitor='val_accuracy',verbose=1, save_best_only=True, save_weights_only=True)
es = EarlyStopping(monitor='val_loss', mode='min', verbose=1)
Q_history = Q_Forest_def.fit(Q_train,Q_train_labels,epochs = 50,batch_size=32, validation_data = (Q_valid, Q_valid_labels),callbacks=[save_model])

# Save model history to .npy file
np.save('F_D_Q.npy', Q_Forest_def.history.history)
# Load model history from .npy file
Quantum_model_history = np.load('F_D_Q.npy', allow_pickle='TRUE').item()

# plotting loss, validation_loss, accuracy and validation_accuracy on the same plot
pd.DataFrame(history.history).plot()
plt.show()

"""### ***Calculating all Evaluation Metrics***"""

# Calculating Testing Accuracy
a1 = Q_Forest_def.evaluate(Q_test, Q_test_labels, verbose=0)
a2 = Q_Forest_def.evaluate(Q_train, Q_train_labels, verbose=0)
print("Training Accuracy: %.2f%%" % (a2[1]*100))
print("Testing Accuracy: %.2f%%" % (a1[1]*100))

# predicting target clases for test set
Q_yhat_probs = Q_Forest_def.predict(Q_test, verbose=0)
# converting the predicted probabilities into 1's and 0's
Q_yhat_probs = (Q_yhat_probs>0.5).astype(np.float32)
Q_yhat_probs = Q_yhat_probs[:, 0]

# Calculating Precision,Recall,F1 Score and Accuracy
Q_precision = precision_score(Q_test_labels, Q_yhat_probs)
Q_recall = recall_score(Q_test_labels, Q_yhat_probs)
Q_f1 = f1_score(Q_test_labels, Q_yhat_probs)
Q_auc = roc_auc_score(Q_test_labels, Q_yhat_probs)
# Confusion Matrix
Q_confusion_matrix = confusion_matrix(Q_test_labels, Q_yhat_probs)
# Printing all the Evalution Metrics
print(Q_confusion_matrix)
print('Precision(Q): %f' % Q_precision)
print('Recall(Q): %f' % Q_recall)
print('F1 score (Q): %f' % Q_f1)
print('ROC AUC (Q): %f' % Q_auc)

names = ['TN','FP','FN','TP']
counts = ["{0:0.0f}".format(value) for value in Q_confusion_matrix.flatten()]
percents = ["{0:.2%}".format(value) for value in Q_confusion_matrix.flatten()/np.sum(Q_confusion_matrix)]
lab = [f"{v1}\n{v2}\n{v3}" for v1, v2, v3 in
          zip(names,counts,percents)]
lab = np.asarray(lab).reshape(2,2)
sns.heatmap(Q_confusion_matrix, annot=lab, fmt='', cmap='OrRd')
plt.show()

"""# **C - Q Approach**

## ***Transfer Learning***
"""

# Importing all necessary packages
import time
import os
import copy
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim import lr_scheduler
import torchvision
from torchvision import datasets, transforms
from tqdm import tqdm
import pennylane as qml
from pennylane import numpy as np
torch.manual_seed(42)
np.random.seed(42)
import matplotlib.pyplot as plt
os.environ["OMP_NUM_THREADS"] = "1"
from copy import deepcopy

# Creating class_1 subfolder
os.makedirs('Pytorch_data/class_1')

# creating class_0 subfolder
os.makedirs('Pytorch_data/class_0')

# creating two empty lists class_1 and class_0
# looping through the dataset and appending images belonging to class 1 to class_1 and class 0 to class_0
class_1 = []
class_0 = []
for i in tqdm(range(1000)):
   if labels['tags'][i] == 1:
    img = tf.keras.utils.load_img('/content/planet/planet/train-jpg/'+labels['image_name'][i]+'.jpg',target_size=(224,224,1))
    img = tf.keras.utils.img_to_array(img)
    class_1.append(img)
    cv2.imwrite('/content/Pytorch_data/class_1/'+labels['image_name'][i]+'.jpg',img)
   else:
    img = tf.keras.utils.load_img('/content/planet/planet/train-jpg/'+labels['image_name'][i]+'.jpg',target_size=(224,224,1))
    img = tf.keras.utils.img_to_array(img)
    class_0.append(img)
    cv2.imwrite('/content/Pytorch_data/class_0/'+labels['image_name'][i]+'.jpg',img)

# using the splitfolders function to divide the folder into train, val and test subfolders in 0.5,0.3,0.2 ratios respectively
input_folder = '/content/Pytorch_data'
splitfolders.ratio(input_folder,output="Train_Val",seed=42,ratio=(.6,.4),group_prefix=None)

batch_size = 4

data_transforms = {
    "train": transforms.Compose(
        [
            transforms.RandomResizedCrop(224),     # data augmentation
            transforms.RandomHorizontalFlip(),     # data augmentation
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            # Normalizing
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]
    ),
    "val": transforms.Compose(
        [
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]
    ),
}

data_dir = "/content/Train_Val"
image_datasets = {
    x if x == "train" else "val": datasets.ImageFolder(
        os.path.join(data_dir, x), data_transforms[x]
    )
    for x in ["train", "val"]
}
dataset_sizes = {x: len(image_datasets[x]) for x in ["train", "val"]}
class_names = image_datasets["train"].classes

# Initialize dataloader
dataloaders = {
    x: torch.utils.data.DataLoader(image_datasets[x], batch_size=batch_size, shuffle=True)
    for x in ["train", "val"]
}

# iterating over the validation data in dataloaders to extract inputs nad classes
inputs, classes = next(iter(dataloaders["val"]))
# visualizing a batch of the data
out = torchvision.utils.make_grid(inputs)
#transposing the images
out = out.numpy().transpose((1, 2, 0))
# Reversing back to the images before normalization
mean = np.array([0.485, 0.456, 0.406])
std = np.array([0.229, 0.224, 0.225])
out = std * out + mean
out = np.clip(out, 0, 1)
# displaying images
plt.imshow(out)

"""### ***Classical Transfer Learning***"""

def metrics(confusion_matrix):
  test_accuracy = confusion_matrix.diag(0).sum()/confusion_matrix.sum()
  precision = (confusion_matrix[1][1]/confusion_matrix.sum(0)[1])
  recall = (confusion_matrix[1][1]/confusion_matrix[1].sum())
  f1_score = 2*((precision*recall)/(precision+recall))
  sensitivity = (confusion_matrix[1][1])/(confusion_matrix[1][0]+confusion_matrix[1][1])
  specificity = (confusion_matrix[0][0])/(confusion_matrix[0][0]+confusion_matrix[0][1])
  auc = (sensitivity + specificity)/2
  return print(confusion_matrix),print("Testing Accuracy: %.2f%%" % (test_accuracy*100)),print("Precision:",precision.numpy()),print("Recall:",recall.numpy()),print("F1 Score:",f1_score.numpy()),print("AUC:",auc.numpy())

def eval_metrics(model):
  confusion_matrix = torch.zeros(2,2)
  with torch.no_grad():
      for i, (inputs, classes) in enumerate(dataloaders['val']):
          inputs = inputs.to(device)
          classes = classes.to(device)
          outputs = model(inputs)
          _, preds = torch.max(outputs, 1)
          for t, p in zip(classes.view(-1), preds.view(-1)):
                  confusion_matrix[t.long(), p.long()] += 1
  return  metrics(confusion_matrix)

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

def train_model(model, criterion, optimizer, scheduler, num_epochs):
    since_time = time.time()
    best_weights = copy.deepcopy(model.state_dict())
    best_accuracy = 0.0
    best_loss = 10000.0  
    best_accuracy_train = 0.0
    best_loss_train = 10000.0 
    print("Training started:")

    for epoch in range(num_epochs):

        # Each epoch has a training and validation phase
        for phase in ["train", "val"]:
            if phase == "train":
                # Set model to training mode
                model.train()
            else:
                # Set model to evaluate mode
                model.eval()
            running_loss = 0.0
            running_corrects = 0

            # Iterate over data.
            n_batches = dataset_sizes[phase] // batch_size
            it = 0
            for inputs, labels in dataloaders[phase]:
                since_time_batch = time.time()
                batch_size_ = len(inputs)
                inputs = inputs.to(device)
                labels = labels.to(device)
                optimizer.zero_grad()

                # Track/compute gradient and make an optimization step only when training
                with torch.set_grad_enabled(phase == "train"):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)
                    if phase == "train":
                        loss.backward()
                        optimizer.step()

                # Print iteration results
                running_loss += loss.item() * batch_size_
                batch_corrects = torch.sum(preds == labels.data).item()
                running_corrects += batch_corrects
                print(
                    "Phase: {} Epoch: {}/{} Iter: {}/{} Batch time: {:.4f}".format(
                        phase,
                        epoch + 1,
                        num_epochs,
                        it + 1,
                        n_batches + 1,
                        time.time() - since_time_batch,
                    ),
                    end="\r",
                    flush=True,
                )
                it += 1

            # Print epoch results
            epoch_loss = running_loss / dataset_sizes[phase]
            epoch_acc = running_corrects / dataset_sizes[phase]
            print(
                "Phase: {} Epoch: {}/{} Loss: {:.4f} Acc: {:.4f}        ".format(
                    "train" if phase == "train" else "val",
                    epoch + 1,
                    num_epochs,
                    epoch_loss,
                    epoch_acc,
                )
            )

            # Check if this is the best model wrt previous epochs
            if phase == "val" and epoch_acc > best_accuracy:
                best_accuracy = epoch_acc
                best_weights = copy.deepcopy(model.state_dict())
            if phase == "val" and epoch_loss < best_loss:
                best_loss = epoch_loss
            if phase == "train" and epoch_acc > best_accuracy_train:
                best_accuracy_train = epoch_acc
            if phase == "train" and epoch_loss < best_loss_train:
                best_loss_train = epoch_loss

            # Update learning rate
            if phase == "train":
                scheduler.step()

    # Print final results
    model.load_state_dict(best_weights)
    time_elapsed = time.time() - since_time
    print(
        "Training completed in {:.0f}m {:.0f}s".format(time_elapsed // 60, time_elapsed % 60)
    )
    print("Best Training Loss: {:.4f} | Best Training Accuracy: {:.4f}".format(best_loss_train, best_accuracy_train))
    print("Best Validation Loss: {:.4f} | Best validation Accuracy: {:.4f}".format(best_loss, best_accuracy))
    return model

"""#### **Resnet18**"""

resnet = torchvision.models.resnet18(pretrained=True)

num_ftrs = resnet.fc.in_features
# Here the output targets is set to 2 as the we have two classes class_1 and class_0
resnet.fc = nn.Linear(num_ftrs, 2)
resnet = resnet.to(device)
# setting the criterion
criterion = nn.CrossEntropyLoss()
# optimizer Adam with a learning rate of 0.0004
optimizer_ft = optim.Adam(resnet.parameters(), lr=0.0004)
# Decay LR every 10 epochs i.e. step size and with factor 0.1 i.e. gamma
exp_lr_scheduler = lr_scheduler.StepLR(optimizer_ft, step_size=10, gamma=0.1)

resnet = train_model(resnet, criterion, optimizer_ft, exp_lr_scheduler,num_epochs=30)

eval_metrics(resnet)

confusion_matrix = torch.zeros(2,2)
with torch.no_grad():
    for i, (inputs, classes) in enumerate(dataloaders['val']):
          inputs = inputs.to(device)
          classes = classes.to(device)
          outputs = resnet(inputs)
          _, preds = torch.max(outputs, 1)
          for t, p in zip(classes.view(-1), preds.view(-1)):
                  confusion_matrix[t.long(), p.long()] += 1

"""####**VGG16**"""

vgg16 = torchvision.models.vgg16(pretrained=True)

num_ftrs = 25088
# Here the output targets is set to 2 as the we have two classes class_1 and class_0
vgg16.classifier = nn.Linear(num_ftrs, 2)
vgg16 = vgg16.to(device)

# setting the criterion
criterion = nn.CrossEntropyLoss()
# optimizer Adam with a learning rate of 0.0004
optimizer_vgg16 = optim.Adam(vgg16.parameters(), lr=0.0004)
# Decay LR every 10 epochs i.e. step size and with factor 0.1 i.e. gamma
exp_lr_scheduler_vgg16 = lr_scheduler.StepLR(optimizer_vgg16, step_size=10, gamma=0.1)

vgg16.classifier

vgg16 = train_model(vgg16, criterion, optimizer_vgg16, exp_lr_scheduler_vgg16,num_epochs=30)

eval_metrics(vgg16)

"""####**densenet**"""

densenet = torchvision.models.densenet121(pretrained=True)

# Here the output targets is set to 2 as the we have two classes class_1 and class_0
num_ftrs =densenet.classifier.in_features
densenet.classifier = nn.Linear(num_ftrs, 2)
densenet = densenet.to(device)

# Setting criterion
criterion = nn.CrossEntropyLoss()
# optimizer Adam with a learning rate of 0.0004
optimizer_densenet = optim.Adam(densenet.parameters(), lr=0.0004)
# Decay LR every 10 epochs i.e. step size and with factor 0.1 i.e. gamma
exp_lr_scheduler_densenet = lr_scheduler.StepLR(optimizer_densenet, step_size=10, gamma=0.1)

densenet = train_model(densenet, criterion, optimizer_densenet, exp_lr_scheduler_densenet,num_epochs=30)

eval_metrics(densenet)

"""####**Alexnet**"""

alexnet = torchvision.models.alexnet(pretrained=True)

# Here the output targets is set to 2 as the we have two classes class_1 and class_0
num_ftrs = 9216
alexnet.classifier = nn.Linear(num_ftrs, 2)
alexnet = alexnet.to(device)

# Setting Criterion
criterion = nn.CrossEntropyLoss()
# optimizer Adam with a learning rate of 0.0004
optimizer_alexnet = optim.Adam(alexnet.parameters(), lr=0.0004)
# Decay LR every 10 epochs i.e. step size and with factor 0.1 i.e. gamma
exp_lr_scheduler_alexnet = lr_scheduler.StepLR(optimizer_alexnet, step_size=10, gamma=0.1)

alexnet = train_model(alexnet, criterion, optimizer_alexnet, exp_lr_scheduler_alexnet,num_epochs=30)

eval_metrics(alexnet)

"""### ***Quantum Transfer Learning***"""

qubits = 4                  # Number of qubits required
batch_size = 4              # samples to be trained in each step
qdepth = 6                  # number of varaitional layers of the quantum circuit
qdelta = 0.01               # quantum weights spread
start_time = time.time()    # Start of the computation timer

dev = qml.device("default.qubit", wires= qubits)

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

def H_layer(nqubits):
    
    # layer of single - qubit Hadamard gates
    for idx in range(nqubits):
        qml.Hadamard(wires=idx)

def RY_layer(w):

    # Layer of parametrized qubit rotations around the y axis
    for idx, element in enumerate(w):
        qml.RY(element, wires=idx)

def entangling_layer(nqubits):
    # Layer of CNOTs followed by another shifted layer of CNOT
    
    for i in range(0, nqubits - 1, 2):  # Loop over even indices
        qml.CNOT(wires=[i, i + 1])
    for i in range(1, nqubits - 1, 2):  # Loop over odd indices
        qml.CNOT(wires=[i, i + 1])

@qml.qnode(dev, interface="torch")
def quantum_net(q_features, qweights):
    # Reshaping weights with respect to qdepth and qubits
    qweights = qweights.reshape(qdepth, qubits)
    H_layer(qubits)
    # Embedding features into the quantum node initiated
    RY_layer(q_features)
    # trainable variational layers put in sequence
    for k in range(qdepth):
        entangling_layer(qubits)
        RY_layer(qweights[k])
    # Expectation values in the Z basis
    exp_vals = [qml.expval(qml.PauliZ(position)) for position in range(qubits)]
    return tuple(exp_vals)

class DressedQuantumNet(nn.Module):
    # Using torch module to implement a dressed quantum net
    # this replaces the fully-connected layer of the pretrained model
    def __init__(self):
        
        # A dressed layout is formed
        # A classical pre-processing layer, an parametric layer and an post-processing layers are defined
        super().__init__()
        self.pre_net = nn.Linear(512, qubits)
        self.q_params = nn.Parameter(qdelta * torch.randn(qdepth * qubits))
        self.post_net = nn.Linear(qubits, 2)

    def forward(self, input_features):

        # the input features are obtained
        # Reducing the feature dimensions from 512 to 4 
        pre = self.pre_net(input_features)
        #  using the activation fuction tanh and constant scaling
        q_input = torch.tanh(pre) * np.pi / 2.0

        # Each Element is passed through the Quantum circuit and is appended to q_output
        q_output = torch.Tensor(0, qubits)
        q_output = q_output.to(device)
        for element in q_input:
            q_output_element = quantum_net(element, self.q_params).float().unsqueeze(0)
            q_output = torch.cat((q_output, q_output_element))

        # Output from the postprocessing layer
        return self.post_net(q_output)

"""####**Resnet18**"""

# loading the resnet18 pretrained model from torchvision
resnet_hybrid = torchvision.models.resnet18(pretrained=True)

for param in resnet_hybrid.parameters():
    param.requires_grad = False

# Replacing the resnet_hybrid.fc which is the last layer with dressed quantum network
resnet_hybrid.fc = DressedQuantumNet()
resnet_hybrid = resnet_hybrid.to(device)

criterion = nn.CrossEntropyLoss()
optimizer_hybrid_resnet = optim.Adam(resnet_hybrid.parameters(), lr=0.0004)
exp_lr_scheduler_resnet = lr_scheduler.StepLR(optimizer_hybrid_resnet, step_size=10, gamma=0.1)
resnet_hybrid = train_model(resnet_hybrid, criterion, optimizer_hybrid_resnet, exp_lr_scheduler, num_epochs=30)

eval_metrics(resnet_hybrid)

"""####**VGG16**"""

class DressedQuantumNet_vgg16(nn.Module):
    # Using torch module to implement a dressed quantum net
    # this replaces the fully-connected layer of the pretrained model
    def __init__(self):
        
        # A dressed layout is formed
        # A classical pre-processing layer, an parametric layer and an post-processing layers are defined
        super().__init__()
        self.pre_net = nn.Linear(25088, qubits)
        self.q_params = nn.Parameter(qdelta * torch.randn(qdepth * qubits))
        self.post_net = nn.Linear(qubits, 2)

    def forward(self, input_features):

        # the input features are obtained
        # Reducing the feature dimensions from 25088 to 4 
        pre = self.pre_net(input_features)
        #  using the activation fuction tanh and constant scaling
        q_input = torch.tanh(pre) * np.pi / 2.0

        # Each Element is passed through the Quantum circuit and is appended to q_output
        q_output = torch.Tensor(0, qubits)
        q_output = q_output.to(device)
        for element in q_input:
            q_output_element = quantum_net(element, self.q_params).float().unsqueeze(0)
            q_output = torch.cat((q_output, q_output_element))

        # Output from the postprocessing layer
        return self.post_net(q_output)

# loading the vgg16 pretrained model from torchvision
vgg16_hybrid = torchvision.models.vgg16(pretrained=True)

for param in vgg16_hybrid.parameters():
    param.requires_grad = False

# Replacing the vgg16_hybrid.classifier which is the last layer with dressed quantum network
vgg16_hybrid.classifier = DressedQuantumNet_vgg16()

vgg16_hybrid = vgg16_hybrid.to(device)

criterion = nn.CrossEntropyLoss()
optimizer_hybrid_vgg16 = optim.Adam(vgg16_hybrid.parameters(), lr=0.0004)
exp_lr_scheduler_vgg16 = lr_scheduler.StepLR(optimizer_hybrid_vgg16, step_size=10, gamma=0.1)
vgg16_hybrid = train_model(vgg16_hybrid, criterion, optimizer_hybrid_vgg16, exp_lr_scheduler_vgg16, num_epochs=30)

eval_metrics(vgg16_hybrid)

"""####**Densenet**"""

class DressedQuantumNet_densenet(nn.Module):
    # Using torch module to implement a dressed quantum net
    # this replaces the fully-connected layer of the pretrained model
    def __init__(self):
        
        # A dressed layout is formed
        # A classical pre-processing layer, an parametric layer and an post-processing layers are defined
        super().__init__()
        self.pre_net = nn.Linear(1024, qubits)
        self.q_params = nn.Parameter(qdelta * torch.randn(qdepth * qubits))
        self.post_net = nn.Linear(qubits, 2)

    def forward(self, input_features):

        # the input features are obtained
        # Reducing the feature dimensions from 1024 to 4 
        pre = self.pre_net(input_features)
        #  using the activation fuction tanh and constant scaling
        q_input = torch.tanh(pre) * np.pi / 2.0

        # Each Element is passed through the Quantum circuit and is appended to q_output
        q_output = torch.Tensor(0, qubits)
        q_output = q_output.to(device)
        for element in q_input:
            q_output_element = quantum_net(element, self.q_params).float().unsqueeze(0)
            q_output = torch.cat((q_output, q_output_element))

        # Output from the postprocessing layer
        return self.post_net(q_output)

# Loading the densenet121 pretrained model from torchvision
densenet_hybrid = torchvision.models.densenet121(pretrained=True)

for param in densenet_hybrid.parameters():
    param.requires_grad = False

# Replacing the densenet_hybrid.classifier which is the last layer with dressed quantum network
densenet_hybrid.classifier = DressedQuantumNet_densenet()

densenet_hybrid = densenet_hybrid.to(device)

criterion = nn.CrossEntropyLoss()
optimizer_hybrid_densenet = optim.Adam(densenet_hybrid.parameters(), lr=0.0004)
exp_lr_scheduler_densenet = lr_scheduler.StepLR(optimizer_hybrid_densenet, step_size=10, gamma=0.1)
densenet_hybrid = train_model(densenet_hybrid, criterion, optimizer_hybrid_densenet, exp_lr_scheduler_densenet, num_epochs=30)

eval_metrics(densenet_hybrid)

"""####**Alexnet**"""

class DressedQuantumNet_alexnet(nn.Module):
    # Using torch module to implement a dressed quantum net
    # this replaces the fully-connected layer of the pretrained model
    def __init__(self):
        
        # A dressed layout is formed
        # A classical pre-processing layer, an parametric layer and an post-processing layers are defined
        super().__init__()
        self.pre_net = nn.Linear(9216, qubits)
        self.q_params = nn.Parameter(qdelta * torch.randn(qdepth * qubits))
        self.post_net = nn.Linear(qubits, 2)

    def forward(self, input_features):

        # the input features are obtained
        # Reducing the feature dimensions from 4096 to 4 
        pre = self.pre_net(input_features)
        #  using the activation fuction tanh and constant scaling
        q_input = torch.tanh(pre) * np.pi / 2.0

        # Each Element is passed through the Quantum circuit and is appended to q_output
        q_output = torch.Tensor(0, qubits)
        q_output = q_output.to(device)
        for element in q_input:
            q_output_element = quantum_net(element, self.q_params).float().unsqueeze(0)
            q_output = torch.cat((q_output, q_output_element))

        # Output from the postprocessing layer
        return self.post_net(q_output)

# Loading the alexnet pretrained model from torchvision
alexnet_hybrid = torchvision.models.alexnet(pretrained=True)

for param in alexnet_hybrid.parameters():
    param.requires_grad = False

# Replacing the alexnet_hybrid.classifier which is the last layer with dressed quantum network
alexnet_hybrid.classifier = DressedQuantumNet_alexnet()

alexnet_hybrid = alexnet_hybrid.to(device)

criterion = nn.CrossEntropyLoss()
optimizer_hybrid_alexnet = optim.Adam(alexnet_hybrid.parameters(), lr=0.0004)
exp_lr_scheduler_alexnet = lr_scheduler.StepLR(optimizer_hybrid_alexnet, step_size=10, gamma=0.1)
alexnet_hybrid = train_model(alexnet_hybrid, criterion, optimizer_hybrid_alexnet, exp_lr_scheduler_alexnet, num_epochs=30)

eval_metrics(alexnet_hybrid)