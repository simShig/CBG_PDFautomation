import exceptiongroup
import openai
from pathlib import Path
# from llama_index import download_loader
import os
import openai
from llama_index.core import SimpleDirectoryReader
from llama_index.readers.file import  PDFReader,ImageCaptionReader, ImageReader, ImageVisionLLMReader,PyMuPDFReader


from openai import OpenAI

client = OpenAI()

#
# # PDF Reader with `SimpleDirectoryReader`
# parser = PDFReader()
# file_extractor = {".pdf": parser}
# documents = SimpleDirectoryReader(
#     "./data", file_extractor=file_extractor
# ).load_data()

#
# ImageReader = download_loader("ImageReader")
# imageLoader = ImageReader(text_type="plain_text")
# FlatPdfReader = download_loader("FlatPdfReader")
# pdfLoader = FlatPdfReader(image_loader=imageLoader)

# paper_list = ['Shapira_Phantom_Sponges_Exploiting_Non-Maximum_Suppression_To_Attack_Deep_Object_Detectors_WACV_2023_paper.pdf','Sponge_Examples_Energy-Latency_Attacks_on_Neural_Networks.pdf',
#
#                '2211.08859.pdf','1910.11099.pdf']

import os
from openai import AzureOpenAI
from openai import OpenAI
client = OpenAI()

dir_path = fr'C:\Users\Simon\PycharmProjects\CBGproject\venv\ExtractFromArticles\PDFs'
arr_paper = os.listdir(dir_path)

#arr_paper = ['41_SpongeExamplesEnergyLatencyAttacksonNeuralNetworks.pdf','44_ENERGYLATENCYATTACKSVIASPONGEPOISONING.pdf']
# setx OPENAI_API_KEY "de53e63870474486910d4109044e9be3"
openai.api_type = "azure"
openai.api_base = "https://avishag.openai.azure.com/"  # os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_key =  'de53e63870474486910d4109044e9be3'  #os.getenv("OPENAI_API_KEY")
openai.api_version = "2023-12-01"
#
# completion = client.chat.completions.create(
#   model="gpt-3.5-turbo",
#   messages=[
#     {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
#     {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
#   ]
# )
#
# print(completion.choices[0].message)


client = AzureOpenAI(
    api_key="de53e63870474486910d4109044e9be3",  # os.getenv("AZURE_OPENAI_KEY"),
    api_version="2023-12-01-preview",
    azure_endpoint="https://avishag.openai.azure.com/"  # os.getenv("AZURE_OPENAI_ENDPOINT"),
)

deployment_name = 'gpt4-avishag'



def get_completion(prompt_sys, prompt_user, model=deployment_name ):#"gpt-3.5-turbo-16k"):#"gpt-3.5-turbo-16k-0613"):#:#"gpt-3.5-turbo"):
    messages = [{"role": "system", "content": prompt_sys},

                {"role": "user", "content": prompt_user}]
    #messages = [{"role": "system", "content":"who won the world series i 2020?"}]
    response = client.chat.completions.create(#
        model=model,
        messages=messages,
        temperature=0,
        #response_format={ "type": "json_object" }
        #stream=True
    )
    return response#.choices[0].message["content"]

# def get_completion_images(prompt_sys, prompt_user_base64_image, model="gpt-4-vision-preview" ):#"gpt-3.5-turbo-16k"):#"gpt-3.5-turbo-16k-0613"):#:#"gpt-3.5-turbo"):
#     messages = [{"role": "system", "content": [{"type":"text", "text": prompt_sys}]},
#                 #{"role": "user", "content": demi_user1.text},
#                 #{"role": "assistant", "content": assistant_string1},
#                 {"role": "user", "content": demi_user2_base64_images_contene},
#                 {"role": "assistant", "content": [{"type":"text", "text": assistant_string2}]},
#                 {"role": "user", "content": prompt_user_base64_image},
#                 #{"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{prompt_user_base64_image}"}}}
#                 ]

    #print(messages)
    #messages = [{"role": "system", "content":"who won the world series i 2020?"}]
    response = client.chat.completions.create(#
        model=model,
        messages=messages,
        temperature=0,
        max_tokens = 4096,
        #response_format={ "type": "json_object" }
        #stream=True
    )
    return response#.choices[0].message["content"]

