import json
from random import randrange
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

dataServers = {}
leadersWithFollowers = []
availableServers = []

#----------------endpoints to manage data-----------------

@app.route('/', methods=['POST'])
def setValue():
    if request.method == 'POST' and 'key' in request.json and 'value' in request.json:
        try:
            if(len(leadersWithFollowers) != 0): #si hay nodos en la red
                leader = randrange(len(leadersWithFollowers)) #numero random entre 0 y el num particiones - 1
                requests.post(leadersWithFollowers[leader]["url"], json=request.json) #envía petición de escritura a leader

                newDataServers = [leadersWithFollowers[leader]["url"]]
                for follower in leadersWithFollowers[leader]["followers"]:
                    newDataServers.append(follower)

                if(request.json['key'] not in dataServers): #si la key es nueva, añade los posibles nodos donde se puede hallar
                    dataServers[request.json['key']] = [ newDataServers ]
                elif(newDataServers not in dataServers[request.json['key']]): #si los nodos propuestos no se encuentran mapeados se agregan
                    dataServers[request.json['key']].append(newDataServers)

                return jsonify(f'Valor almacenado exitosamente en la particion {leader + 1}'), 201
            else:
                return jsonify("error almacenando el dato, no hay servers data"), 400

        except:
            return jsonify("error almacenando el dato"), 400

    return jsonify("error almacenando el dato"), 400


@app.route('/value', methods=['GET'])
def getValue():
    key = request.args.get('key')
    if(key and key in dataServers):
        try:
            responseAll = []
            for partition in dataServers[key]:
                nodo = randrange(len(partition))
                response = requests.get(f'{partition[nodo]}value', params={'key': key})
                response = json.loads(response.content)
                responseAll = responseAll + response

            return jsonify(responseAll), 200
        except:
            return jsonify("error obteniendo datos, intente nuevamente"), 500


    return jsonify("error obteniendo datos, key no encontrada"), 400


@app.route('/dataServers', methods=['GET'])
def getDataServers():
    try:
        return jsonify(dataServers), 200

    except:
        return jsonify("Error getting data servers"), 400


#----------------endpoints to manage server network-----------------

@app.route('/server', methods=['POST'])
def newServer():
    if request.method == 'POST' and 'url' in request.json:
        #try:
            if(request.json['url'] not in availableServers): #si el nodo no se encuentra ya en la red
                if(len(leadersWithFollowers) < 2): #los primeros dos nodos serán leaders de particiones
                    leadersWithFollowers.append({
                        'url': request.json['url'],
                        'followers': []
                    }) #se agrega leader a la red
                    availableServers.append(request.json['url'])

                    return jsonify(f'Leader # {len(leadersWithFollowers)} añadido exitosamente'), 201
                else:
                    minFollowers = 100000
                    leaderSelected = -1
                    for idx in range(len(leadersWithFollowers)): #ciclo para ver cual particion tiene menos replicas
                        leader = leadersWithFollowers[idx]
                        followersNumber = len(leader['followers'])
                        if(minFollowers > followersNumber):
                            leaderSelected = idx
                            minFollowers = followersNumber

                    requests.post(leadersWithFollowers[leaderSelected]["url"]+"follower", json=request.json) #se le avisa al leader que tiene nuevo follower
                    leadersWithFollowers[leaderSelected]['followers'].append(request.json['url']) #se agrega follower a leader
                    availableServers.append(request.json['url'])

                    for key in dataServers: #ciclo para agregar follower nuevo a las opciones donde se puede leer la data
                        for partitions in dataServers[key]:
                            if(leadersWithFollowers[leaderSelected]["url"] in partitions):
                                partitions.append(request.json['url'])
                                break

                    return jsonify(f'Follower añadido exitosamente a leader # {leaderSelected + 1}'), 201
            else:
                return jsonify("error añadiendo server a la red, ya existe en la red"), 400
        #except:

    return jsonify("error añadiendo server a la red, datos incorrectos"), 400


@app.route('/leader', methods=['POST'])
def newLeader():
    if request.method == 'POST' and 'url' in request.json:
        #try:
            if(request.json['url'] not in availableServers):
                leadersWithFollowers.append({
                    'url': request.json['url'],
                    'followers': []
                })

                availableServers.append(request.json['url'])

                return jsonify(f'Leader # {len(leadersWithFollowers)} añadido exitosamente'), 201
            else:
                return jsonify("error añadiendo leader a la red, ya existe server en la red"), 400

        # except:

    return jsonify("error añadiendo leader a la red, datos incorrectos"), 400


@app.route('/follower', methods=['POST'])
def newFollower():
    if request.method == 'POST' and 'url' in request.json and 'leader' in request.json:
        #try:
            if(request.json['url'] not in availableServers):
                addedFollower = -1

                for idx in range(len(leadersWithFollowers)): #ciclo para buscar a que leader pertenece la id y agregar follower
                    leader = leadersWithFollowers[idx]
                    if(leader['url'] == request.json['leader']):
                        requests.post(leader["url"]+"follower", json=request.json)
                        leader['followers'].append(request.json['url'])

                        for key in dataServers:
                            for partitions in dataServers[key]:
                                if(leader["url"] in partitions):
                                    partitions.append(request.json['url'])
                                    break

                        addedFollower = idx
                        break

                if(addedFollower != -1):
                    availableServers.append(request.json['url'])

                    return jsonify(f'Follower añadido exitosamente a leader # {addedFollower + 1}'), 201
                else:
                    return jsonify("error añadiendo server a la red, leader no existe"), 400
            else:
                return jsonify("error añadiendo follower a la red, ya existe server en la red"), 400
        # except:

    return jsonify("error añadiendo follower a la red, datos incorrectos"), 400

@app.route('/servers', methods=['GET'])
def getServers():
    try:
        return jsonify(leadersWithFollowers), 200

    except:
        return jsonify("Error getting servers"), 400


if __name__ == "__main__":
    app.run(port=3000, debug=True, host="0.0.0.0")
