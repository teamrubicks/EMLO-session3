from flask import Flask, render_template, request
from models import MobileNet
import os
from math import floor

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'

model = MobileNet()


def predict_model(f):
    saveLocation = f.filename
    f.save('static/img/'+saveLocation)
    inference, confidence = model.infer('static/img/'+saveLocation)
    # make a percentage with 2 decimal points
    confidence = floor(confidence * 10000) / 100
    # delete file after making an inference
    # os.remove(saveLocation)
    return inference,confidence
 
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/infer', methods=['POST'])
def success():
    if request.method == 'POST':
        uploaded_files = request.files.getlist("files[]")
        inferences=[]
        confidences=[]
        for i in uploaded_files:
            infer,conf = predict_model(i) 
            inferences.append(infer)
            confidences.append(str(conf))
        # respond with the inference
        return render_template('inference.html', name=inferences, confidence=confidences,images=uploaded_files,count=len(inferences))


if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get("PORT", 80))
    app.run(host='0.0.0.0', port=5001, debug=True)
