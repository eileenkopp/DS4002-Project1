# DS4002-Project1

### Section 1: Software and Platform

 
- We used Python for this project, specifically Python 3.14.7

Add-on packages that need to be installed with the software (can check requirements.txt in SCRIPTS to see exact versions):
- scikit learn
- pandas
- numpy
- joblib

The platform we used: 
- Mac


### Section 2: Documentation Map. 

An outline illustrating the hierarchy of folders and subfolders contained in your Project Folder, and listing the files stored in each folder or subfolder. 

- DATA
    - court_case_data
        - circuit_criminal_2020_anon_00.csv
        - circuit_criminal_2021_anon_00.csv
        - circuit_criminal_2022_anon_00.csv
        - circuit_criminal_2023_anon_00.csv
        - circuit_criminal_2024_anon_00.csv
        - circuit_criminal_2025_002.csv
        - circuit_criminal_2025_anon_00.csv
        - circuit_criminal_2025_anon_01.csv
    - labeled_code_sections.csv
    - unique_code_section.csv
    - data_cleaned.csv
        - **this file was too big to upload to github. To access, use this link to view the file in google drive: https://drive.google.com/file/d/18tYYAcxT0N9HHhBcbOf5kmi2x2k4Et-D/view?usp=drive_link**
    - README.md
- OUTPUT
    - category_distribution_percentage.png
    - confusion_matrix_normalized.png
    - contingency_table_full.csv
    - consingency_table_visual.png
    - eval_stats_summary.txt
    - model_stats_summary.txt
- SCRIPTS
    - best_model.joblib
    - evaluate_model.py
    - model.py
    - preprocess_data.py
    - requirements.txt
    - run_scripts.py
- LICENSE
- README.md

### Section 3: Instructions for reproducing your results.  
- Clone the repo:
    - clone this repo to your local and open it up in your IDE
 
- 2 options for how to reproduce the results:
- 1. Change Directory into the SCRIPTS directory, then run the run_scripts.py file to automatically to do the steps in the second option
  2. Manually do the following steps below in-a-row starting from pre_processing script, then running the model, finishing with running the evaluation script
- Run the preprocessing script:
    - in your IDE (ex: vscode), open up the project and your terminal
    - make sure you have python3 downloaded on your computer
    - if you don't have them already, download our software dependencies (listed above)
    - run: python3 preprocess_data.py
        - this cleans the data and labels crime categores for training
        - When cleaning the data it removes duplicates and normalizes the charge text before it can be used by the model
- Run the model:
    - run: python3 model.py
        - this trains, validates, and tests the model, outputting the results to the terminal
- Run the significance / evaluation script:
    - run: python3 evaluate_model.py
    - this creates the confusion matrix, contingency table, and runs statistical analysis (cramer's-v and chi-squared) and saves results to output folder
- Interpret your results from the figures produced in the output folder.

### References
1. Virginia Court Data, “Court case information from Virginia’s Circuit and General District courts,” virginiacourtdata.org. [Online]. Available: https://virginiacourtdata.org/  - Where we got the dataset (2020 - 2025)
2. "Code of Virginia," Virginia Law, 2026. [Online]. Available: https://law.lis.virginia.gov/vacode/ . (Accessed: Sep. 23, 2026). – what we used to create category labels



