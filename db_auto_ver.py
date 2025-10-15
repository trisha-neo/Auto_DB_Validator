import gzip
import argparse
from sys import argv

def main():
    args = parse_arguments()

    # dictionary
    clinvar_data = {}

    print('Reading ClinVar VCF file...')

    # opens compressed vcf file
    with gzip.open(args.clinvar_vcf, 'r') as file_n:    
        for bline in file_n:
            # decoding byte code into string (type UTF-8)
            line = bline.decode('UTF-8')
            if not line.startswith('#'):
                # looks for new line at edges and strips out
                # splits string at tabs
                columns = line.strip('\n').split('\t')
                #look for eigth column in vcf file
                col8 = columns[7]
                info = col8.split(';')

                cln_sig = ''
                cln_revstat = ''

                for item in info:
                    if 'CLNSIG=' in item: # This is picking up items with CLNSIGSCV fields as well otherwise, if not specified with =
                        cln_sig = item.split('=')[1]
                    if 'CLNREVSTAT=' in item:
                        cln_revstat = item.split('=')[1]
                    if 'ALLELEID=' in item:
                        allele_id = item.split('=')[1]

                # in dictionary it is assigning the alleleid to the other two info field values
                clinvar_data[allele_id] = [cln_sig, cln_revstat]

    pipeline_vcf_data = {}

    print('Reading pipeline output VCF file...')

    with gzip.open(args.pipeline_vcf, 'r') as file_n:
        for bline in file_n:
            line =  bline.decode('UTF-8')
            if not line.startswith('#'):
                columns = line.strip('\n').split('\t')
                col8 = columns[7]
                info = col8.split(';')
                cln_sig = ''
                cln_revstat = ''
                database_id = ''

                for item in info:
                    if 'CLNSIG' in item and not '.' in item:
                        cln_sig = item.split('=')[1]
                    if 'CLNREVSTAT' in item and not '.' in item:
                        cln_revstat = item.split('=')[1]
                    if 'CLNALLELEID' in item and not '.' in item:
                        database_id = item.split('=')[1]

                pipeline_vcf_data[database_id] = [cln_sig, cln_revstat]

    match_f_count = 0
    match_nf_count = 0

    print("Analyzing results...")

    with open('analysis_VCF.txt', 'w') as file_n:
        for database_id, values in pipeline_vcf_data.items():
            sig2 = values[0]
            rating2 = values[1]
            if database_id in clinvar_data:
                vals = clinvar_data[database_id]
                sig1 = vals[0]
                rating1 = vals[1]
                if sig1 == sig2 and rating1 == rating2:
                    match_f_count += 1
                else:
                    match_nf_count += 1
                    file_n.write(f'Match not found.\nDatabase id: {database_id}\nSignificance observed: {sig2}\nSignificance expected: {sig1}\nRating observed: {rating2}\nRating expected: {rating1}\n')

    with open("VCF_auto_verification_results.txt", 'w') as file_name:
        file_name.write(f'Matches found: {match_f_count}\nMatches not found: {match_nf_count}\nTotal variants: {match_nf_count + match_f_count}\n')

#   define command line arguments
def parse_arguments():
   parser = argparse.ArgumentParser(description = __doc__,
                                    formatter_class = argparse.RawTextHelpFormatter)
   
   parser.add_argument("-c",
                       "--clinvar-vcf",
                       type = str,
                       help = "This VCF file contains data from the ClinVar database, which will be compared to the variants from the user's pipeline (MUST BE GZIPPED).")
   
   parser.add_argument("-p",
                       "--pipeline-vcf",
                       type = str,
                       help = "This VCF file contains data from the user pipeline, and it will be compared to the ClinVar Database VCF file (MUST BE GZIPPED).")
   
   return parser.parse_args()

if __name__ == '__main__':
    main()