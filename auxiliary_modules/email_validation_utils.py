import requests
import json
from tqdm.auto import tqdm
import pandas as pd
import os
from termcolor import colored
import configparser


def get_api_key(config_file,api,verbose):
    # parse the configuration file
    validate_config_file(config_file=config_file)
    config = configparser.ConfigParser()
    config.read(config_file)
    assert api == "abstract" or api == "debounce", colored("The specified api {api} is not valid. Please use \"abstract\" or \"debounce\"","red")
    assert config['API_KEYS'][api] != "" ,colored(f"[-] The configuration file does not contain a {api} API key of the format is not the appropiate one.","red")
    return config['API_KEYS'][api]

def validate_config_file(config_file):
    assert  os.path.isfile(config_file),colored(f"[-] Configuration file {config_file} does not seem to exist. Please check for any errors.","red")

def validate_output_file(output_file):
    # validate if outfile file contains no extentions and if the save path exist
    assert "xlsx" not in output_file or  "csv" not in output_file, colored(f"[-] The output file should only be limited to the name. Please ommit the extention.","red")
    if output_file.find("/") != -1 or output_file.find("\\") != -1:
        path = os.path.dirname(output_file)
        assert os.path.exists(path=path), colored(f"The path {path} does not seem to exist.","red")

def validate_name(filename,verbose):
    # validate if the input file exist and if it contains an allowed extention
    assert  os.path.isfile(filename),colored(f"[-] Specified file {filename} does not seem to exist. Please check for any errors.","red")
    extention = filename.split(".")[-1]
    assert  extention != "csv" or extention != "txt" or extention != "xlsx" ,colored(f"[-] Specified file {filename} is not in an allowed format (xlsx,csv,txt).","red")
    if verbose:
        print(colored(f"[+] File {filename} found.","green"))

def debounce_api_request(mail,api_key):
    url = f"https://api.debounce.io/v1/?api={api_key}&email={mail}"
    response = requests.get(url=url)
    return response

def abstract_api_request(mail,api_key):
    url = f"https://emailvalidation.abstractapi.com/v1/?api_key={api_key}&email={mail}"
    response = requests.get(url=url)
    return response

def read_text_file(filename):
    with open(filename,"r",encoding="utf-8") as f:
        lines = f.readlines()
    f.close()
    return [line.strip() for line in lines]

def get_mail_df(filename):
    mails = read_text_file(filename=filename)
    mails_table = pd.DataFrame({"email":mails})
    return mails_table 

def get_emails_data_table(input_file,verbose):
    extention = input_file.split(".")[-1]
    if verbose:
        print(colored(f"[*] Reading and normalizing data from file {input_file}","blue"))
    
    if extention == "xlsx":
        input_data = pd.read_excel(input_file)
    elif extention == "csv":
        input_data = pd.read_csv(input_file)
    else: # txt file
        input_data = get_mail_df(filename=input_file)
    
    assert "email" in input_data.columns, colored("[-] The file is not in the correct format. If it is either a csv file or an excel book,  please make sure it has an \"email\" column.","red")
    input_data["email"] = input_data["email"].apply(lambda x : str(x).lower())
    return input_data

def get_email_list(input_data,verbose):
    email_list = list(set(input_data["email"].to_list()))
    if verbose:
        print(colored(f"[+] Found {len(email_list)} unique emails.","green"))
    return email_list

def get_verification_responses(mail_list,api,api_key,verbose):
    if verbose:
        print(colored("[*] Validating emails...","blue"))
    responses = list()
    if verbose:
        if api == "abstract":
            for mail in tqdm(mail_list):
                response = abstract_api_request(mail=mail,api_key=api_key)
                if response.status_code == 200:
                    responses.append(response)
        else:
            for mail in tqdm(mail_list):
                response = debounce_api_request(mail=mail,api_key=api_key)
                if response.status_code == 200:
                    responses.append(response)      
    else:
        if api == "abstract":
            for mail in mail_list:
                response = abstract_api_request(mail=mail,api_key=api_key)
                if response.status_code == 200:
                    responses.append(response) 
        else:
            for mail in mail_list:
                response = debounce_api_request(mail=mail,api_key=api_key)
                if response.status_code == 200:
                    responses.append(response) 
    return responses

def process_debounce_sample(json_dump,columns_delete = ["reason","send_transactional"]):
    json_dict = json.loads(json_dump)
    processed = pd.Series(json_dict["debounce"])
    processed.drop(columns_delete,inplace=True)
    return processed

def process_abstract_sample(json_dump):
    keys = ["is_valid_format","is_free_email","is_disposable_email","is_role_email","is_catchall_email","is_mx_found","is_smtp_valid"]        

    json_dict = json.loads(json_dump)
    for key in keys:
        json_dict[key] = json_dict[key]["text"]
    return pd.Series(json_dict)

def get_email_verification_table_absract(json_samples):
    processed_samples = [process_abstract_sample(json_sample) for json_sample in json_samples]
    processed_table = pd.DataFrame(processed_samples)
    return processed_table


def get_email_verification_table(responses,api,codes = {
    1 : "Not an email",
    2: "Spam-trap by ESPs",
    3: "A temporary, disposable address",
    4: "A domain-wide setting",
    5: "Verified as real address",
    6: "Verified as invalid (Bounce)",
    7: "The server cannot be reached",
    8: "See roles column"
    }):
    json_dumps = [response.text for response in responses]
    processed_samples = [process_abstract_sample(json_sample) for json_sample in json_dumps] if api == "abstract" else [process_debounce_sample(json_sample) for json_sample in json_dumps]
    processed_table = pd.DataFrame(processed_samples)
    if "code" in processed_table.columns:
        processed_table["validation_additional_information"] = processed_table["code"].apply(lambda x : codes[int(x)])
    return processed_table

def merge_table(emails_table,validation_table):
    merged_table = emails_table.merge(validation_table,how="outer",on="email")
    return merged_table

def save_table(parsed_table,save_path,output_format,verbose):
    """
    Inputs: 
        - parsed_table: A processed pandas dataframe.
        - save_path: The to which the table will be saved as an excel book.
    """
    if output_format == "csv":
        filename = save_path + "." + "csv"
        parsed_table.to_csv(filename,index = False)
    else:
        filename = save_path + "." + "xlsx"
        parsed_table.to_excel(filename, index=False)
         
    if verbose:
        print(colored(f"[+] Exporting the results to {save_path}.","green"))