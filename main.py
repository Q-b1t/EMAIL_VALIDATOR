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
    parser.add_argument("-i","--input_file",help="Input file containing (excel book) containing the emails to check (default: \"merged_data.xlsx\")",type=str,default="merged_data.xlsx",nargs="?")
    parser.add_argument("-o","--output_file",help="Name of the output file the hostnames will be exported to (default: \"email_verified\")",type=str,default="email_verified",nargs="?")
    parser.add_argument("-v","--verbose",help="Whether to output into the console information about the script's progress or not",type=bool,default=False,nargs="?")
    parser.add_argument("-f","--output_format",help="It can be either \"excel\" or \"csv\" (default: \"excel\")",type=str,default="excel",nargs="?")
    parser.add_argument("-a","--api",help="It can be either \"abstract\" or \"debounce\" (default: \"abstract\")",type=str,default="abstract",nargs="?")
    # fetcth the specified parameters
    args: Namespace = parser.parse_args()
    config_file = args.config_file
    input_file = args.input_file
    output_file = args.output_file
    verbose = args.verbose
    output_format = args.output_format
    api = args.api


    # retrieve the api key
    API_KEY = get_api_key(config_file=config_file,api=api,verbose=verbose)

    # validate the input file
    validate_name(filename=input_file,verbose=verbose)
    
    # validate the output file
    validate_output_file(output_file=output_file)

    # fetch the data from the input file
    input_data = get_emails_data_table(input_file=input_file,verbose=verbose)
    
    # get emails list
    email_list = get_email_list(input_data=input_data,verbose=verbose)

    # make the api requests and parse the responses into a table
    responses = get_verification_responses(mail_list=email_list,api=api,api_key=API_KEY,verbose=verbose)

    # parse the responses
    email_verification_table = get_email_verification_table(responses=responses,api=api)

    # merge the original input data with the verification table
    merged_table = merge_table(emails_table=input_data,validation_table=email_verification_table)

    # save the table
    save_table(parsed_table=merged_table,save_path=output_file,output_format=output_format,verbose=verbose)

    export_valid_mail_list(verified_table=merged_table,api=api,output_file=output_file,verbose=verbose)