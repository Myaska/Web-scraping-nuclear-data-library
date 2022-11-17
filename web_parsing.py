import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import matplotlib.pyplot as plt

def data_parsing(particle, element, initial_isotope, production_isotope):
    
    URL = "https://tendl.web.psi.ch/tendl_2021/tendl2021.html"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")

    results = soup.find(id="highlights")
    links = results.find_all("a", href=True)

    links_url = [link["href"] for link in links]
    
    for link in links_url:
        if particle in link:
            elements_url = link
    
    page = requests.get(elements_url)
    soup = BeautifulSoup(page.content, "html.parser")
    
    results = soup.find(id = 'frame')
    
    links_elements = results.find_all("a", href=True)
    links_url_elements = [link["href"] for link in links_elements]
    
    for link in links_url_elements:
        if element in link:
            element_reaction = link
            
    page = requests.get(element_reaction)
    soup = BeautifulSoup(page.content, "html.parser")
    
    results = soup.find(id = 'frame')
    
    links_iso = results.find_all("a", href=True)
    links_url_iso = [link["href"] for link in links_iso]
    
    for link in links_url_iso:
        if initial_isotope in link:
            isotope_reaction = link
    
    cross_section = isotope_reaction[:-5] + 'residual.html'
        
    page = requests.get(cross_section)
    soup = BeautifulSoup(page.content, "html.parser")
    
    results = soup.find(id = 'frame')
    data_link = results.find_all("a", href=True)
    data_url = [link["href"] for link in data_link]
    
    all_cs= [link for link in data_url if re.findall(f"rp....{production_isotope}", link)]
    
    generated_text = []
    
    for page in all_cs:
        open_link = requests.get(page)
        soup = BeautifulSoup(open_link.content, "html.parser")
        generated_text.append(soup.text)
        
    return generated_text, all_cs

def postgres_connection(dbname, user, password):
    conn = psycopg2.connect("dbname={0} user={1} password={2}".format(dbname, user, password))
    cursor = conn.cursor()
    engine = create_engine('postgresql+psycopg2://{0}:{1}@localhost:5432/{2}'.format(user, password, dbname))
    
    return conn, cursor, engine

def data_cleaning(generated_text):
        
    for frame in generated_text: 
        clean_data = pd.DataFrame([x for x in frame.split('\n')],  columns=['Data'])
        clean_data = clean_data.drop([0, 1, 2, 3, 4, 5, 6])
        clean_data = pd.DataFrame(x.split(' ') for x in clean_data['Data'])
        clean_data =  clean_data.rename(columns={1: 'e_mev', 2: 'xs_mb', 3:'e_error', 4:'xs_error'}) 
        clean_data = clean_data.drop([0], axis = 1)
        clean_data = clean_data.dropna()
    
    return clean_data
        
def load_to_postgres(clean_data, all_cs, postgres_table_name, engine):
    
    for num in range(len(all_cs)):
        clean_data.to_sql(postgres_table_name + str(num), if_exists='append', con = engine, index=False)

    return print('Data was successfully loaded')


def data_visualization(conn, cursor, production_element, production_isotope, element, initial_isotope, reaction):     
    
    cursor.execute("""SELECT table_name FROM information_schema.tables
                   WHERE table_schema = 'public'""")
    extracted_data = []
    tables = []
    for table in cursor.fetchall():
        tables.append(table[0])
    for table in tables:    
        if production_element and production_isotope in table:  
            cursor.execute('''SELECT * from "%s"'''%(table))
        
            text = cursor.fetchall()
            extracted_data.append(text)
        
    for plot in extracted_data: 
        df_plots = pd.DataFrame([x for x in plot])
        df_plots =  df_plots.rename(columns={0: 'e_mev', 1: 'xs_mb', 2:'e_error', 3:'xs_error'})      
        df_plots['e_mev'] = df_plots['e_mev'].astype(float)
        df_plots['xs_mb'] = df_plots['xs_mb'].astype(float)
            
        df_plots.plot(x='e_mev',
                      y='xs_mb',
                      xlim = 25,
                      title='Cross section of {0}{1}{2}{3}{4} reaction'.format(initial_isotope, element, reaction, production_isotope, production_element),
                      xlabel = 'E (MeV)',
                      ylabel = 'Cross Section (mb)',
                      legend = False,
                      kind='scatter')	

        plt.savefig('TENDL_{0}{1}{2}{3}{4}.png'.format(initial_isotope, element, reaction, production_isotope, production_element), dpi=1200)
        
    print("Plot was succesfully saved in a working directory")
        
    conn.commit()
    conn.close()        
  
