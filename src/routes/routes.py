import os
from base64 import b64encode
from io import BytesIO
from math import floor

import src.config as config
from flask import flash, render_template, request, url_for
from joblib import dump
from PIL import Image, UnidentifiedImageError
from src import app
from werkzeug.utils import redirect
from src.models import MobileNet
from glob import glob, iglob
from joblib import load


def get_image(img_byte):
    return Image.open(BytesIO(img_byte))


def get_encoded_img(img):
    return b64encode(img)


def retrieve_imgs_from_store():
    past_images = []
    list_images_stored = glob(os.path.join(config.IMG_STORE, "*.pkl"))
    num_images_in_gallery = (
        5 if len(list_images_stored) > 5 else len(list_images_stored)
    )
    pkl_files_in_gallery = sorted(
        iglob(os.path.join(config.IMG_STORE, "*.pkl")),
        key=os.path.getctime,
        reverse=True,
    )[:num_images_in_gallery]

    if len(list_images_stored) > 5:
        for _f in set(list_images_stored) - set(pkl_files_in_gallery):
            os.remove(os.path.join(config.IMG_STORE, _f))
    for pkl in pkl_files_in_gallery:
        _file = load(pkl)
        img_byte = BytesIO()
        _file["img_data"].save(img_byte, format="PNG")
        img_byte = img_byte.getvalue()
        _file[
            "img_data"
        ] = f"data:image/jpeg;base64,{get_encoded_img(img_byte).decode('utf-8')}"
        past_images.append(_file)
    return past_images


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/infer", methods=["POST", "GET"])
def success():
    if request.method == "POST":
        inf = []
        files = request.files.getlist("files[]")

        if len(files) == 0 | len(files) > 3:
            flash(f"You can only upload upto 3 images per upload", "danger")
            return redirect(url_for("index"))
        past_imgs = retrieve_imgs_from_store()
        for img_file in files:
            img_byte = img_file.read()
            try:
                img = get_image(img_byte)
            except UnidentifiedImageError:
                flash(f"Please Select file(s) to upload", "danger")
                return redirect(url_for("index"))
            encoded_img = get_encoded_img(img_byte)
            img_data = f"data:image/jpeg;base64,{encoded_img.decode('utf-8')}"
            inference, confidence = MobileNet().infer(img)
            # make a percentage with 2 decimal points
            confidence = floor(confidence * 10000) / 100

            # save the image + confidence pickle object in data_files
            dump(
                {"img_data": img, "confidence": confidence, "name": inference},
                os.path.join(
                    config.IMG_STORE, img_file.filename.split(".")[0] + ".pkl"
                ),
            )
            inf.append(
                {"name": inference, "confidence": confidence, "img_data": img_data}
            )
        # respond with the inference
        return render_template("inference.html", current_img=inf, past_img=past_imgs)
    return redirect(url_for("index"))
