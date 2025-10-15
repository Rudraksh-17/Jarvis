import torch
import torch.nn as nn
import json
from jarvis1 import tokenize, stem, bag_of_words
from model import NeuralNet

# Load model
data = torch.load("data.pth")

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data["all_words"]
tags = data["tags"]

model = NeuralNet(input_size, hidden_size, output_size)
model.load_state_dict(data["model_state"])
model.eval()

def predict_class(sentence):
    sentence = tokenize(sentence)
    X = bag_of_words(sentence, all_words)
    X = torch.from_numpy(X).float()

    output = model(X)
    _, predicted = torch.max(output, dim=0)
    tag = tags[predicted.item()]
    return tag

if __name__ == "__main__":
    while True:
        sentence = input("You: ")
        if sentence.lower() in ["quit", "exit"]:
            break
        tag = predict_class(sentence)
        print(f"Predicted intent: {tag}")
