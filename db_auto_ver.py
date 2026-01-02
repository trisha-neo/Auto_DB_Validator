"""
Database Auto-Verification Tool (cyvcf2 version)
Validates ClinVar annotations in pipeline VCF against original ClinVar database

This version uses cyvcf2 for 10-50x performance improvement on large VCF files
while maintaining exact compatibility with the original output format.
98[]"""

import argparse
from cyvcf2 import VCF


def main():
    args = parse_arguments()

    vcf_data1 = {}

    print('Reading clinvar VCF file...')

    # Use cyvcf2 for fast VCF parsing
    vcf1 = VCF(args.clinvar_vcf)
    for variant in vcf1:
        # Get the database ID from the ID column
        database_id = variant.ID
        
        # Access INFO fields directly via cyvcf2
        cln_sig = variant.INFO.get('CLNSIG', '')
        cln_revstat = variant.INFO.get('CLNREVSTAT', '')
        
        # Convert None to empty string for consistency
        if cln_sig is None:
            cln_sig = ''
        if cln_revstat is None:
            cln_revstat = ''
        
        # Handle list returns (cyvcf2 may return lists for some fields)
        if isinstance(cln_sig, (list, tuple)):
            cln_sig = ','.join(str(x) for x in cln_sig)
        if isinstance(cln_revstat, (list, tuple)):
            cln_revstat = ','.join(str(x) for x in cln_revstat)
        
        vcf_data1[database_id] = [str(cln_sig), str(cln_revstat)]

    vcf_data2 = {}

    print('Reading pipeline output VCF file...')

    vcf2 = VCF(args.pipeline_vcf)
    for variant in vcf2:
        # Get custom INFO fields from pipeline annotation
        cln_sig = variant.INFO.get('clinvar_sig', '')
        cln_revstat = variant.INFO.get('clinvar_review', '')
        database_id = variant.INFO.get('clinvar_id', '')
        
        # Convert None to empty string
        if cln_sig is None:
            cln_sig = ''
        if cln_revstat is None:
            cln_revstat = ''
        if database_id is None:
            database_id = ''
        
        # Handle list returns
        if isinstance(cln_sig, (list, tuple)):
            cln_sig = ','.join(str(x) for x in cln_sig)
        if isinstance(cln_revstat, (list, tuple)):
            cln_revstat = ','.join(str(x) for x in cln_revstat)
        if isinstance(database_id, (list, tuple)):
            database_id = ','.join(str(x) for x in database_id)
        
        # Skip if database_id is missing or contains 'MISSING'
        if database_id and 'MISSING' not in str(database_id).upper():
            vcf_data2[str(database_id)] = [str(cln_sig), str(cln_revstat)]

    match_f_count = 0
    match_nf_count = 0

    print('Analyzing results...')

    with open('analysis_VCF.txt', 'w') as file_n:
        for database_id, values in vcf_data2.items():
            sig2 = values[0]
            rating2 = values[1]
            if database_id in vcf_data1:
                vals = vcf_data1[database_id]
                sig1 = vals[0]
                rating1 = vals[1]
                if sig1 == sig2 and rating1 == rating2:
                    match_f_count += 1
                else:
                    match_nf_count += 1
                    file_n.write(f'Match not found.\nDatabase id: {database_id}\nSignificance observed: {sig2}\nSignificance expected: {sig1}\nRating observed: {rating2}\nRating expected: {rating1}\n')

    with open("VCF_auto_verification_results.txt", 'w') as file_name:
        file_name.write(f'Matches found: {match_f_count}\nMatches not found: {match_nf_count}\nTotal variants: {match_nf_count + match_f_count}\n')

    print(f'Complete! Found {match_f_count} matches and {match_nf_count} mismatches.')


#   define command line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("-c",
                        "--clinvar-vcf",
                        type=str,
                        help="This VCF file contains data from the ClinVar database, which will be compared to the variants from the user's pipeline (MUST BE GZIPPED).")

    parser.add_argument("-p",
                        "--pipeline-vcf",
                        type=str,
                        help="This VCF file contains data from the user pipeline, and it will be compared to the ClinVar Database VCF file (MUST BE GZIPPED).")

    return parser.parse_args()


if __name__ == '__main__':
    main()