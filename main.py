from fastapi import FastAPI, HTTPException
import httpx

# se carga FastAPI
app = FastAPI()


"""End point episodes

aca se extrae toda la informacion de los capitulos.

Raises:
    HTTPException: en caso que no se pueda conectar da un error. No mando mensaje con codigo 400 porque me quede sin tiempo, sorry.

Returns:
    episode_names: Entrega una lista de los nombres de los episodios
"""
@app.get("/episodes")
async def get_episodes():
    url = "https://rickandmortyapi.com/api/episode" #se tiene la url quemada para siempre hacer las consultas.
    async with httpx.AsyncClient() as client: #proceso asincrono para ir consultando a cada personaje.
        try:
            response = await client.get(url) #se obtiene la informacion del endpoint de episodios.
            data = response.json()  # Obtiene el JSON de la respuesta
            episode_names = [episode["name"] for episode in data["results"]] # Se crea una lista con los nombres de cada episodio.
            return episode_names # Se entrega la lista de nombres.
        except:
            return ["No se pudo conectar con el endpoint de episodios, se pudrio todo."]
        
#Diccionario para guardar las ubicaciones de cada personaje, en caso que una ubicacion la compartan varios. Se consulta a este diccionario. Este es temporal y solo aplica para un solo episodio.
location_dict = {}
#Diccionario para ir guardando la informacion de cada personaje. Una vez se registra a un personaje, ya no se tiene que consultar por el al endpoit
character_db_list = {}


"""Funcion para entregar la informacion de los personajes. Recibe el nombre del espisodio

Raises:
    HTTPException: _description_

Returns:
    _type_: _description_
"""
@app.get("/getinfo/{name}")
async def get_episodes(name: str):
    url = "https://rickandmortyapi.com/api/episode" #se tiene la url quemada para siempre hacer las consultas.
    character_info_list = [] # se crea la lista que se va a entregar con la informacion de cada personaje.
    #location_dict.clear # se limpia el diccionario de ubicaciones ya que este funciona solo para cada episodio. Se elimina para que sea global.
    async with httpx.AsyncClient() as client:
        response = await client.get(url) #se obtiene la informacion del endpoint de episodios. Es verdad que se puede mejorar guardando la respuesta del enpoint anterior, pero ya quedo asi y no estan costosa esa consulta.
        data = response.json()  # Obtiene el JSON de la respuesta
        response = [episode for episode in data["results"] if episode["name"].lower() == name.lower()] # se extrae el episodio que tenga el mismo nombre que se ingreso en el endpoint
        response = response[0] # por el tipo de dato, no hay dos capitulos con el mismo nombre. por ende, el primer objeto de la lista es el episodio. Se guarda toda la info del episodio
        if not response: # error en dado caso que no encuentre el capitulo
            raise HTTPException(status_code=404, detail="Episode not found")
        for character_url in response["characters"]: #en este ciclo recorremos cada uno de los links de los personajes del capitulo selecionado.
            if (character_url not in character_db_list): # se verifica si ya se ha registrado a ese personaje o no. En caso de ser la primera vez que se consulta:
                character_info = await get_info(character_url, "character") # se llama a al funccion get_info que accede a la informacion del personaje. recibe el str de "character" para diferenciarlo de una ubicacion
                character_info_list.append(character_info) #se agrega a la lista que se va a entregar la informacion relevante del personaje
                character_db_list[character_url] = character_info #se agrega al historico el personaje para evitar tener que volver a consumir su endpoint y evitar una consulta redundante.
            else:
                character_info_list.append(character_db_list[character_url])# en caso de que ya se haya registrado, se saca la informacion del diccionario donde ya esta guardada su infromacion relevante
        return character_info_list # se entrega la info.
    
"""Funcion get info
Aca es donde accedemos a los personajes o ubicaciones para sacar la informacion relevante, y se entrega en el formato deseado.
Recibe la URL del personaje o ubicacion y el string que define si es personaje o ubicacion.
character_info = {
                    "name": character_data["name"],
                    "status": character_data["status"],
                    "specie": character_data["species"],
                    "gender": character_data["gender"],
                    "current location": location_info["location_name"],
                    "current location type": location_info["location_type"]
                }
                
location_info = {
                    "location_name": location_data["name"],
                    "location_type": location_data["type"]
                }
                
return: devuelve un diccionario con la informacion del personaje o ubicacion
"""
async def get_info(url: str, type: str):
    async with httpx.AsyncClient() as client:
        if (type == "character"): #Aca es donde esta la "sobre carga de metodos" ya que dependiendo si es personaje o ubicacion hace un proceso diferente.
            response = await client.get(url) # ingresa a la URL
            character_data = response.json() # saca el json
            if (character_data['location']['name'] not in location_dict): #Revisa si en el diccionario de ubicaciones ya se ha registrado esa ubicacion o no. En caso de ser la primera vez:
                location_info = await get_info(character_data["location"]["url"], "location") # Hace recursion llamandose a si mismo pero para sacar la ubicacion respectiva. Aca saca la url de la ubicacion.
                character_info = { #se crea el diccionario con la informacion del personaje y la informacion de la ubicacion extraida.
                    "name": character_data["name"],
                    "status": character_data["status"],
                    "specie": character_data["species"],
                    "gender": character_data["gender"],
                    "current location": location_info["location_name"],
                    "current location type": location_info["location_type"]
                }
                location_dict[location_info["location_name"]] = location_info["location_type"] #se registara la ubicacion para no volver a consultarla.
            else:
                character_info = { #en caso de que la informacion ya este registrada, solo la extrae del diccionario evitando otra solicitud al endpoint de ubicacion.
                    "name": character_data["name"],
                    "status": character_data["status"],
                    "specie": character_data["species"],
                    "gender": character_data["gender"],
                    "current location": character_data['location']['name'],
                    "current location type": location_dict[character_data['location']['name']]
                }
            return character_info #entrega el diccionario.
        elif (type == "location"): # en caso que se este extrayendo una ubicacion.
            if (url): #como hay personajes que no se sabe donde estan, hay ubicaciones sin links. En caso de que si se conosca la ubicacion:
                response = await client.get(url) #se entra al endpoin de la ubicacion
                location_data = response.json() #se extrae el json.
                location_info = { #extraemos en un diccionario el nombre y el tipo de la ubicacion.
                    "location_name": location_data["name"],
                    "location_type": location_data["type"]
                }
            else:
                location_info = { #en caso que no se sepa donde esta el personaje, se entrega un desconocido.
                    "location_name": "unknown",
                    "location_type": "unknown"
                }
            return location_info # se entrega un diccionario con la informacion de la ubicacion para que sea agregado al diccionario del personaje.
        

