"""
This file is used to automatically run through the programs in order to reproduce our results given the same data
Just clone the repo, then switch into the scripts directory and run this script to get the full reproduction of our results
***Note***: Model may vary slightly due to the differnce in training data selected at random
"""
import subprocess

#quick summary of the scripts in order 
scripts = [
    "preprocess_data.py", #takes the existing court data and cleans it by removing duplicates and normalizing the charge text
    "model.py", #takes the cleaned data and test several types of models and selects the best one, then saves info of the models stats 
    "evaluate_model.py" #takes the best model and performs statistical analysis of the results of the model (chi-squared, cramer's-v test)
]

result = subprocess.run(["pip", "install", "-r", "requirements.txt"])

if result.returncode != 0:
    print(f"Failue when installing requirements, make sure you are in a virtual python enviroment using <python3 -m venv venv>")
    exit(1)
else:
    print(f"Requirements installed\n")


for script in scripts:
    print(f"Starting {script}...")
    result = subprocess.run(["python", script])
    
    #Stop execution if a script fails
    if result.returncode != 0:
        print(f"{script} failed. Stopping the sequence.")
        break
    print(f"{script} finished successfully.\n")