# Cross Section data from TENDL nuclear data library

<img width="675" alt="Screen Shot 2022-11-17 at 9 51 50 AM" src="https://user-images.githubusercontent.com/72933965/202507681-23e595f0-2d9d-4323-a22e-66b85b834ac3.png">

This is a web scraping application for the TENDL nuclear data library which provides the output of the TALYS nuclear model code system for direct use in both basic physics and applications (https://tendl.web.psi.ch/tendl_2021/tendl2021.html).

### Befor run this up you should:
  - create a DataBase in PostgresSQL where you want to load data
  
### Change parameters in params.yml:

#### extraction_parameters
  - particle : you can choose (neutron, proton, deuteron, triton, alpha, gamma)
  - element : provide symbol of element, you want to use as a target material (e.g. Cr, Mn, Sc, Ti...)
  - initial_isotope : enter the number of isotope; for natural targets insert the isotope with the highest abundancy 
  - production_element : provide symbol of element, you want to use as a target material (e.g. Cr, Mn, Sc, Ti...)
  - production_isotope : production isotope 
  - reaction : enter the reaction in format: (a,x), (p, n), (d, 2n)...
  
  #### PostgresSQL
  - dbname : choose the database name in PostgresSLQ
  - user : set up your username
  - password : set up your password
  
  ### To run the app execute the following commands:
  - tested in Python 3.9.12
  - pip install -r requirements.txt
  - sh run_app.sh
