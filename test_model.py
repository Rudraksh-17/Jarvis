from ml_model import predict_class

# Test some commands
test_sentences = [
    "hello",
    "can you open google",
    "what time is it",
    "shutdown my computer",
    "tell me a joke",
    "quit"
]

for sentence in test_sentences:
    intent = predict_class(sentence)
    print(f"Input: {sentence} --> Predicted Intent: {intent}")
