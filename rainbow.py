# Use python 3

import pickle, hashlib, itertools, binascii

# Constants
TABLE_SIZE = 8000000

def create_table(hash_type, alphabet_type, range_start, range_end):
    """Creates a rainbow table of hash_type using the alphabet from alphabet_type.
    The table will be made of all combinations of length range_start to range_end
    and will be written to a file. 
    
    Alphabets: loweralpha, loweralpha_numeric, loweralpha_numeric_space
               mixalpha_numeric, mixalpha_numeric_space
               
    Hashes: md5, sha1, sha256, sha512  
   """
    
    # Bytestring constants
    lowercase = [x.encode(encoding='utf-8') for x in "abcdefghijklmnopqrstuvwxyz"]
    mixcase = lowercase + [x.encode(encoding='utf=8') for x in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]
    digits = [x.encode(encoding='utf-8') for x in "0123456789"]
    space = [" ".encode(encoding='utf-8')]
    
    alphabets = {"loweralpha": lowercase, 
                 "loweralpha_numeric": lowercase + digits,
                 "loweralpha_numeric_space": lowercase + digits + space,
                 "mixalpha_numeric": mixcase + digits,
                 "mixalpha_numeric_space": mixcase + digits + space}
        
    alphabet = alphabets[alphabet_type]
    
    print("Creating combinations...")
    # Generator of products of all lengths
    def create_combinations():
        for i in range(range_start, range_end+1): 
            yield itertools.product(alphabet, repeat=i) 
    
    # Flatten combinations into single generator
    combinations = itertools.chain.from_iterable(create_combinations())
    
    
    if hash_type == "md5":
        h = hashlib.md5()
    elif hash_type == "sha1":
        h = hashlib.sha1()
    elif hash_type == "sha256":
        h = hashlib.sha256()
    elif hash_type == "sha512":
        h = hashlib.sha512()
    else:
        raise Exception("Bad hash name")
    

    rainbow_table = {} 

    i = 0
    file_number = 0
    file = "tables/{}_{}#{}-{}_".format(hash_type, alphabet_type, range_start, range_end)
    file_full = file + str(file_number)
    
    print("Hashing, writing to file...")
    
    def write_to_file(file_name):
        # Optional: use gzip
        # import gzip
        with open(file_name + '.p', 'wb') as f:
            pickle.dump(rainbow_table, f, pickle.HIGHEST_PROTOCOL)
        
    
    for combination in combinations:
        combination = b''.join(combination) # Single bytestring
        
        current_hash = h.copy() # New hash object
        current_hash.update(combination)
        digest = current_hash.digest()
        
        rainbow_table[digest] = combination # Add entry {hash: data}
        
        if i == TABLE_SIZE: # Reset for new file
            file_full = file + str(file_number)
            print("*File", file_number)
            write_to_file(file_full)
            
            i = 0
            file_number += 1    
            rainbow_table = {}
        
        i += 1

    write_to_file(file_full) # Last file write

    print("Done!")
        
        
def table_lookup(hash_value, file):
    """Looks up a hash from a pre-computed rainbow table as file."""
    with gzip.open(file + '.p', 'rb') as f:
        rainbow_table = pickle.load(f)
            
    try:
        data = rainbow_table[binascii.unhexlify(hash_value)]
        return data.decode(encoding='utf-8')
    except:
        raise Exception("Can't find hash")
    

def main():
    create_table("md5", "loweralpha_numeric_space", 1, 5)
    #print(table_lookup("1fad0e4bfb59d3c0e8229ede1f6d26b3", "tables/md5_loweralpha_numeric_space#1-4_0"))

main()