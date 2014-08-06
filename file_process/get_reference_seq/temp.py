from twobit import TwoBitFile

# Download 2bit genome with:
# wget http://hgdownload.soe.ucsc.edu/goldenPath/hg19/bigZips/hg19.2bit 
HG19_2BIT_FILEPATH = 'hg19.2bit'

def main():
    twobit_file = TwoBitFile(HG19_2BIT_FILEPATH)
    chrom = 'chrY'
    start = 10000
    end = start + 50
    seq = twobit_file[chrom][start:end]
    print seq

if __name__ == "__main__":
    main()
