# Modern Data Analytics
## ​​An investigation into the temporal evolution of research output and funding from Horizon 2020 and Horizon Europe​ 

### Project overview
This project analyses EU-funded research projects from the Horizon 2020 and Horizon Europe programmes. The goal is to extract insights about funding patterns, research categories, international collaboration and scientific output using a combination of interactive visualizations and statistical modeling. 

### Data used 
The datasets used in this repository were downloaded form the official Horizon project portals at the start of the project. Although newer versions may exist, only the original versions available at that time were used. Eight core datasets were used in total, split evenly between Horizon 2020 and Horizon Europe, including: 
- EuroSciVoc
- organization 
- project
- projectPublications 

> ⚠️ **Note:** Some of the datasets are larger than 100MB and are therefore excluded from the GitHub repository due to upload size limits.  
> You can download these files manually via the following link and place them in the `data/` folder of the project:  
> [Download large datasets](<https://kuleuven-my.sharepoint.com/:f:/g/personal/jana_swaans_student_kuleuven_be/EhCXXS87Ac5AjALggniR3XkBHPz_VPfiTw7KCy90ZrQmfw?e=1yhzbS>)


### Repository structure 
- app/
    - contains the app.py, which is the main entry point of the web application.
    - includes a www/ folder for all images used in the interface
    - the utils/ folder contains 
        - layout.py: defines the banner, layout shown on every panel 
        - methods.py: includes utility functions such as ISO2-to-ISO3 country conversion 
    - the panels/ folder includes eight separate scripts, each responsible for a distinct part of the analysis (e.g. funding map, clustering, research impact, etc.)
- notebooks/
    - contains two jupyter notebooks: 
        - one for exploratory analysis, showing general patterns and relationships in the data
        - one for explanatory modeling, which includes a regression analysis 
- scripts/ 
    - contains the scripts necessary to run the Topological Data Analysis (TDA)
- data 
    - stores both the original datasets (as downloaded) and processed datasets (generated during analysis)
- requirements.txt
    - lists all python packages required to run the app and supporting scripts 