#
def get_completion_validation(prompt_sys, prompt_user_paper, prompt_assis, prompt_user_valid, model=deployment_name ):#"gpt-3.5-turbo-16k"):#"gpt-3.5-turbo-16k-0613"):#:#"gpt-3.5-turbo"):
    messages = [{"role": "system", "content": prompt_sys},
                #{"role": "user", "content": demi_user1.text},
                #{"role": "assistant", "content": assistant_string1},
                # {"role": "user", "content": demi_user2.text},
                # {"role": "assistant", "content": assistant_string2},
                {"role": "user", "content": prompt_user_paper},
                 {"role": "user", "content": prompt_assis},
                {"role": "user", "content": prompt_user_valid}]
    #messages = [{"role": "system", "content":"who won the world series i 2020?"}]
    response = client.chat.completions.create(#
        model=model,
        messages=messages,
        temperature=0,
        #response_format={ "type": "json_object" }
        #stream=True
    )
    return response#.choices[0].message["content"]



#Step 4: Query the API
def get_template():
    with open('summary_template_system_updated_excel.txt') as f:#with open('summary_template_system_new_3_gpt4-turbo-only-part.txt') as f:#summary_template_system_new_3_gpt4-turbo.txt', 'r') as f:#open('summary_template_system_new_3_gpt4-turbo-only-part.txt', 'r') as f:#('summary_template_system_new_3_gpt4-turbo-5arracks_looks good for sponge exampple.txt', 'r') as f:###('summary_template_system_new_3_gpt4-turbo-only-few-fields.txt', 'r') as f:#
        return f.read().strip()



###go over all the papers until final analysis
import pandas as pd
import re
import json
import pdfplumber


def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text



prompt_sys = ""
paper_list_first_analysis = []
paper_list_sec_analysis = []
json_lists =[]
columns_order = ["record_id","paper_name","Attack Name", "Objective", "Threat Model", "Attacker Knowledge",  "is Backdoor" , "Attack Type", "Attack Phase",
                 "Domain", "Applicable in the physical domain", "Description", "Attack's success rate - digital domain", "Attack's success rate - physical domain", "Attacked models", "Datasets", "Reference"]
df_columns_order = pd.DataFrame([columns_order], columns=columns_order)

csv_name = 'output_new_updated.csv'
if not os.path.exists(csv_name):
    df_columns_order.to_csv(csv_name, mode='a', index=False, header=True)
    df_existing = pd.DataFrame(columns=columns_order)
else:
    df_existing = pd.read_csv(csv_name)

existing = list(df_existing['paper_name'].str.strip().str.lower().values)

