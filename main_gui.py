import tkinter as tk
from tkinter import ttk
import httpx

# URL base de la API de FastAPI
API_BASE_URL = "http://127.0.0.1:8000"

def get_episodes():
    """ Obtiene la lista de episodios de la API y actualiza la lista en la interfaz gráfica. """
    try:
        url = f"{API_BASE_URL}/episodes"
        response = httpx.get(url)
        response.raise_for_status()  # Verifica si hay errores en la respuesta
        episodes = response.json()  # Convierte la respuesta en formato JSON
        episode_listbox.delete(0, tk.END)  # Limpiar la lista antes de agregar nuevos elementos
        for episode in episodes:
            episode_listbox.insert(tk.END, episode)  # Agrega cada episodio a la lista
        get_info_button.config(state=tk.NORMAL)  # Habilita el botón Get Info después de cargar episodios
    except httpx.HTTPError as e:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Error: {str(e)}")  # Muestra el error HTTP
    except Exception as e:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Unexpected error: {str(e)}")  # Muestra errores inesperados

def get_info():
    """ Obtiene la información del episodio seleccionado y la muestra en la interfaz gráfica. """
    selected_index = episode_listbox.curselection()  # Obtiene el índice del episodio seleccionado
    if not selected_index:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "Please select an episode from the list.")  # Solicita la selección de un episodio
        return

    try:
        episode_name = episode_listbox.get(selected_index)  # Obtiene el nombre del episodio seleccionado
        url = f"{API_BASE_URL}/getinfo/{episode_name}"
        response = httpx.get(url, timeout=60)  # Solicita la información del episodio con un tiempo de espera de 60 segundos
        response.raise_for_status()
        info_list = response.json()  # Convierte la respuesta en formato JSON
        
        formatted_info = f"Capítulo: {episode_name}\n"
        for character_info in info_list:
            formatted_info += (
                f"Name: {character_info['name']}\n"
                f"Status: {character_info['status']}\n"
                f"Specie: {character_info['specie']}\n"
                f"Gender: {character_info['gender']}\n"
                f"Current Location: {character_info['current location']}\n"
                f"Current Location Type: {character_info['current location type']}\n"
                f"================\n"
            )
        
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, formatted_info)  # Muestra la información formateada del episodio
    except httpx.HTTPError as e:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Error: {str(e)}")  # Muestra el error HTTP
    except httpx.ReadTimeout:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "Request timed out. Please try again.")  # Muestra un mensaje si la solicitud excede el tiempo de espera
    except Exception as e:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Unexpected error: {str(e)}")  # Muestra errores inesperados

def on_select(event):
    """ Habilita el botón Get Info cuando se selecciona un episodio de la lista. """
    get_info_button.config(state=tk.NORMAL)

# Configuración de la ventana principal
root = tk.Tk()
root.title("FastAPI GUI")

# Configuración de la interfaz
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

episode_listbox = tk.Listbox(frame, selectmode=tk.SINGLE, height=10, width=50)
episode_listbox.bind('<<ListboxSelect>>', on_select)  # Enlaza el evento de selección con la función on_select
episode_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Agregar un scrollbar para la lista de episodios
scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=episode_listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
episode_listbox.config(yscrollcommand=scrollbar.set)

# Botones para ejecutar las funciones de FastAPI
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

get_episodes_button = tk.Button(button_frame, text="Get Episodes", command=get_episodes)
get_episodes_button.pack(side=tk.LEFT, padx=5)

get_info_button = tk.Button(button_frame, text="Get Info", command=get_info, state=tk.DISABLED)
get_info_button.pack(side=tk.LEFT, padx=5)

# Etiqueta para mostrar los resultados en un área desplazable
result_frame = tk.Frame(root)
result_frame.pack(pady=10)

result_text = tk.Text(result_frame, wrap=tk.WORD, height=15, width=70)
result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Agregar un scrollbar al área de resultados
result_scrollbar = tk.Scrollbar(result_frame, orient=tk.VERTICAL, command=result_text.yview)
result_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
result_text.config(yscrollcommand=result_scrollbar.set)

# Inicia el bucle principal de la interfaz gráfica
root.mainloop()
