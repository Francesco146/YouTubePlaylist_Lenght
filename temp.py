import json
with open('users.json') as json_file:
            data = json.load(json_file)
            passwords = data['users']
print(passwords)



for i in range(len(passwords)):
    if "tempo" in passwords[i]["id"] and "t3mpo" in passwords[i]["passwd"]:
        print("Si")
        break
    else:
        print("No")