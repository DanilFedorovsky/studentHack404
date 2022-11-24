from flask import Flask, request
from flask.json import jsonify
import json
import torch
import model_architecture
import load_data

# Load data
X,Y = load_data.load()

# Load model 
PATH = "model.pt"
state_dict = torch.load(PATH)

from collections import OrderedDict
new_state_dict = OrderedDict()
for k, v in state_dict.items():
    name = k[7:] # remove `module.` from state dict
    new_state_dict[name] = v
# load params
model = model_architecture.Ensemble()
model.load_state_dict(new_state_dict)
model.eval()

def get_lamp_color(y_val):
    if torch.argmax(y_val[0]) == torch.Tensor([2]):
        return "RED"
    elif torch.argmax(y_val[0]) == torch.Tensor([1]):
        return "YELLOW"
    else:
        return "GREEN"

app = Flask(__name__)
@app.route('/')
def index():
    input = int(request.args.get('nr'))
    print(input)
    pred = model(torch.stack([X[input]]))
    print(pred)
    color = get_lamp_color(pred)
    print(color)

    return jsonify({'prediction': str(pred), 'classification': str(color),'input':str(X[input])})

app.run(debug=True, use_reloader=False)