table_annovar.pl ~/Downloads/clinvar.vcf.gz \
  ~/projects/annovar/humandb/ \
  -buildver hg38 \
  -out clinvar_annovar_out \
  -remove \
  -protocol clinvar_20250615 \
  -operation f \
  -nastring . \
  -vcfinput \
  --thread 4 \
  --maxgenethread 4 