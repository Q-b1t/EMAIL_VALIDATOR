import configparser
from argparse import ArgumentParser,Namespace
import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from auxiliary_modules.email_validation_utils import *
from termcolor import colored

if __name__ == '__main__':
    # create the cli arguments
    parser = ArgumentParser()
    parser.add_argument("-c","--config_file",help="Configuration file contianing the API keys (default: \"conf.cfg\")",type=str,default="conf.cfg",nargs="?")
    parser.add_argument("-i","--input_file",help="Input file containing (excel book) containing the emails to check (default: \"merged_data.xlsx\")",type=str,default="./inputs/merged_data.xlsx",nargs="?")
    parser.add_argument("-o","--output_file",help="Name of the output file the hostnames will be exported to (default: \"email_verified.xlsx\")",type=str,default="./outputs/email_verified.xlsx",nargs="?")
    parser.add_argument("-v","--verbose",help="Whether to output into the console information about the script's progress or not",type=bool,default=False,nargs="?")
    args: Namespace = parser.parse_args()
    config_file = args.config_file
    input_file = args.input_file
    output_file = args.output_file
    verbose = args.verbose

    # parse the configuration file
    config = configparser.ConfigParser()
    config.read(config_file)
    assert config['API_KEY']['debounce'] != None, colored("[-] The configuration file does not contain an API key of the format is not the appropiate one.","red")

    DEBOUNCE_API_KEY = config['API_KEY']['debounce']

    # validate read the input file 
    assert input_file.split(".")[1] != "xlsx" and input_file.split(".")[1] != "csv",colored("[-] Input file must be either an excel book or a csv file.","red")
    if verbose:
        print(colored(f"[*] Reading file {input_file}","blue"))
    input_data = pd.read_excel(input_file)
    input_data["email"] = input_data["email"].apply(lambda x : str(x).lower())
    
    # validate if the excel book has a valid format 
    assert "email" in input_data.columns, colored("[-] The file is not in the correct format. Make sure the excel book has \"email\" column.","red")
    email_list = list(set(input_data["email"].to_list()))
    if verbose:
        print(colored(f"[+] Found {len(email_list)} potential emails.","green"))
    
    # make the api requests and parse the responses into a table
    if verbose:
        print(colored("[*] Validating emails...","blue"))
    responses = get_verification_responses(mail_list=email_list,api_key=DEBOUNCE_API_KEY,verbose=verbose)
    json_dumps = [response.text for response in responses]
    email_verification_tables = get_email_verification_table(json_samples=json_dumps)
    # merge the responses with the original data and export to the output file
    assert output_file.split(".")[1] != "xlsx" or output_file.split(".")[1] != "csv",colored("[-] Output file must be either an excel book or a csv file.","red")
    if verbose:
        print(colored(f"[+] Exporting the results to {output_file}.","green"))
    export_data = input_data.merge(email_verification_tables,how="outer",on="email")
    export_data.to_excel(output_file)