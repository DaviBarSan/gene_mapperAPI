#this file must be inside TBLASTn-resulsts directory to locate 
import re
import xlsxwriter
from scrappingTools import scrappingFunctions

#create a workbook and a worksheet ---> ('newfilename.xlsx')
workbook = xlsxwriter.Workbook('PSY-phytoene-synthase-Chlorophytas_new_test.xlsx')
worksheet = workbook.add_worksheet()

parameters = ('Query Name', 'Query Acss Number', 'Biological Source','Contig Acss Number', 'Score (Bits)', 'Expect', 'Frame', 'Start', 'Stop','Protein Coverage - Start', 'Protein Coverage - Stop','Length')

row = 0
col = 0

#temporary list that stores position start and stop references to each protein region matched
tmp_query_coverage = []
#temporary list that stores position start and stop references to each frame reading
position_numbers_list = []
#temporary list that store "pieces" of species name
specie_puzzle = []
#lista para guardar os dados do frame
#uma vez que o position numbers usa os dados do penultimo match com ''frame''
frame_list = []
#flag to protein lenght. Might exist to do not mismatch the T. striata sequence alingned, instead of query length
protein_len_flag = False 

#creating .xlsx headers
for item in parameters:
    worksheet.write(row, col, item)
    col +=1
row +=1
#!!!!!!UPDATE HERE!!!! OS.PWD
#set TBLASTN alignment result file path 
filename = "/home/barrsant/Desktop/learning/Portifolio/tblastn_mapper_API/gene_mapping_t._striata/blast-PSY-phytoene-synthase-Chlorophytas.txt"
fi = open(filename, "r")

contents = fi.readlines()   

