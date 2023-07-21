These script allowed user to pre-process data from chatGPT, annotator's result, pseudocode

# How to use the script:
# 1. ChatGPT

Step 1: Run **annotation_absa.py** to perform annotation using chatGPT. After that, the script will generate triplets column

*Arguements*:
- python3 annotation_absa.py --annotator ChatGPT --input_path /Users/chinpangchia/Desktop/test.anno_chatgpt.csv --column content --api_key sk-xxx --pause_time 0.5

Arguement | Description | Example
| ------------- |:-------------:|:-------------:|
annotator | Selection of either **ChatGPT, GPT3, ChatGPTWeb** | ChatGPT
input_path | Input file | /Users/{user_environment}/Desktop/test.anno_chatgpt.csv
column | Content column name | content
api_key | OpenAI API key | sk-xxx
pause_time | Pause time for every API call [to prevent run-time error] | 0.5

Step 2: Run **main.py** from *game_gas_format_file_creation_process folder* to create game & gas format

*Arguements*:
- python3 main.py --new_data_input_path /Users/chinpangchia/Desktop/test.anno_chatgpt_v1.2.csv --old_data_input_path /Users/chinpangchia/Desktop/test.anno_chatgpt_v1.1.csv --data_output_path /Users/chinpangchia/Desktop/ --version 1.0 --train 1 --valid 0 --test 0 --to_format gas

Arguement | Description | Example
| ------------- |:-------------:|:-------------:|
new_data_input_path | Input file that need to process | /Users/{user_environment}/Desktop/test.anno_chatgpt_v1.2.csv
old_data_input_path | Old file but the data need to be remove if exist in new_data_input_path | /Users/{user_environment}/Desktop/test.anno_chatgpt_v1.1.csv
data_output_path | File location to save output data | /Users/{user_environment}/Desktop/
version | Output data version | 1.0
train | Training data split ratio | 1
valid | Valid data split ratio | 0
test | Testing data split ratio | 0
to_format | Produce gas data | gas



# 2. Annotator's Result

Step 1: Run **annotators_data_augmentation.py** to create triplets json format
-- python3 annotators_data_augmentation.py --emoji_choices text_with_emoji --truncation False --input_path /Users/chinpangchia/Desktop/ABSA/test.anno_chatgpt_v1.1.csv --output_path /Users/chinpangchia/Desktop/ABSA

*Arguements*:
Arguement | Description | Example
| ------------- |:-------------:|:-------------:|
emoji_choices | The output should display either **text_with_emoji, emoji_to_text or text_without_emoji** | text_with_emoji
truncation | Whether want truncate sentence or not: True/False | True
input_path | Input file | /Users/chinpangchia/Desktop/ABSA/test.anno_chatgpt_v1.1.csv
output_path | Output file | /Users/chinpangchia/Desktop/ABSA

Step 2: Run **main.py** from *game_gas_format_file_creation_process folder* to create game & gas format

*Arguements*:
- python3 main.py --new_data_input_path /Users/chinpangchia/Desktop/test.anno_chatgpt_v1.2.csv --old_data_input_path /Users/chinpangchia/Desktop/test.anno_chatgpt_v1.1.csv --data_output_path /Users/chinpangchia/Desktop/ --version 1.0 --train 1 --valid 0 --test 0 --to_format gas

Arguement | Description | Example
| ------------- |:-------------:|:-------------:|
new_data_input_path | Input file that need to process | /Users/{user_environment}/Desktop/test.anno_chatgpt_v1.2.csv
old_data_input_path | Old file but the data need to be remove if exist in new_data_input_path | /Users/{user_environment}/Desktop/test.anno_chatgpt_v1.1.csv
data_output_path | File location to save output data | /Users/{user_environment}/Desktop/
version | Output data version | 1.0
train | Training data split ratio | 1
valid | Valid data split ratio | 0
test | Testing data split ratio | 0
to_format | Produce gas data | gas


# 3. Pseudocode Result

Step 1: Run **annotation_absa.py** to create triplets json format 

*Arguements*: 
- python3 annotation_absa.py --input_path /Users/chinpangchia/Desktop/test.anno_chatgpt.txt

Arguement | Description | Example
| ------------- |:-------------:| :-------------:|
input_path | Input file | /Users/{user_environment}/Desktop/test.anno_chatgpt.txt

Step 2: Run **main.py** from *game_gas_format_file_creation_process folder* to create game & gas format

*Arguements*:
- python3 main.py --new_data_input_path /Users/chinpangchia/Desktop/test.anno_chatgpt_v1.2.csv --old_data_input_path /Users/chinpangchia/Desktop/test.anno_chatgpt_v1.1.csv --data_output_path /Users/chinpangchia/Desktop/ --version 1.0 --train 1 --valid 0 --test 0 --to_format gas

Arguement | Description | Example
| ------------- |:-------------:|:-------------:|
new_data_input_path | Input file that need to process | /Users/{user_environment}/Desktop/test.anno_chatgpt_v1.2.csv
old_data_input_path | Old file but the data need to be remove if exist in new_data_input_path | /Users/{user_environment}/Desktop/test.anno_chatgpt_v1.1.csv
data_output_path | File location to save output data | /Users/{user_environment}/Desktop/
version | Output data version | 1.0
train | Training data split ratio | 1
valid | Valid data split ratio | 0
test | Testing data split ratio | 0
to_format | Produce gas data | gas