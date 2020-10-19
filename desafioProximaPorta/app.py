from botocore.parsers import JSONParser
from chalice import Chalice
from chalice.app import BadRequestError, Response
import boto3
import json
import re
import dijkstra
from dijkstra.dijkstra import DijkstraSPF
from dijkstra.graph import Graph

app = Chalice(app_name='desafioProximaPorta')

DDB = boto3.client('dynamodb')

@app.route('/addMap', methods=['POST'])
def addMap():
    # Get the Map name and paths
    map = app.current_request.json_body

    # If don't receive a Map raise a BadRequestError
    if not map:
        raise BadRequestError("Missing Map")
    mapName = map['mapName']
    paths = json.dumps(map['paths'])
    if not mapName and not paths:
        raise BadRequestError("Map name or paths not found")
    
    DDB.put_item(
        TableName="Maps",
        Item={
            "mapName":{'S':mapName},
            "paths":{'S':paths}
        }
    )
    return {"map": map}

@app.route('/retrievePaths/{mapName}')
def retrievePaths(mapName):
    map = DDB.get_item(TableName="Maps",Key={'mapName':{'S':mapName}})
    if not map:
        BadRequestError("mapName was not found in the database")
    paths = json.loads(map['Item']['paths']['S'])
    return {'Paths':paths}
    
@app.route('/costCalculation', methods=['POST'])
def costCalculation():
    data = app.current_request.json_body
    if (not data['mapName'] or not data['startPoint'] or 
        not data['startPoint'] or not data['autonomy'] or 
        not data['endPoint'] or not data['valuePerLiter']):
        BadRequestError('One or more parameters are missing!')


    mapName = data['mapName']
    startPoint = data['startPoint']
    autonomy = int(data['autonomy'])
    endPoint = data['endPoint']
    valuePerLiter = float(data['valuePerLiter'])


    
    paths = retrievePaths(mapName)
    paths = paths['Paths']
    regEx = r"\[\w+\,\w+\,\d+\]"
    paths = list(re.findall(regEx,paths))

    graph = Graph()
    for i in range(len(paths)):
        edges = re.findall(r"\w+",paths[i])

        graph.add_edge(edges[0],edges[1],int(edges[2]))

    dijkstra = DijkstraSPF(graph, startPoint)
    distance = dijkstra.get_distance(endPoint)
    path = str(" -> ".join(dijkstra.get_path(endPoint)))
    cost = (distance / autonomy)*valuePerLiter
    returnText = str("The shortest route from "+ startPoint +" to "+ endPoint
                    +" is "+ path + " with a total distance of "+ str(distance)
                    +" and it will cost $"+ str(cost))

    return {'Cost':returnText}