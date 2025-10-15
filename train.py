import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from jarvis1 import tokenize, stem, bag_of_words, load_intents
from model import NeuralNet
import json
import random
import pandas as pd
from sklearn.model_selection import train_test_split


# Load dataset
intents = load_intents("C:\\Users\\rudra\\OneDrive\\Documents\\python\\jarvis\\intents.json")

all_words = []
tags = []
xy = []

# Collect all words and tags
for intent in intents['intents']:
    tag = intent['tag']
    tags.append(tag)
    for pattern in intent['patterns']:
        w = tokenize(pattern)
        all_words.extend(w)
        xy.append((w, tag))

# Stem and remove duplicates
ignore_words = ['?', '!', '.', ',']
all_words = [stem(w) for w in all_words if w not in ignore_words]
all_words = sorted(set(all_words))
tags = sorted(set(tags))

# Training data
X_train = []
y_train = []

for (pattern_sentence, tag) in xy:
    bag = bag_of_words(pattern_sentence, all_words)
    X_train.append(bag)
    y_train.append(tags.index(tag))

X_train = np.array(X_train)
y_train = np.array(y_train)

# Hyperparameters
input_size = len(all_words)
hidden_size = 8
output_size = len(tags)
learning_rate = 0.001
num_epochs = 5000

# Model, loss, optimizer
model = NeuralNet(input_size, hidden_size, output_size)
checkpoint = torch.load("data.pth")
model.load_state_dict(checkpoint["model_state"])
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=learning_rate)

# Training loop
for epoch in range(num_epochs):
    X = torch.from_numpy(X_train).float()
    y = torch.from_numpy(y_train).long()

    # Forward pass
    outputs = model(X)
    loss = criterion(outputs, y)

    # Backward pass
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if (epoch + 1) % 100 == 0:
        print(f'Epoch [{epoch + 1}/{num_epochs}], Loss: {loss.item():.4f}')

# Save model
data = {
    "model_state": model.state_dict(),
    "input_size": input_size,
    "hidden_size": hidden_size,
    "output_size": output_size,
    "all_words": all_words,
    "tags": tags
}

FILE = "data.pth"
torch.save(data, FILE)
print(f"Training complete. Model saved to {FILE}")
