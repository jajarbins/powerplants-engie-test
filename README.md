# Coding Challenge

Work in Progress: 
- Add parts to README (how to test webhook/websocket ; API Logic Explanation ; Algorithm Explanation)
- remove returning custom error message 
- test PowerFinder (sort_by_merit_order ; insort ; update_powerplants_production)
- add Websocket handling
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
Finally, run Api.py file with python, the RESTFul API will be exposed at http://127.0.0.1:8888/power

