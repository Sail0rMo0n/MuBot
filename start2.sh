#!/bin/bash

python_alias="python3.12"

# Install python3
sudo apt install -y python3.12

# Install screen
sudo apt install -y screen

# Install pipenv
sudo apt install -y pipenv

# Install ffmpeg
sudo apt install -y ffmpeg && sudo apt install --only-upgrade -y ffmpeg

# Create a new Pipenv environment
pipenv --python $python_alias

# Install dependencies
pipenv install -r requirements.txt

# Run MuBot.py with screen multiplexer
screen -dmS MuBot bash -c "pipenv run python MuBot.py"

echo "MuBot.py is now running in a detached screen session. Run screen -r to attach."