#iterating over blastresults data for each line
for line in contents:
    #caso encontre query data, escrevê-lo em  worksheet
    if re.search(r"Query=...+", line):
        #data_id_row += 1
        #atualizar query_data para preenchimento da célula (novo query)
        query_numb = scrappingFunctions.query_acess_number(line)
        worksheet.write(row, 1, query_numb)
        #regexing enzyme name and specie name in list[1]
        enzyme_name = scrappingFunctions.query_name(line)
        worksheet.write(row, 0, enzyme_name)
        protein_len_flag = True
    
    if (re.search(r"(?<=\bLength\b=\b).+", line) and protein_len_flag == True):
        curr_prot_len = scrappingFunctions.query_prot_len(line)
        worksheet.write(row, 11, curr_prot_len)
        protein_len_flag = False

    
    #regexing species name in multiple situations
    #Most case will run, but some can raise exception because breaklines;
        #e.g ([Coccomyxa subellipsoidea
        #C-169]; [Haematococcus
        #lacustris]) it generates attribute error
    #\]$ matches all specie name situations
    if re.search(r"\[...+", line):   
        try:
            data_specie_name = re.search(r"(?<=\[)...+(?=\])", line)
            specie_name = data_specie_name.group()
            worksheet.write(row, 2, specie_name)
            continue
        except AttributeError:
            #matching all the specie name untill the breake line
            # appending puzzle one to specie_puzzle    
            puzzle_one = re.search(r"(?<=\[)...+", line)
            specie_puzzle.append(puzzle_one.group())
            continue
    #para completar o puzzle, é preciso dar match com uma sentença que não tenha o '['
    #mas tenha ]
    if re.search(r"\]$", line) != None and re.search(r"\[", line) == None:
        #match com toda a palavra até ']'
        puzzle_two = re.search(r"...+(?=\])", line)
        specie_puzzle.append(puzzle_two.group())
        specie_name = " ".join(specie_puzzle)
        worksheet.write(row, 2, specie_name)
        specie_puzzle.clear()
    #caso encontre contig id em line
    elif re.search(r"^>\w+", line): 
        contig_str_id = scrappingFunctions.contig_id(line)
        worksheet.write_string(row, 3, contig_str_id)
    #a cada iteração do 'for', preencher células abaixo do primeiro match do id,
    #enquanto este id não for atualizado

    
    #caso encontre score data em line
    if re.search(r"\bScore\b\s\=\s\d+.\d", line):
        score_str_data = scrappingFunctions.score_data(line)
        worksheet.write_string(row, 4, score_str_data)
    #caso encontre expect value data
    if re.search(r"(?<=\bExpect...)...+(?=,)", line):
        e_value_data = scrappingFunctions.expect_value(line)
        worksheet.write_number(row, 5, e_value_data)
    #caso encontre frame value
    if re.search(r"\bFrame\s=\s.+", line):
        frame_str_data = scrappingFunctions.frame_data(line)
        worksheet.write_string(row, 6, frame_str_data)
       
        #uma vez que o position_number é preenchido segundo os dados do match anterior,
        # é necessário guardar o valor do last frame, para determinar o start e stop
        frame_list.append(int(frame_str_data))
        #uma vez que Frame é usado como flag para preenchimento das frames anteriores
        #se a lista de ref. não estiver vazia (evita error do primeiro match com ''frame'' encontrado)
        #a lista position numbers é preenchida em iterações após o match com o primeiro ''frame'', uma vez que os dados 
        # de start e stop referentes àquele frame só são obtidos em iterações seguintes ao match com o frame;
        # (row-1) pois o worksheet é preenchido em retrocesso. O match atual preenche as coordenadas referente ao match anterior   
        if position_numbers_list != []:
            start_position_prot_coverage = min(tmp_query_coverage)
            stop_position_prot_coverage = max(tmp_query_coverage)
            worksheet.write(row-1, 9, start_position_prot_coverage)
            worksheet.write(row-1, 10, stop_position_prot_coverage)
            if  frame_list[-2]> 0:
                start_position = min(position_numbers_list)
                stop_position = max(position_numbers_list)
                worksheet.write(row-1, 7, start_position)
                worksheet.write(row-1, 8, stop_position)
            else:
                start_position = max(position_numbers_list)
                stop_position = min(position_numbers_list)
                worksheet.write(row-1, 7, start_position)
                worksheet.write(row-1, 8, stop_position)
        
        #é necessario um backup para preencher os dados referentes ao ultimo frame do documento FASTA
        backup_last_position_numbers_list = position_numbers_list
        position_numbers_list.clear()
        backup_last_query_position_numbers_list = tmp_query_coverage
        tmp_query_coverage.clear()
        
        #preenchendo todas as células da planilha, com as referências correspondentes ao respectivo frame, até estas serem atualizadas
        #query_name (nome da enzima); query_accss_number; specie; contig_id;
        worksheet.write(row, 0, enzyme_name)
        worksheet.write(row, 1, query_numb)
        worksheet.write(row, 2, specie_name)
        worksheet.write_string(row, 3, contig_str_id)
        worksheet.write(row, 11, curr_prot_len)

        #testing jumping lines inside last function called (provisório ser em frame, final version sera em 'stop')
        row +=1    
    #a cada match com um position reference, estes numeros serão adicionados a position_number_list. Esta lista 
    #vai crescer até line ser uma linha referente à frame, score, e-value... Então, será adicionado na linha do excel
    #min e max dessa linha referente ao start e stop, consoante ao frame de leitura
    if re.search(r"\bSbjc...+", line):
        position_data_list_str = re.findall(r"\d+\b", line)
        for i in position_data_list_str:
            position_numbers_list.append(int(i))

    if re.search(r"\bQuery\s...+", line):
        tmp_query_coverage_str = re.findall(r"\d+\b", line)
        for i in tmp_query_coverage_str:
            tmp_query_coverage.append(int(i))


    if re.search(r"\bMatrix:\s", line):##flag to end the loop and close the file 
        start_position_prot_coverage = min(backup_last_query_position_numbers_list)
        stop_position_prot_coverage = max(backup_last_query_position_numbers_list)
        worksheet.write(row-1, 9, start_position_prot_coverage)
        worksheet.write(row-1, 10, stop_position_prot_coverage)
        #dados start stop do ultimo frame
        if frame_list[-1] > 0:
            start_position = min(backup_last_position_numbers_list)
            stop_position = max(backup_last_position_numbers_list)
            worksheet.write(row-1, 7, start_position)
            worksheet.write(row-1, 8, stop_position)
        else:
            start_position = max(backup_last_position_numbers_list)
            stop_position = min(backup_last_position_numbers_list)
            worksheet.write(row-1, 7, start_position)
            worksheet.write(row-1, 8, stop_position)
        

        fi.close()
        workbook.close()
