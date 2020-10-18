from botocore.parsers import JSONParser
from chalice import Chalice
from chalice.app import BadRequestError, Response
import boto3
import json

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
    