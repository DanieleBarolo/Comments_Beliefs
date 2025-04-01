import requests  

def download_file_content(api_key, output_file_id, output_file):
    url = f"https://api.groq.com/openai/v1/files/{output_file_id}/content"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    response = requests.get(url, headers=headers)
    
    # Write the content to a file
    with open(output_file, 'wb') as f:
        f.write(response.content)

    return f"File downloaded successfully to {output_file}"

# Usage example
api_key = "YOUR_GROQ_API_KEY"
output_file_id = "file_01jh6xa97be52b7pg88czwrrwb" # replace with your own completed batch job's `output_file_id`
output_file = "batch_output.jsonl" # replace with your own file of choice to download batch job contents to

try:
    result = download_file_content(api_key, file_id, output_file)
    print(result)

except Exception as e:
    print(f"Error: {e}")