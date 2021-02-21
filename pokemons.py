import requests
import json
from pydrive.drive import GoogleDrive 
from pydrive.auth import GoogleAuth
import pandas as pd
import datetime

#A que hora se corrió el script
timeRan = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

#Autenticación de Google Drive
gauth = GoogleAuth()
gauth.LocalWebserverAuth()        
drive = GoogleDrive(gauth) 

#Abir el JSON que generó el script de shell
f = open("pokemons.json", "r")
#parsear el json para poder trabajar con él
pokemons = json.loads(f.read())

#Cargamos el archivo de google drive
newFile = drive.CreateFile({"id": "1z-VHSgk6PEdk-MKDxnXgT83uSJLACkyF"})
newFile.GetContentFile('pokemons.xlsx')

#Leemos el archivo a un dataframe
df = pd.read_excel('./pokemons.xlsx')

#Guardamos todos los IDs en una variable
IDs = df['id'].to_numpy()
#Estos son los datos que no vienen indicados directo del json, hay que interpretarlos
specialData = ['hp','attack','defense','special-attack','special-deffense','speed','types','Script']

#Comenzamos a recorrer todos los pokemons del JSON
for pokemon in pokemons['results']:
    #Hacemos una request a pokeapi para cada pokemon
    r = requests.get(pokemon['url'])
    #parseamos los datos que nos devuelve la API
    pokemonData = json.loads(r.text)
    
    if pokemonData['id'] in IDs:
        df.iloc[IDs == pokemonData['id'], df.columns.get_loc('Script_Ran')] = timeRan
        continue
    #Creamos un arreglo para el nuevo pokemon
    newPokemon = []
    #Comenzamos a recorrer las columnas del excel
    for column in df.columns:
        #Si eciste alguna de las columnas que tenemos que interpretar diferente
        if any(special in column for special in specialData):
            #Si es el tipo principal, agragarlo
            if 'types 1' in column:
                newPokemon.append(pokemonData['types'][0]['type']['name'])
            #Si es el tipo secundario, checar si tiene, si no poner solo un 'no'
            elif 'types 2' in column:
                newPokemon.append(pokemonData['types'][1]['type']['name'] if len(pokemonData['types']) > 1 else 'No')
            #La columna de script se llena con el tiempo en que fue corrido el script
            elif 'Script' in column:
                newPokemon.append(timeRan)
            #Maneja los stats
            else:
                #Checamos que stat estamos manejando en ese momento
                baseStat = pokemonData['stats'][specialData.index(column)]['base_stat']
                newPokemon.append(baseStat)
            continue
        #Agregamos el valor de dicha columna a nuestro pokemon
        newPokemon.append(pokemonData[column])
    #Agregamos una fila completa al dataframe
    df = df.append(pd.DataFrame([newPokemon], columns=df.columns),ignore_index=True)

#ordenamos los pokemons por ID
df.sort_values('id', inplace=True)
#Guardamos el excel
df.to_excel('./pokemons.xlsx', index=False)

#Indicamos que archivo vamos a subir
newFile.SetContentFile('pokemons.xlsx')

#Subimos el archivo a drive
newFile.Upload()