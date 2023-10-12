import certifi
from flask import Flask, request, send_file, render_template
import os
from flask_pymongo import PyMongo
from flask_cors import CORS
from bson.json_util import dumps
from bson.json_util import loads
import json
from bson.objectid import ObjectId


app = Flask(__name__)
app.debug = True
CORS(app)
uri_mongo = "mongodb://F28_LC_APPS_so:k1mYwLd3h1zM51w@d1lc1mon042.ger.corp.intel.com:7357,d2lc1mon042.ger.corp.intel.com:7357,d3lc1mon042.ger.corp.intel.com:7357/?authMechanism=DEFAULT&authSource=F28_LC_APPS&tls=true&tlsCAFile=localdevCert.pem"
uri_mongo_dbaas = "mongodb://F28_LC_APPS_so:k1mYwLd3h1zM51w@d1lc1mon042.ger.corp.intel.com:7357,d2lc1mon042.ger.corp.intel.com:7357,d3lc1mon042.ger.corp.intel.com:7357/F28_LC_APPS?ssl=true&replicaSet=mongo7357"
mongo = PyMongo(app, uri=uri_mongo_dbaas)
db = mongo.db



@app.route('/')
def home():
    return render_template('index.html')


@app.route("/form", methods=['POST'])
def new_item():
    if request.method == 'POST':
        item = request.form.to_dict()
        file_image = request.files['image']
        item['image'] = file_image.filename
        if os.path.exists("./images/" + file_image.filename):
            return '{"status":"Existing image file name"}', 500
        db.items.insert_one(item)
        file_image.save("./images/" + file_image.filename)
        return '{"status":"success"}'


@app.route("/allitems")
def all_items():
    items = db.items.find()
    items_dict = (loads(dumps(items)))
    return json.dumps(items_dict, default=str)


@app.route("/files/<filename>", methods=['GET'])
def get_file(filename):
    return send_file("./images/" + filename)


@app.route("/delete/<path:item_id>", methods=['DELETE'])
def del_item(item_id):
    item_cursor = db.items.find({"_id": ObjectId(item_id)})
    image_to_delete = item_cursor[0]['image']
    db.items.delete_one({"_id": ObjectId(item_id)})
    try:
        os.remove("./images/" + image_to_delete)
    except:
        return '{"status":"file not exists"}', 500

    return '{"status":"success"}', 200


if __name__ == '__main__':
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
