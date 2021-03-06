# Use python 3
import pickle, hashlib

# Constants
LOOKUP_TABLE_SIZE = 8000000
HASH_CHAIN_LENGTH = 1000
# Chance hash chains don't have plaintext (ignoring collisions)
PLAINTEXT_MISS = 0.01 




def create_combinations(alphabet_type, range_start, range_end):
    """Create a generator of all combinations of alphabet_type from
    range_start to range_end.
    
    Alphabets:  loweralpha, loweralpha_numeric, loweralpha_numeric_space
                mixalpha_numeric, mixalpha_numeric_space
    """
    import string, itertools
    
    # Bytestring constants
    lowercase = [x.encode(encoding='utf-8') for x in string.ascii_lowercase]
    mixcase = lowercase + [x.encode(encoding='utf-8') for x in string.ascii_uppercase]
    digits = [x.encode(encoding='utf-8') for x in string.digits]
    space = [" ".encode(encoding='utf-8')]
    
    alphabets = {"loweralpha": lowercase, 
                 "loweralpha_numeric": lowercase + digits,
                 "loweralpha_numeric_space": lowercase + digits + space,
                 "mixalpha_numeric": mixcase + digits,
                 "mixalpha_numeric_space": mixcase + digits + space,
                 }
        
    alphabet = alphabets[alphabet_type]
    
    print("Generating combinations...")
    
    # Generator of products of all lengths
    def create_all():
        for i in range(range_start, range_end+1): 
            yield itertools.product(alphabet, repeat=i) 
    
    # Flatten combinations into single generator
    combinations = itertools.chain.from_iterable(create_all())      
        
    return (combinations, len(alphabet))


def write_to_file(file_name, table):
    # Optional: use gzip
    # import gzip
    with open(file_name + '.p', 'wb') as f:
        pickle.dump(table, f, pickle.HIGHEST_PROTOCOL)
        
        
def create_hashlib(hash_type):
    """Creates hashlib object.
    
    Hashes: md5, sha1, sha256, sha512
    """
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
    
    return h



def create_lookup_table(hash_type, alphabet_type, range_start, range_end):
    """Creates a lookup table of hash_type using the alphabet from alphabet_type.
    The table will be made of all combinations of length range_start to range_end
    and will be written to a file. 
    
    See create_hashlib for hashes that can created and create_combinations for
    possible alphabet types.
   """
   # Friendly warning
    if range_end >= 5:
        print("That's a big file - Are you sure?")
        

    combinations = create_combinations(alphabet_type, range_start, range_end)[0]
    h = create_hashlib(hash_type)
      
    file = "tables/{}_{}#{}-{}".format(hash_type, alphabet_type, range_start, range_end)
    
    count = 0
    file_number = 0
    file_full = file + "_" + str(file_number)
    
    print("Hashing, writing to file...")
        
    lookup_table = {} 
    
    for combination in combinations:
        combination = b''.join(combination) # Single bytestring
        
        current_hash = h.copy() # New hash object
        current_hash.update(combination)
        digest = current_hash.digest()
        
        lookup_table[digest] = combination # Add entry {hash: data}
        
        if count == LOOKUP_TABLE_SIZE: # Reset for new file
            file_full = file + "_" + str(file_number)
            print("*File", file_number)
            write_to_file(file_full, lookup_table)
            
            file_number += 1    
            lookup_table = {}
            count = 0
        
        count += 1

    write_to_file(file_full, lookup_table) # Last file write
    #print(lookup_table)
    
    # Starting from 0
    print("Done! Dictionary entries:", file_number*LOOKUP_TABLE_SIZE+count+1) 
        
        
def table_lookup(hash_value, file):
    """Looks up a hash from a pre-computed lookup table as file.
    
    Enter your file name in up to the character range (ex. 1-5)
    """
    import os.path, binascii
    file_number = 0
    
    while True:
        full_path = file + "_" + str(file_number) + '.p'
        print("Searching " + full_path + " ...")
        
        if os.path.isfile(full_path): # If numbered file exists
            with open(full_path, 'rb') as f:
                lookup_table = pickle.load(f)

            try:
                data = lookup_table[binascii.unhexlify(hash_value)]
                return "Original text: " + data.decode(encoding='utf-8')
                break
            except:
                file_number += 1
        else:
            raise Exception("Hash not found or file doesn't exist!")
        
        
def create_rainbow_table(hash_type, alphabet_type, length):
    """Creates pre-computed hash chains (currently) of hash_type using the 
    alphabet of alphabet_type. Each password is length long. 
    
    See create_hashlib for hashes that can created and create_combinations for
    possible alphabet types.
    """
    import math
    
    combinations, chars = create_combinations(alphabet_type, length, length)
    h = create_hashlib(hash_type)
    
    file_full = "tables/{}_{}#{}".format(hash_type, alphabet_type, length)
    
    # miss = (1 - 1/(num chars)^length)^(total hashes)
    total_hashes = math.log(PLAINTEXT_MISS) / math.log(1 - 1/chars**length)
    chains = int(total_hashes / HASH_CHAIN_LENGTH) 
    
    print(chains)
    
    
    
    
create_rainbow_table("md5", "mixalpha_numeric", 2)
    
    
