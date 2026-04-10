import hashlib
import glob 

pairs = []
    
for file in glob.glob('../task_2/data/*.data'): 

    with open(file, 'rb') as f: 
        data = f.read()
    
    hash_object = hashlib.sha3_256(data) 
    hex_dig = hash_object.hexdigest() 
    
    # print(hex_dig)
    
    hex_key = 1
    for char in hex_dig:
        hex_key *= int(char, 16) + 1
    
    pairs.append((hex_key, hex_dig))
    

print(f'files processed: {len(pairs)}')

sorted_pairs = sorted(pairs, key=lambda x: x[0]) # sort the list of tuples by the first element (hash)

final_str = ''.join(value for _, value in sorted_pairs)

combined_str = final_str + 'serik.nuradil@gmail.com'

# final hash
final_hash = hashlib.sha3_256(combined_str.encode()).hexdigest()
    
print(final_hash)

