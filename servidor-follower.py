from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
#CORS(app, resources={r"/*": {"origins": "*"}})

data = {}

@app.route('/', methods=['POST'])
def setValue():
    if request.method == 'POST' and 'key' in request.json and 'value' in request.json:
        try:
            if(request.json['key'] not in data):
                data[request.json['key']] = [request.json['value']]
            else:
                data[request.json['key']].append(request.json['value'])

            return jsonify('Valor almacenado exitosamente'), 201

        except:
            return jsonify("error almacenando el dato"), 400
    
    return jsonify("error saving data, missing key or value"), 400


@app.route('/values', methods=['POST'])
def setAllValues():
    if request.method == 'POST' and 'info' in request.json:
        try:
            data['test'] = ['test']
            data.update(request.json['info'])
            del data['test']

            return jsonify('Valores almacenados exitosamente'), 201

        except:
            return jsonify("error almacenando el dato"), 400
    
    return jsonify("error saving data, missing data"), 400


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

if __name__ == "__main__":
    port = input()
    app.run(port=port, debug=True, host="0.0.0.0")