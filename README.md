# desafioProximaPorta

The challenge was to create an API to calculate the cost of a trip.

## 1. First API.
### The first API was an API to save new Maps.
#### Acces URL: "/addMap"
#### Method: POST

|Parameters|obligatoriness|
|---|---|
|mapName|Obligatory|
|paths|Obligatory|

##### Examples of paths format:

```
[
[A,B,10]
[A,C,15]
[B,D,5]
[B,C,20]
]
```
## 2. Second API.
### The second API was an API to retrieve the Maps saved.
#### Acces URL: /retrievePaths/{mapName}
#### Method: GET

It's necessary to put the name of the map inside the {} and the API will return the paths of the map with the chosen name.

## 3. Third API
### The third API is an API to make the cost calculation of the shortest path with dijkstra function.
#### Acces URL: /costAndPathCalculation
#### Method: POST

|Parameters|obligatoriness|
|---|---|
|mapName|Obligatory|
|startPoint|Obligatory|
|endPoint|Obligatory|
|autonomy|Obligatory|
|valuePerLiter|Obligatory|

Example of return with the Cost, Path and Distance: 
"The shortest route from A to D is A -> B -> D with a total distance of 30 and it will cost $15"