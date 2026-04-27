import requests
import json
import sys
import os

BASE_URL = "http://10.11.99.1"

def list_folder(subfolder = "", show =False):
    """Fetch a single post from the API"""
    url = f"{BASE_URL}/documents/{subfolder}"
    
    # Make HTTP GET request
    response = requests.get(url)
    
    # Parse JSON response
    post = response.json()
    if show:
        for p in post:
            if p["Type"] != "DocumentType":
                print(f"- 🗁  {p["VisibleName"]}, {p["ID"]}")
            else:
                print(f"- 🖹  {p["VisibleName"]}")
    return post

def upload_file(file_path):
    url = f"{BASE_URL}/upload"
    with open(file_path, 'rb') as f:
        # Prepare the multipart form data
        files = {
            'file': (file_path, f, 'application/pdf')
        }
        
        # Set headers as shown in the curl example
        
        # Make the POST request
        response = requests.post(
            url,
            files=files,
        )
        if response.status_code == 201:
            print("fitxer pujat correctament")
        else:
            print(f"Resposta {response.status_code}, possible error")

def download_file(id, output_dir = "."):
    url = f"{BASE_URL}/download/{id}/pdf"
    print(f"Downloading notebook: {id}")
    print(f"From: {url}\n")
    
    try:
        # Make the GET request
        response = requests.get(url)
        
        # Check if download was successful
        if response.status_code == 200:
            # Get filename from headers or use guid
            content_disposition = response.headers.get('content-disposition', '')
            if 'filename' in content_disposition:
                filename = content_disposition.split('filename=')[1].strip('"')
            else:
                filename = f"{id}.pdf"
            
            # Save the file
            file_path = os.path.join(output_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✓ Download successful!")
            print(f"Saved to: {file_path}")
            print(f"File size: {len(response.content)} bytes")
            return file_path
        else:
            print(f"✗ Download failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return None
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def get_id_path(path):
    current_id = ""
    for f in path.split('/'):
        folders = list_folder(subfolder=current_id)
        for e in folders:
            if e["VisibleName"] == f and e["Type"]:
                current_id = e["ID"]
    return current_id

def main():
    if len(sys.argv)>=2:
        if sys.argv[1] == "-l":
            if len(sys.argv) >= 3:
                list_folder(subfolder=sys.argv[2])
            else: list_folder()
        elif sys.argv[1] == "-u":
            upload_file(sys.argv[2])
        elif sys.argv[1] == "-d":
            id = get_id_path(sys.argv[2])
            download_file(id)
    else:
        com = ""
        path = [{"ID": "", "VisibleName": ""}]
        while com != "exit":
            com = input(f"{"/".join([path[i]["VisibleName"] for i in range(1, len(path))])}> ")
            coms = com.split(" ")
            if len(coms) > 0:
                if coms[0] == "ls":
                    list_folder(subfolder=path[-1]["ID"], show = True)

                elif coms[0] == "cd":
                    folders = list_folder(subfolder=path[-1]["ID"])
                    if coms[1] == "..":
                        path.pop()
                    else:
                        for e in folders:
                            if e["VisibleName"] == coms[1]:
                                path.append(e)
                                print(path[-1])
                                break




if __name__ == "__main__":
    main()
