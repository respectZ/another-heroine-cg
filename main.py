import sys
import requests
import json
import urllib3
import os

# disable warning
urllib3.disable_warnings()

# 1 for copy link to cg, else 0 download file
mode = 1

if os.environ["EMAIL"]:
    print("Login..")
else:
    print(os.environ["EMAIL"])
    print("Envionment hasn't been set.")
    exit()

# Funcs
def logContent(text):
    with open("./log.txt", "a", encoding="utf-8") as f:
        f.write(text)
        f.write("\n")

def downloadImage(url):
    fName = url.split("/item/")[1]
    if(os.path.isfile(f"./images/{fName}")):
        return
    print(f"Downloading {fName} ...")
    img_data = requests.get(url, verify=False).content
    with open(f'./images/{fName}', 'wb') as handler:
        handler.write(img_data)
        print(f"{fName} Done!")

def updateCGList(imgs=[], mode=1):
    if mode == 0:
        imgs = ["./images/" + x.split("item/")[1] for x in imgs if "item/" in x]
    with open("./cgtest.txt", "a", encoding="utf-8") as f:
        for i in imgs:
            f.write(i + "\n")

def mainBatch(start=5010011, step=70000, mode=1):
    # Main Code
    homepage = "https://www.123chat.jp"
    s = requests.session()

    # Get Token
    data = s.get(homepage, verify=False).text
    token = data.split('name="token" value="')[1].split('"')[0]

    loginData = {
        "email": os.environ["EMAIL"],
        "password": os.environ["PASSWORD"],
        "token": token
    }


    # Login
    w = s.post(homepage + "/enter/authentication/", data=loginData)


    # main ?
    test = s.get(homepage + "/album", verify=False).text

    # set headers
    s.headers.update({"content-type": "application/x-www-form-urlencoded; charset=UTF-8"})

    # # Fetch Gallery
    # id starts from 501001 ?
    # up to          600996, 600997 not found
    # cour 1 : - 70000
    # cour 2 : - 140000
    # cour 3 : - 210000
    # cour 4 : - 280000
    # cour 5 : - 350000
    # cour 6 : - 420000
    # cour 7 : - 490000
    # or brute force from 100 to 1000000
    imgs = []
    for i in range(start, start+step):
        data = s.post(homepage + "/album/data/", data=f"id={i}")
        # idiot solution
        dataJSON = json.loads(data.text[1:])
        if(dataJSON['success'] == 0 or dataJSON['error'] == 1):
            continue
        # prevent dupe imgs
        if dataJSON['image'] not in imgs:
            imgs.append(dataJSON['image'])
        if mode == 0:
            downloadImage(dataJSON['image'])
        elif mode == 1:
            print(f"Found: {dataJSON['image']}")
        else:
            print("Undefined Mode")
            break
    updateCGList(imgs, 1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Not Enough args [start] [step]")
    else:
        start = int(sys.argv[1])
        step = int(sys.argv[2])
        try:
            mode = int(sys.argv[3])
        except IndexError:
            mode = 1
        mainBatch(start=start, step=step, mode=mode)