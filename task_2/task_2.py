import hashlib
import glob 

temp_store_dict = {}

for file in glob.glob('../task_2/data/*.data'): # loop through all files in the directory
    with open(file, 'rb') as f: # read files as raw bites (rb)
        data = f.read()
    
    hash_object = hashlib.sha3_256(data) # create hash object
    hex_dig = hash_object.hexdigest() # get the hexadecimal representation of the hash
    print(hex_dig)
    
    hex_key = 1
    for char in hex_dig:
        hex_key *= int(char, 16) + 1
        
    temp_store_dict[hex_key] = hex_dig
    
