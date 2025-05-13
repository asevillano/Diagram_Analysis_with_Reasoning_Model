# PROMPTS

# STEP 1: Extract connection types from connnection legend
SYSTEM_PROMPT_CONNECTION_TYPES = """You are an expert engineer in hydraulic schematic design.
The provided image is the hydraulic schematic design page that includes the legend with the connection types.
Your task is to analyze the legend and describe the connection types based on the colors and shapes of the lines in the hydraulic schematic design page.
You can detect the legend of connection types by a list of lines (solid line, long-dashed line, dash-dot line, dotted line) along with their corresponding names.
Provide the connection type names according to the colors and shapes of the lines.
You **MUST** be very extrict identifying **every connection types** in the legend.
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
First list the components and their numbers in the hydraulic schematic design page. Then, list the connection types and their names between every component.
Take your time to read the legend of the hydraulic schematic design and analyze the connections between the components in the hydraulic schematic design page.
Provide all the connections type names according to the colors and shapes of the lines and the component numbers based on the information in the connection types provided.
You **MUST** be very extrict identifying **every component** and **every connections** between them.
Provide a detailed description of the connections between the components in the hydraulic schematic design page based on the information in the legend.
Your response should be in this JSON format:
"list_of_components": [
   {{
      "component_name": "complete name from the legend",
      "component_number": component number,
      "component_description": "description of the component"
   }}
],
"connections": [
   {{
      "component_name": "complete name from the legend",
      "component_number": component number,
      "connected_to": [ 
			{{"component_name": component name from the legend,
              "component_number": component number,
			  "connection_style": "color and shape of the line",
              "connection_type": "named as listed in the connection types provided",
			}}
		]
   }}
]
"""
USER_PROMPT_CONNECTIONS = "Analyze this image with the legend information and the hydraulic schematic design:"