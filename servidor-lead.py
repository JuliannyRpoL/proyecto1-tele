from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

data = {}
followers = []

@app.route('/', methods=['POST'])
def setValue():
    if request.method == 'POST' and 'key' in request.json and 'value' in request.json:
        try:
            if(request.json['key'] not in data):
                data[request.json['key']] = [request.json['value']]
            else:
                data[request.json['key']].append(request.json['value'])

            for follower in followers: #por cada follower hace la petición de escritura
                requests.post(follower, json=request.json)

            return jsonify('Valor almacenado exitosamente'), 201

        except:
            return jsonify("error almacenando el dato"), 400

    return jsonify("error saving data, missing key or value"), 400


@app.route('/value', methods=['GET'])
def getValue():
    if(request.args.get('key')):
        try:    
            return jsonify(data[request.args.get('key')]), 200

        except:
            return jsonify("Error getting data, key doesn't exist in server"), 400

    return jsonify("Error getting data, missing key in queryparam"), 400


@app.route('/', methods=['GET'])
def getValues():
    try:    
        return jsonify(data), 200

    except:
        return jsonify("Error getting data"), 400


@app.route('/follower', methods=['POST'])
def addFollower():
    if request.method == 'POST' and 'url' in request.json:
        if(request.json['url'] not in followers):
            if(bool(data)): #si data no es vacía, hace petición para copiar los datos existentes al nuevo follower
                requests.post(request.json["url"]+"values", json={"info": data})

            followers.append(request.json["url"])

            return jsonify("Added follower successfully"), 201
        else:
            return jsonify("Error updating follower, follower alredy exist"), 400
    else:
        return jsonify("Error updating follower, error in data"), 400


if __name__ == "__main__":
    port = input()
    app.run(port=port, debug=True, host="0.0.0.0")