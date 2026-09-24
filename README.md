# DS4002-Project1

### Section 1: Software and Platform

 
- We used Python for this project, specifically Python 3.14.7

Add-on packages that need to be installed with the software:
- scikit learn
- pandas
- matplotlib

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
        - circuit_criminal_2025_anon_00.csv
        - circuit_criminal_2025_anon_01.csv
        - circuit_criminal_2025_anon_02.csv
    - labeled_code_sections.csv
    - unique_code_section.csv
    - README.md
- OUTPUT
- SCRIPTS
    - label_data.py
    - model.py
    - preprocess_data.py
- LICENSE
- README.md

### Section 3: Instructions for reproducing your results.  
- Clone the repo:
    - clone this repo to your local and open it up in your IDE
- Run the preprocessing script:
    - in your IDE (ex: vscode), open up the project and your terminal
    - make sure you have python3 downloaded on your computer
    - if you don't have them already, download our software dependencies:
        - scikit learn
        - pandas
        - matplotlib
    - run: python3 preprocess_data.py
        - this cleans the data and labels crime categores for training
- Run the model:
    - run: python3 model.py
- Interpret your results from the terminal output.