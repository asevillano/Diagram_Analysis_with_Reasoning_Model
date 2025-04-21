import json
import os
import re
from dotenv import load_dotenv
from openai import AzureOpenAI
import base64
from mimetypes import guess_type
from PIL import Image
import streamlit as st
import networkx as nx
from pyvis.network import Network
import matplotlib.pyplot as plt
import plotly.graph_objects as go

import pandas as pd

# Function to encode a local image into data URL 
def local_image_to_data_url(image_path):
    # Guess the MIME type of the image based on the file extension
    mime_type, _ = guess_type(image_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'  # Default MIME type if none is found

    # Read and encode the image file
    with open(image_path, "rb") as image_file:
        base64_encoded_data = base64.b64encode(image_file.read()).decode('utf-8')

    # Construct the data URL
    return f"data:{mime_type};base64,{base64_encoded_data}"

# Function to analyze an image
def analyze_image(client, deployment_name, image_path, system_prompt, user_prompt, temperature=0.0):
    # Prepare the image to analyze
    data_url = local_image_to_data_url(image_path)
    print(f'Analyzing image {image_path}...\n')

    # Initiate the message with the system prompt
    messages=[
            { "role": "system", "content": system_prompt },
            { "role": "user", "content": [
                { 
                    "type": "text",
                    "text": user_prompt
                },
                { 
                    "type": "image_url",
                    "image_url": {
                        "url": data_url
                    }
                }
                ]
            }
    ]
    response = client.chat.completions.create(
        model=deployment_name,
        messages=messages,
        #max_tokens=2000,
        #temperature=temperature,
    )
    answer = response.model_dump()['choices'][0]['message']['content']
    print(f'RESPONSE: {answer}')
    return answer

# Extract data between two delimiters
def extract_text(texto, start_delimiter, end_delimiter=''):
    # This regular expression searches for any text between the delimiters.
    patron = re.escape(start_delimiter) + '(.*?)' + re.escape(end_delimiter)
    resultado = re.search(patron, texto, re.DOTALL)
    if resultado:
        return resultado.group(1)
    else:
        return None
    
# CONTANTS

# STEP 1: Extract connection types from connnection legend
SYSTEM_PROMPT_CONNECTION_TYPES = """You are an expert engineer in hydraulic schematic design.
The provided image is the hydraulic schematic design page that includes the legend with the connection types.
Your task is to analyze the legend and describe the connection types based on the colors and shapes of the lines in the hydraulic schematic design page.
Provide the connection type names according to the colors and shapes of the lines.
Your resopnse should be in this JSON format:
"connection_types": [
    {
        "connection_style": "color and shape of the connection line",
        "connection_type": "connection name as listed in the legend inside the hydraulic schematic design page"
    }
]
"""
USER_PROMPT_CONNECTION_TYPES = "Analyze this image with the legend information about the connection types and provide the connection name, shapes and colors:"

# STEP 2: Extract connections from schematic design
SYSTEM_PROMPT_CONNECTIONS = """You are an expert engineer in hydraulic schematic design.
The provided image was created from several pages of a document.
The first part, in vertical orientation, contains the legend page(s) with the component symbols and their names.
The last part of the image, in horizontal orientation, is the hydraulic schematic design page.
Your task is to analyze the hydraulic schematic design and describe the type of connections between the components, taking into account the information in the legend with the following details:
- The components are represented by symbols described in the legend or by standard symbols for hydraulic schematic designs.
- The connection type names are the specified in this json: {connection_types}. The colors and shapes of the lines indicate the type of connection.
- The number associated with each component is identified by its symbol as described in the legend pages.

Take your time to read the legend of the hydraulic schematic design and analyze the connections between the components in the hydraulic schematic design page.
Provide the connections type names according to the colors and shapes of the lines and the component numbers based on the information in the connection types provided.
Provide a detailed description of the connections between the components in the hydraulic schematic design page based on the information in the legend.

Your response should be in this JSON format:
"connections": [
   {{
      "component_number": component number,
      "component_name": "complete name from the legend",
      "connected_to": [ 
			{{"component_number": component number,
              "component_name": "complete name from the legend",
			  "connection_style": "color and shape of the line",
              "connection_type": "named as listed in the connection types provided",
			}}
		]
   }}
]
"""
USER_PROMPT_CONNECTIONS = "Analyze this image with the legend information and the hydraulic schematic design:"

# List of Design Diagrams for the listbox
DESIGN_LIST = ['Hydraulic_design', '462-Piping', 'abb', 'ML102530301']

def main():
    # Get Azure OpenAI Service settings
    load_dotenv(override=True)
    api_version = os.getenv("AOAI_API_VERSION")
    # Load o1 configuration
    aoai_o1_endpoint = os.getenv("AOAI_ENDPOINT")
    aoai_o1_apikey = os.getenv("AOAI_API_KEY")
    aoai_o1_deployment_name = os.getenv("AOAI_DEPLOYMENT_NAME")
    print(f'aoai_o1_endpoint: {aoai_o1_endpoint}, aoai_o1_deployment_name: {aoai_o1_deployment_name}')
    # Create the AOAI client
    aoai_o1_client = AzureOpenAI(
        azure_endpoint = aoai_o1_endpoint, 
        api_key= aoai_o1_apikey,
        api_version=api_version
    )

    # Set up initial Streamlit parameters from .env file
    st.set_page_config(
        page_title="Hydraulic Design Analysis",
        layout="centered",
        initial_sidebar_state="auto",
    )
    # Set the MS logo
    st.image("microsoft.png", width=100)
    # Set title
    st.title("Connections Design Analysis")

    # Innitiate the session_state to store the information between reloads
    if "connections" not in st.session_state:
        st.session_state.connections = None

    with st.sidebar:
        design = st.selectbox("Select Design", DESIGN_LIST)
    
    if design:
        st.write(f"Selected Design: {design}")
        design_path = os.path.join(design, design + "_schema.png")
        st.image(design_path)
        # Button to analyze the hydraulic design
        if st.button("Analyze hydraulic design", use_container_width=True, type='primary'):
            # Analyze the connection types
            with st.spinner(f"STEP 1: Analyzing connection types with Azure OpenAI, o1 model..."):
                response = analyze_image(aoai_o1_client, aoai_o1_deployment_name, design_path, 
                                                 SYSTEM_PROMPT_CONNECTION_TYPES, USER_PROMPT_CONNECTION_TYPES)
                st.write("Identified Connection types:")
                connection_types = json.loads(response)
                # SHOW IN JSON FORMAT
                #st.code(json.dumps(connection_types, indent=4), language='json')
                # SHOW THE CONNECTION TYPES AS A TABLE
                st.table(pd.DataFrame(connection_types['connection_types']))
            
            # Analyze the connections
            with st.spinner(f"Analyzing connections with Azure OpenAI, o1 model..."):
                stitchted_path = design_path.replace("_schema.png", "_stitchted.png")
                system_prompt = SYSTEM_PROMPT_CONNECTIONS.format(connection_types=connection_types)
                response = analyze_image(aoai_o1_client, aoai_o1_deployment_name, stitchted_path,
                                         system_prompt = system_prompt, 
                                         user_prompt = USER_PROMPT_CONNECTIONS)

                st.write("Identified Connection:")
                connections = json.loads(response)
                # SHOW IN JSON FORMAT
                #st.code(json.dumps(connections, indent=4), language='json')
                
                # SHOW THE CONNECTIONS AS A LIST
                for connection in connections['connections']:
                    text=""
                    text += f"Component {connection['component_number']} - {connection['component_name']}\n"
                    for connected_to in connection['connected_to']:
                        text += f" - Connected to: {connected_to['component_number']} - {connected_to['component_name']}, Connection Type: {connected_to['connection_type']}, Style: {connected_to['connection_style']}\n"
                    st.write(text)

                # SHOW THE CONNECTIONS AS A RELATIONSHIP GRAPH
                # Create a directed graph
                G = nx.DiGraph()
                # Add nodes and edges from the JSON data
                for component in connections['connections']:
                    component_name = component['component_name']
                    component_number = component['component_number']
                    
                    for connection in component['connected_to']:
                        connected_component = connection['component_name']
                        connection_type = connection['connection_type']
                        
                        G.add_edge(component_name, f"Component {connected_component}", label=connection_type)

                # Create a PyVis network
                net = Network(notebook=True)
                net.from_nx(G)

                # Generate the graph and save it as an HTML file
                net.show("graph.html")

                # Display the graph in Streamlit
                st.title("Component Connection Graph")
                st.components.v1.html(open("graph.html").read(), height=800)


                # Guardamos el resultado del análisis en session_state para su uso posterior.  
                st.session_state.connections = connections 

    # Sección para consultar (chatbot) sobre un componente concreto  
    if st.session_state.connections is not None:  
        #st.markdown("### Ask about a specific component")  
        #st.markdown("Enter the name (or part) of a component to see its relationships:")  
         
        component_query = st.chat_input("Enter the name (or part) of a component to see its relationships:")  
         
        # Al pulsar el botón, construimos y mostramos el subgrafo basado en el componente consultado.  
        if component_query: #st.button("Show Relationship Graph"):  
            if component_query.strip() == "":  
                st.warning("Please, Enter the name of a component.")  
            else:  
                new_G = nx.DiGraph()  
                found = False
                text = ""
                for component in st.session_state.connections['connections']:  
                    source = component['component_name']  
                    # Si el componente principal coincide con la consulta, agregamos todas sus conexiones.  
                    if component_query.lower() in source.lower():  
                        new_G.add_node(source)
                        text += f"Component {component['component_number']} - {component['component_name']}\n"
                        for conn in component['connected_to']:  
                            target = conn['component_name']  
                            new_G.add_edge(source, target, label=conn['connection_type'])  

                            text += f" - Connected to: {conn['component_number']} - {conn['component_name']}, Connection Type: {conn['connection_type']}, Style: {conn['connection_style']}\n"
                        found = True  
                    else:  
                        # Si algún componente conectado coincide, agregamos la relación  
                        for conn in component['connected_to']:  
                            target = conn['component_name']  
                            if component_query.lower() in target.lower():  
                                new_G.add_edge(source, target, label=conn['connection_type'])  
                                text += f" - Connected to: {conn['component_number']} - {conn['component_name']}, Connection Type: {conn['connection_type']}, Style: {conn['connection_style']}\n"
                                found = True  
                if not found:  
                    st.error("No relationships were found for the specified component.")  
                else:
                    st.subheader(f"Relationship graph for '{component_query}'")  
                    st.write(text)
                    sub_net = Network(notebook=True)  
                    sub_net.from_nx(new_G)  
                    sub_net.show("subgraph.html")  
                    st.components.v1.html(open("subgraph.html").read(), height=800) 

if __name__ == "__main__":
    main()