for paper_name in arr_paper:#paper_list:
    print("paper name: "+paper_name)
    # Iterate through the new data and add rows that don't exist in the existing CSV
    normalized_paper_name = paper_name.strip().lower()
    if normalized_paper_name in existing:
        print("existing, passing next")
        continue
    existing.append(normalized_paper_name)
    # document = pdfLoader.load_data(file=Path(fr'C:\Users\Administrator\Documents\phd\oran\down_paper\CBG_PDFautomation\PDFs_new\{paper_name}'))#(file=Path(fr'C:\Users\Administrator\Documents\phd\oran\papers\{paper_name}'))
    # Extract text from the PDF
    pdf_path = dir_path + '\\'+ paper_name
    try:
        pdf_text = extract_text_from_pdf(pdf_path)
    except Exception:
        print("Couldnt Read Pdf,continue to next")
        continue
    #print(document.text)

    prompt_sys = get_template()#"<YOUR QUERY>"
    #print(prompt_sys)
    response = get_completion(prompt_sys, pdf_text)#get_completion_images(prompt_sys, pdf2gptmessage_content(fr'C:\Users\Administrator\Documents\phd\oran\papers\{paper_name}'))#
    #print(response)

    #json_output = text_to_json(response.choices[0].message["content"])
    paper_f_ana = response.choices[0].message.content
    print(paper_f_ana)

    paper_list_first_analysis.append(paper_f_ana)#(json_output)
    ##print(response.choices[0].message["content"])#json_output)
    print("------------------------------------sec_analysis:--------------------------------------------------------")

    ##sec analysis (fine tuning)
    prompt_user_valid = "You are a system that refines and clarifies information. Every time, the system gets a summarization on an attack in a JSON format, and adjusts the info that is is presented to be an input for another automatic analysis system. " \
    "The system tries to refine the information in the original JSON, make it shorter and more accurate. " \
                 "Here are some EXAMPLES:" \
                 "1. if you get a range of numbers - the system replaces it with the average of the range. " \
                 "2. if data is presented with many words, the system tries to replace it with the most important info (for example, with a number if possible). " \
                 "3. there are 'Description' and 'explanation' fields. These fields contain info regarding other fields (specially, about the 'Attack's success rate' fields and 'Attack Type'). " \
                 "The information in these fields is more reliable than values in the other fields. " \
                 "Analyze CAREFULLY the info in the 'Description' and 'explanation' fields, in cases where you can fill in other fields' values based on the info you found during the analysis of those fields - replace the exists values in the other fields with the info that was extracted from the 'Description' and 'explanation' fields." \
                 "For example, if the info in the existing 'attack's success rate - digital domain' is different between than the information that was extracted from the 'explanation' fields - change the value of the 'Attack's success rate - digital domain' to be the same as in the 'explanation' field)."##. at the end, don't add the 'explanation' field to the final response"####"Therefore, examine if there is contradict info between the info in this field and others, and prioritize info from this fields (for example, if the attack's success rate are different between the explanation and the 'Attack's success rate' value - change the inf oin 'Attack's success rate' to be the same as in the 'explanation' field)." \


    #print(prompt_sys)
    prompt_user_paper = pdf_text
    #(prompt_sys, prompt_user_paper, prompt_assis, prompt_user_valid,
    response = get_completion_validation(prompt_sys, prompt_user_paper, paper_f_ana,prompt_user_valid)
    #print(response)

    #json_output = text_to_json(response.choices[0].message["content"])
    res_sec_ana = response.choices[0].message.content
    paper_list_sec_analysis.append(res_sec_ana)
    print(res_sec_ana)
    # print("********************************************")
    # prompt_user_valid_by_model = ("what are the attacks' success rate (digital and physical) and what are the types of attacks of all the attacks"
    #                               " tested on the LResNet100E model? (based on the syste instructions)")
    # response_by_model = get_completion_validation(prompt_sys, prompt_user_paper, "lets say that you got an answer",prompt_user_valid_by_model)
    # print(response_by_model.choices[0].message.content)
    print("********************************************")

# Extracting JSON strings
    #json_string = re.findall(r'```json\n([\s\S]*?)\n```',res_sec_ana)
    # Regular expression for matching JSON objects and arrays
    json_regex =  r'\{(?:[^{}]|\{[^{}]*\})*\}|\[(?:[^\[\]]|\[[^\[\]]*\])*\]'    #r'(\{.*?\}|\[.*?\])'

    # Find all matches in the text
    json_string = re.findall(json_regex, res_sec_ana, re.DOTALL)

    # Converting JSON strings to Python lists of dictionaries
    #if len(json_string) != 0:
        #json_strings = re.findall(r'```json\n([\s\S]*?)```',res_sec_ana)


    '''
    # Converting JSON strings to Python lists of dictionaries
    try:
        json_list = [json.loads(js)[0] for js in json_strings]#[json.loads(js) for js in json_strings]
    except:
        json_list = [json.loads(js) for js in json_strings]
    '''

        # Parse each match as JSON
    json_list = []
    for match in json_string:
        try:
            json_object = json.loads(match)
            json_list+=(json_object)
        except json.JSONDecodeError:
            print("Invalid JSON detected and skipped:", match)

    json_lists+=(json_list)

    #all_jsons+=json_list[0]


    try:
        df = pd.DataFrame(json_list)
    except Exception:
        print("got exception : AttributeError: 'str' object has no attribute 'keys'\ncontinue to next article.")
        continue
    df['paper_name'] = paper_name

    df = df.reindex(columns=columns_order)

    # Iterate through the new data and add rows that don't exist in the existing CSV

    # Identify columns with dtype 'object' (typically string columns)
    string_columns = df.select_dtypes(include='object').columns

    # Fill NaN values in string columns with empty strings
    df[string_columns] = df[string_columns].fillna("")

    # Optionally, handle NaN values in numeric columns differently
    # For example, you can fill NaN values in numeric columns with a specific value like 0
    numeric_columns = df.select_dtypes(include='number').columns
    df[numeric_columns] = df[numeric_columns].fillna(0)


    # Write the DataFrame to an Excel file
    df.to_csv(csv_name, mode='a', index=False, header=False)

    print("********************************************")
