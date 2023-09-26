# Email Validator
This is a script used to automate the validation of emails (whether the email inbox exists or not) using the [Debounce API](https://debounce.io/solutions/api/). 
# Prerequisites
- Generate an API key from Debounce by creating an acccout.
- Have enough credits to make the required number of queries.
## Note about credits
In Debounce, one can buy credits based on the number of queries needed. Generally, *1 query = 1 credit*. The API does not charge credits for unsuccesfull results (non completed requests).

# Usage
The script emulates a command line interface command. Before running it, the pertinent dependencies must be installed. It is recomended to create a python virtual environment to do so.
Inside the environment, one can run the command ```pip3 install -r requirements.txt``` to install the corresponding dependencies.
## Creating input and output folders
In order to run the script, one must create the following folders at the same directory level as the script at hand:
- ```inputs```: In this folder goes the input file (excel book containing a merged table of emails from different sources).
- ```outputs```: In this folder, the outpul file will be stored once the script's execution ends.
## Setting up the configuration file
There is a configuration file named ```conf.cfg```. Inside, there is an empty key ```debounce```. In order for the script to work, you must assign your Debounce API key as value to this parameter.
### Example
```
[API_KEY]
debounce = 35shs2tsfs42sd
```
## Run the script
Once the configuratin file has been set up and the input and output folders have beed created, one can run the script by running:
```python ./main.py```.
As it was stated earlier, the script emulates a CLI. Therefore, there are parameters that can be specified in the form of flags. To view information about the flags, one can run one of the following commands:
- ```python ./main.py --help``` 
- ```python ./main.py -h```

The parameters that can be set up and changed are:
- ```--input_file```: The name and location of the input file.
- ```--output_file```: The name and location of the output file.
- ```--config_file```: The name and location of the configuration file.
- ```--verbose```: Whether or not no make the output verbose (display on console what is going on and a progress bar of the mails validated).

## Example:
```
python .\main.py -i .\imerged_data_.xlsx -c .\conf_file.cfg -v True
```