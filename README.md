## ***Quantum-Computing***
## ***Building Quantum Hybrid Models from scratch up to asses the advantages of quantum for real-world applications***

### ***Network Implementation***

#### ***Q-C Approach***

The constructed model has a total of 832,305 parameters, 448 of which are untrainable. The Conv2D layer consists of a kernel of size 3x3 with padding, other hidden layers include a maxpooling layer with a pool size and strides of 2x2, a batch normalisation layer, and a dropout layer. The output layer is added at the end after the final fully connected dense layer, which is a layer outputting the probabilities using a sigmoid activation function, a detailed figure of the constructed model can be seen in figure 6. Further, Images from a dataset must be pre-processed through a quantum circuit, which processes small regions of the input image in parallel and produces an output image of the same pixel but assigned to different channels. In this case, the output image from the circuit is a four-channel image.

<p align="center">
<img width="845" alt="CNN Vizualization" src="https://user-images.githubusercontent.com/66077662/193477135-194a9937-b705-4455-8deb-eeaf9c500837.png">
</p>
<h5 align="center">CNN Model</h5>

First, a new empty axis is added to all the images in the dataset to accommodate the additional channels that are going to be added to the image. The pennylane package creates a default quantum device. A function is defined to pre-process the images through the quantum circuit, The python code to the process is given in Appendix B. The images are shrunk to 64x64 for the convenience of pre-processing the basic images using a quantum circuit. Both datasets of normal images and pre- processed images consist of 1000 images because the quantum circuit takes a long time to pre-process images and even though the traditional method can accommodate several thousand images to be trained on the network, it is done to keep it fair to compare both model performances to each other. Both the models are compiled with Adam as optimiser and mean squared error as loss.

#### ***C – Q Approach***

Transfer learning is used in this strategy, which uses models that have already been trained to do a job. Resnet18, Vgg16, Densenet, and Alexnet were chosen in this research since they are among the top pretrained models shown to be efficient for image categorization. As was already said, a quantum layer, which is a dressed quantum net, takes the place of the FC layer or classifier in these models. A standard A qubit device dev is initialised with pennylane, and a torch device cuda is initialised with torch module. Additionally, a layer with single Hadamard gates with four wires is defined, as the number of qubits in this case is four; and a quantum entangling layer with four qubits is defined. All the previously mentioned functions are put together to make a new function for a quantum network. The weights are reshaped so that qdepth and qubits are the x and y dimensions, respectively. In addition, a class called DressedQuantumNet has been developed, which includes pre-processing, parametric, and post-processing layers.


After obtaining the model from Pytorch, the parameters and weights to be trained are frozen, and only the fc layer, which is now a quantum layer, is trained with the image dataset using a cross entropy loss and an Adam optimizer with a learning rate of 0.0004 and is scheduled to decrease by a factor of 0.1, i.e., gamma, every 10 steps using a lr scheduler. Both the pretrained models and the quantum layer replacement pretrained models are trained on the picture dataset for 30 epochs with a batch size of 4 before being assessed and compared.

### ***Conclusions***

The Quantum - Classical Approach produces similar results as traditional CNN models but appears to be more stable and has shorter computing times, which could be advantageous when training the model on large datasets. However, the pre- processing of the datasets takes a long time and is not feasible for large datasets with high resolution images, this contradicts the whole premise of using quantum computing to anticipate climate change, which requires speedy real-time processing and dealing with massive information.

For the Classical – Quantum Approach With the exception of the VGG16 pretrained network, all pretrained models perform similarly and exhibit a fall in recall when the FC layer is replaced with a dressed quantum network, indicating actual negative rates. Furthermore, models with quantum layers need more training time than conventional models, in this case the classical pretrained models for image classification tasks are proven to be better.

To conclude, hybrid models with quantum layers could be trained on vast amounts of data with either poor or equivalent results, or they can be trained on smaller amounts of quantum pre-processed data with more accurate predictions. There is no ideal equilibrium between the two, and quantum computing must find a perfect balance.

#### ***The process of implementation of the networks and quantum integration is explanined in the report document **"Samireddik.pdf"** in detail with all the supporting python files and Results, please check it out***
