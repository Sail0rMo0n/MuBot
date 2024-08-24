#!/bin/bash

python_alias="python3"

# Install python3-venv
sudo apt install -y python3-venv

# Install screen
sudo apt install -y screen

# Install ffmpeg
sudo apt install -y ffmpeg && sudo apt install --only-upgrade -y ffmpeg

# Define virtual environment
venv_name="env"

# Check if the virtual environment already exists
if [ -d "$venv_name" ]; then
  echo "Virtual environment $venv_name already exists."
else
  # Create the virtual environment
  $python_alias -m venv $venv_name
  echo "Virtual environment $venv_name created."
fi

# Activate the virtual environment
source $venv_name/bin/activate

# Install dependencies
pip install -r requirements.txt

# Update yt-dlp
pip install --upgrade yt-dlp

# Run MuBot.py with screen multiplexer
screen -dmS MuBot bash -c "$python_alias MuBot.py"

echo "MuBot.py is now running in a detached screen session. Run screen -r to attach."
