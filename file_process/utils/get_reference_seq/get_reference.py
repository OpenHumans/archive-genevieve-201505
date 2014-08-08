from twobit import TwoBitFile

# Download 2bit genome with:
# wget http://hgdownload.soe.ucsc.edu/goldenPath/hg19/bigZips/hg19.2bit 
HG19_2BIT_FILEPATH = 'hg19.2bit'

def get_reference_allele(chrom, start):
    twobit_file = TwoBitFile(HG19_2BIT_FILEPATH)
    end = start + 1
    refallele = twobit_file[chrom][start:end]
    print refallele
    return refallele
