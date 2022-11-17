import web_parsing as web
import yaml 

with open('params.yml') as f:
    params = yaml.safe_load(f)

particle = params['extraction_parameters']['particle']
element = params['extraction_parameters']['element']
initial_isotope = str(params['extraction_parameters']['initial_isotope'])
production_element = params['extraction_parameters']['production_element']
production_isotope = str(params['extraction_parameters']['production_isotope'])
reaction = params['extraction_parameters']['reaction']

postgres_table_name = 'TENDL' + '_' + initial_isotope + element + reaction + production_isotope + production_element 
user = params['postgres']['user']
password = params['postgres']['password']
dbname = params['postgres']['dbname']

generated_text, all_cs = web.data_parsing(particle, element, initial_isotope, production_isotope)
conn, cursor, engine = web.postgres_connection(dbname, user, password)
clean_data = web.data_cleaning(generated_text)
web.load_to_postgres(clean_data, all_cs, postgres_table_name, engine)
web.data_visualization(conn, cursor, production_element, production_isotope, element, initial_isotope, reaction)