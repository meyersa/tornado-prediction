# Tornado Predictions

A machine learning project leveraging MIT's TorNet to predict tornado occurrences from satellite images using a 3D Convolutional Neural Network (CNN).

The goal of this project was to take MIT's work and train a 3D network, compared to the 2D networks that have been trained so far, with a better recall and precision. In the end, this was not as effective as planned due to the short length of this project. 

## Results
Although accuracy (0.9188) and AUC (0.8768) are high, they can be misleading. The low precision (0.4128) indicates a high rate of false positives, while the moderate recall (0.6074) shows the model's ability to capture true positives is limited. This makes sense considering the dataset is almost completely skewed to non tornadic data, meaning it just has to guess not tornado to achieve a high accuracy, when in reality it actually has a hard time finding tornados. 

| Metric            | Value |
|-------------------|------------|
| Accuracy          | 0.9188     |
| AUC               | 0.8768     |
| Loss              | 0.2712     |
| Precision         | 0.4128     |
| Recall            | 0.6074     |
| Learning Rate     | 5.0000e-04 |

## Procurement 

Data is downloaded from Zenodo and uploaded to BackBlaze S3, as seen in `populate_records.py`. From there, the downloads are proxied through Cloudflare to avoid egress into the training boxes. 

## Processing 

With the datadownloaded, it is converted in TFRecords through a datapipeline that also removes and flags missing data, slightly normalizes the precision, and then makes it easier to read for the end GPUs. 
 

## Training 

The model consists of a 3d CNN with:
- Batch Normalization: For faster convergence and stable training
- Leaky ReLU: Activations to avoid dying neurons and enhancing gradient flow
- Spatial Dropout: Prevent overfitting by dropping feature maps randomly
- Global Max Pooling: Reduce feature dimensions while retaining relevant information to reduce model size
- L2 Regularization: Add weight penalties to improve generalization and also prevent overfitting
- Class Weights: Utilize exact class sizes to balance properly for precision
- EarlyStopping: Maximize EPOCHs
- ReduceLROnPlateau: Only improve learning when model is increasing in performance
- Checkpoining: Save best model
