# Python 3

import pickle, hashlib, itertools, binascii, gzip

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
    combinations = ()
    for i in range(range_start, range_end+1):
        combinations += tuple(itertools.product(alphabet, repeat=i))
    combinations = iter(combinations)
    
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
    
    print("Hashing...")
    rainbow_table = {}
    for combination in combinations:
        combination = b''.join(combination)
        
        current_hash = h.copy() # New hash object
        current_hash.update(combination)
        digest = current_hash.digest()
        
        rainbow_table[digest] = combination # Add entry {hash: data}
        
    file = "tables/{}_{}#{}-{}".format(hash_type, alphabet_type, range_start, range_end)
    
    print("Writing to file...")
    with gzip.open(file + '.pickle', 'wb') as f:
        pickle.dump(rainbow_table, f, pickle.HIGHEST_PROTOCOL)
    
    print("Done!")
        
        
def table_lookup(hash_value, file):
    """Looks up a hash from a pre-computed rainbow table as file."""
    with gzip.open(file + '.pickle', 'rb') as f:
        rainbow_table = pickle.load(f)
            
    try:
        data = rainbow_table[binascii.unhexlify(hash_value)]
        return data.decode(encoding='utf-8')
    except:
        raise Exception("Can't find hash")
    

def main():
    create_table("sha256", "mixalpha_numeric_space", 1, 3)
    # print(table_lookup("1fad0e4bfb59d3c0e8229ede1f6d26b3", "tables/md5_loweralpha_numeric_space#1-4"))

main()