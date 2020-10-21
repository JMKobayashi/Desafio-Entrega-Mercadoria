from botocore.parsers import JSONParser
from chalice import Chalice
from chalice.app import BadRequestError, Response
import boto3
import json
import re
from dijkstra.dijkstra import DijkstraSPF
from dijkstra.graph import Graph

app = Chalice(app_name='desafioProximaPorta')

DDB = boto3.client('dynamodb')
# API to save new Maps in the database
@app.route('/addMap', methods=['POST'])
def addMap():

    # Get the Map name and paths
    map = app.current_request.json_body

    # If don't receive a Map raise a BadRequestError
    if map == "" or map == None or not map:
        raise BadRequestError("Missing Map")

    # Verifying the format of paths with regular expression
    regEx = r"\[(\[\w\,\w\,\d+\]\,)+\[\w\,\w\,\d+\]\]"
    result = re.match(regEx,map['paths'])
    if(result == None):
        raise BadRequestError("Wrong Path format")

    # If one of the variable is missing raise a BadRequestError
    if ((map['mapName'] == "" or map['mapName'] == None or not map['mapName']) or 
        (map['paths'] == "" or map['paths'] == None or not map['paths'])):
        raise BadRequestError("Map name or paths not found")

    mapName = map['mapName']
    paths = json.dumps(map['paths'])
    
    # Insert map in the database
    DDB.put_item(
        TableName="Maps",
        Item={
            "mapName":{'S':mapName},
            "paths":{'S':paths}
        }
    )
    # Return Map
    return {"map": map}

# API to retrieve Paths from the database
@app.route('/retrievePaths/{mapName}')
def retrievePaths(mapName):
    
    # Retrieve Map from the database
    map = DDB.get_item(TableName="Maps",Key={'mapName':{'S':mapName}})
    
    # If there is no map with the name provided raise a BadRequestError 
    if map == "" or map == None or not map:
        raise BadRequestError("mapName was not found in the database")
    
    # Get the Map Paths from the map variable and encode in JSON format to return
    paths = json.loads(map['Item']['paths']['S'])

    # Return paths
    return {'Paths':paths}

# API to calculate the Cost, Path and Distance
@app.route('/costAndPathCalculation', methods=['POST'])
def costCalculation():

    # Get the Map Name, Start Point, End Point, Autonomy and Value Per Liter
    data = app.current_request.json_body
    if ((data['mapName'] == "" or data['mapName'] == None or not data['mapName']) or 
        (data['startPoint'] == "" or data['startPoint'] == None or not data['startPoint']) or
        (data['endPoint'] == "" or data['endPoint'] == None or not data['endPoint']) or
        (data['autonomy'] == "" or data['autonomy'] == None or not data['autonomy']) or
        (data['valuePerLiter'] == "" or data['valuePerLiter'] == None) or not data['valuePerLiter']):
        raise BadRequestError('One or more parameters are missing!')

    # Assign parameters to variables
    mapName = data['mapName']
    startPoint = data['startPoint']
    autonomy = int(data['autonomy'])
    endPoint = data['endPoint']
    valuePerLiter = float(data['valuePerLiter'])


    # Retrieve paths from the database
    paths = retrievePaths(mapName)
    paths = paths['Paths']
    
    # Checking if starPoint and endPoint exist in paths
    startPointCheck = re.findall(startPoint,paths)
    if startPointCheck == []:
        raise BadRequestError("Start Point doesn't exist in the map")
    endPointCheck = re.findall(endPoint,paths)
    if not endPointCheck:
        raise BadRequestError("End Point doesn't exist in the map")

    #regEx = r"\[\w+\,\w+\,\d+\]"
    paths = list(re.findall(regEx,paths))


    # Create Graph with the paths retrieved from the database
    graph = Graph()
    for i in range(len(paths)):
        edges = re.findall(r"\w+",paths[i])

        graph.add_edge(edges[0],edges[1],int(edges[2]))

    # Setting the initial parameters in the Dijkstra function
    dijkstra = DijkstraSPF(graph, startPoint)

    # Calculating the distance to the End Point
    distance = dijkstra.get_distance(endPoint)

    # Creating a string with the shortest path
    path = str(" -> ".join(dijkstra.get_path(endPoint)))
    
    # Calculating the final cost of the trip
    cost = (distance / autonomy)*valuePerLiter

    # Creating a string with all informations
    returnText = str("The shortest route from "+ startPoint +" to "+ endPoint
                    +" is "+ path + " with a total distance of "+ str(distance)
                    +" and it will cost $"+ str(cost))

    return {'Cost':returnText}

