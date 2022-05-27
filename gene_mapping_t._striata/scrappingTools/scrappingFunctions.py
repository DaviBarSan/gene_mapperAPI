
#function to create a list with query id
def query_acess_number(string_line): 
    #(?<=y\s) means lookahead regex match and do not count 'y=' + '\s' (== whitespace) in match result
    query_access_number = re.search(r"(?<=y=\s)...\w+...(?=\w)", string_line)
    return query_access_number.group()
    
#funtion that returns enzyme name data in current line
def query_name(string_line):    
    try:
        query_name = re.search(r"(?<=\.\d\s\b)\w...+(?=\[)", line)
        return query_name.group()
    except AttributeError:
        try:
            query_name = re.search(r"(?<=\.\d\s\b)\w...+", line)
            return query_name.group()
        except AttributeError:
            query_name = re.search(r"(?<=Full=)\w...+", line)
            return query_name.group()


#function to return contig_id in each line
def contig_id(string_line):
    contig_id = re.search(r"^>\w+", string_line, re.MULTILINE)
    return contig_id.group()

#function to store as string contig data (score) for each alingment
def score_data(string_line):
    score_data = re.search(r"(?<=\bScore\b\s\=\s)\d+.\d", string_line)
    return score_data.group()


#function to store as string contig data (expect == e-value) for each alingment 
def expect_value(string_line): 
    #regex \bExpect matches exactly tihs characters after \b(bounderies), + is greedy search. (?=,) is look behind match ','.
    expect_data_raw = re.search(r"(?<=\bExpect...)...+(?=,)", string_line)
    expect_data = re.search(r"(?<=\b)\d.+", str(expect_data_raw.group()))
    
    return float(expect_data.group())

#function to store as string contig data (reading frame) for each alingment
def frame_data(string_line):
    frame_data = re.search(r"(?<=\bFrame\s=\s).+", string_line)
    
    return frame_data.group()

#function store lenght of current query
def query_prot_len(string_line):
    prot_length = re.search(r"(?<=\bLength\b=\b).+", string_line)
    return prot_length.group()
