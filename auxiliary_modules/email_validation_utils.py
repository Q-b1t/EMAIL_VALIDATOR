import requests
import json
from tqdm.auto import tqdm
import pandas as pd

def debounce_api_request(mail,api_key):
    url = f"https://api.debounce.io/v1/?api={api_key}&email={mail}"
    response = requests.get(url=url)
    return response

def get_verification_responses(mail_list,api_key,verbose):
    responses = list()
    if verbose:
        for mail in tqdm(mail_list):
            response = debounce_api_request(mail=mail,api_key=api_key)
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

def get_email_verification_table(json_samples,codes = {
    1 : "Not an email",
    2: "Spam-trap by ESPs",
    3: "A temporary, disposable address",
    4: "A domain-wide setting",
    5: "Verified as real address",
    6: "Verified as invalid (Bounce)",
    7: "The server cannot be reached",
    8: "See roles column"
    }):
    processed_samples = [process_debounce_sample(json_sample) for json_sample in json_samples]
    processed_table = pd.DataFrame(processed_samples)
    processed_table["validation_additional_information"] = processed_table["code"].apply(lambda x : codes[int(x)])
    return processed_table