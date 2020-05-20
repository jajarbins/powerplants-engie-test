# Coding Challenge

Work in Progress, TODO :
- Add parts to README (API Logic Explanation ; Algorithm Explanation)
- dockerise



## Welcome !

This is my implementation of the coding challenge proposed by the IS team of the SPaaS team within ENGIE GEM

You can Find the description of the challenge [here](https://github.com/gem-spaas/powerplant-coding-challenge)

## How to run it ?

### Windows: 

Open a command Prompt.

Create a virtual environment with your favourite package manager and activate it. Python version should be 3.6 

Change directory to the project root. 

Then install the dependencies with the command: 
```bash
pip install -r requirements.txt
```
Finally, run Api.py file with python, the RESTFul API will be exposed at http://127.0.0.1:8888/

## How to test it ?

Just send an http post request to your localhost at port 8888 containing a json as you can find 
at  [this address](https://github.com/gem-spaas/powerplant-coding-challenge/tree/master/example_payloads/) 
or in the __init__.py file of the tests folder of this project.

## API Logic Explanation

Basically, the Api: 
- Extract the data of the incoming request
- Check if it contains a JSON of the expected form
- Classify the powerplants in the [merit order](https://en.wikipedia.org/wiki/Merit_order) taking into account the CO2 price
- Estimate and set the production of each of the powerplant to fill the load
- Return a list of dictionary containing the powerplants name and their production

## Algorithm Explanation

In this API, we use an algorithm to find the production of the powerplants in order to fill the load and minimize the cost
of producing electricity. You can find it in the update_powerplants_production method of PowerFinder class.

The Algorithms takes a list of Powerplant object sorted in the merit order and sum their maximum production until the 
total production is equal to the load.

If a portion of the production of a powerplant is needed to fill the load, only this portion is used. 

If the minimumm production of a powerplant is higher than the difference between the total production and the load, then
it lower the production of the previous powerplant so that the minimum production of the current production can fill the 
load. 
