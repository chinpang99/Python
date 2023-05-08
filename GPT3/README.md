These script allowed user to extract information from GPT3 API

# How to use the script:
1. Run **GPT3_extraction.py** and input below arguments:

- python3 GPT3_extraction.py --input_path /Users/chinpangchia/Desktop/game_result.csv --output_path /Users/chinpangchia/Desktop/
    

2. After that, the script will extract the raw result from GPT3 and generate triplets format in triplets column


3. Run **GPT3_data_augmentation.py** by inputting below arguements. The script will convert the extracted data to triplets Json format:
    
- python3 GPT3_data_augmentation.py --input_path /Users/chinpangchia/Desktop/game_result.xlsx