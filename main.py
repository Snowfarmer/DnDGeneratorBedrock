# Python Built-Ins:
import base64
import io
import json
import os

# External Dependencies:
import boto3
from PIL import Image



brt = boto3.client(service_name='bedrock-runtime')
###
diffculty =input("What is the difficulty of the encounter? Enter Easy, moderate or hard  ->   ")
partyNumbers=input("How many party members are there?  ->   ")
partyList=input("List the party members in a Class  level format. Use , to seperate each member.  ->   ")
partyAligment=input("What is the overall Alingment of the party?  ->   ")
location=input("Where is this encounter taking place?  ->   ")
###
#diffculty ="moderate"
#partyNumbers="4"
#partyList="Warrior - level 3, Druid - level 3, Bard - level 4, Wizard - level 3"
#partyAligment="lawful evil"
##location="mountain"
#enemyCount = "5"

print("GENERATING ENCOUNTER NOW")

prompt_data = """
Command: Generate a Dungeons and Dragons battle encounter that is {0} but fair. 
The party consists of {1} members and are of {2} alignment. 
The player characters consist of {3} and are located {4}.
Please generate the enemies that they will encounter, listing the type, level and equipment. Format it into a list.
""".format(diffculty, partyNumbers, partyList, partyAligment, location)

body = json.dumps({
    "inputText": prompt_data, 
    "textGenerationConfig":{
        "maxTokenCount":500,
        "stopSequences":[],
        "temperature":0.5,
        "topP":0.3
        }
    }) 

modelId = 'amazon.titan-tg1-large' # change this to use a different version from the model provider
accept = 'application/json'
contentType = 'application/json'
outputText = "\n"

response = brt.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
response_body = json.loads(response.get('body').read())

outputText = response_body.get('results')[0].get('outputText')
print(outputText)

splitOutput = outputText.splitlines()

#Image process
print("GENERATING ENCOUNTER IMAGE")
imagePrompt ="""
A fantasy painting depiction of {0} in a {1}.
""".format(outputText, location)

negative_prompts = [
    "poorly rendered",
    "poor background details",
]

style_preset = "photographic" 
width = 768

imageRequest = json.dumps({
    "text_prompts": (
        [{"text": imagePrompt, "weight": 1.0}]
        + [{"text": negprompt, "weight": -1.0} for negprompt in negative_prompts]
    ),
    "cfg_scale": 25,
    "seed": 65422,
    "steps": 80,
    "width": width,
})
imagemodelId = "stability.stable-diffusion-xl"
#
imageResponse = brt.invoke_model(body=imageRequest, modelId=imagemodelId)
response_body = json.loads(imageResponse.get("body").read())
base_64_img_str = response_body["artifacts"][0].get("base64")
#print(f"{base_64_img_str[0:80]}...")

os.makedirs("data", exist_ok=True)
image_1 = Image.open(io.BytesIO(base64.decodebytes(bytes(base_64_img_str, "utf-8"))))
image_1.save("image_1.png")