#!/usr/bin/python
# Filename: cgivar_to_gff.py
"""Conversion of Complete Genomics, Inc. (CGI) var files to VCF files.

To see command line usage, run with "-h" or "--help".
"""
import bz2
import gzip
import re
import sys

from optparse import OptionParser

from get_reference import get_reference_allele


def auto_zip_open(filepath, mode):
    if filepath.endswith('.gz'):
        outfile = gzip.open(filepath, mode)
    elif filepath.endswith('.bz2'):
        outfile = bz2.BZ2File(filepath, mode)
    else:
        outfile = open(filepath, mode)
    return outfile


def process_full_position(data, header):
    """Return genetic data when all alleles called on same line

    Returns five items in this order:
        (string) chromosome
        (string) start position (1-based)
        (array of strings) matching dbSNP entries
        (string) reference allele sequence
        (array of strings) variant allele sequences
    """

    feature_type = data[header['varType']]
    # Skip unmatchable, uncovered, or pseudoautosomal-in-X
    if (feature_type == 'no-ref' or feature_type.startswith('no-call') or
            feature_type.startswith('PAR-called-in-X')):
        return None
    # TODO: Don't skip REF, call using gVCF syntax.
    if feature_type == 'ref':
        return None

    # Skip low quality
    if ('varQuality' in header and
            data[header['varQuality']].startswith('VQLOW')):
        return None

    chrom = data[header['chromosome']]
    # One-based start to match VCF coordinates
    start = str(int(data[header['begin']]) + 1)
    ref_allele = data[header['reference']]
    alleles = [data[header['alleleSeq']]]
    dbsnp_data = []
    dbsnp_data = data[header['xRef']].split(';')
    return [(chrom, start, dbsnp_data, ref_allele, alleles)]


def process_allele(allele_data, dbsnp_data, header):
    """Combine data from multiple lines refering to a single allele.

    Returns three items in this order:
        (string) concatenated variant sequence
        (string) concatenated reference sequence
        (string) start position (1-based)
    """
    # One-based start to match VCF coordinates
    start = str(int(allele_data[0][header['begin']]) + 1)
    var_allele = ''
    ref_allele = ''
    for data in allele_data:
        # We reject allele data if any subset of the data has a no-call.
        if (data[header['varType']] == 'no-call' or
            ('varQuality' in header and
                data[header['varQuality']].startswith('VQLOW'))):
            var_allele = None
            ref_allele = None
            break
        var_allele = var_allele + data[header['alleleSeq']]
        ref_allele = ref_allele + data[header['reference']]
        if data[header['xRef']]:
            for dbsnp_item in data[header['xRef']].split(';'):
                dbsnp_data.append(dbsnp_item.split(':')[1])
    return var_allele, ref_allele, start


def get_split_pos_lines(data, cgi_input, header):
    """Advance across split alleles and return data from each.

    CGI var file reports alleles separately for heterozygous sites:
    all variant or reference information is called for the first allele,
    then for the second. This function moves forward in the file to
    get lines for each (and ends up with one remaineder line as well).
    """
    s1_data = [data]
    s2_data = []
    next_data = cgi_input.next().rstrip('\n').split("\t")
    while next_data[header['allele']] == "1":
        s1_data.append(next_data)
        next_data = cgi_input.next().rstrip('\n').split("\t")
    while next_data[header['allele']] == "2":
        s2_data.append(next_data)
        next_data = cgi_input.next().rstrip('\n').split("\t")
    return s1_data, s2_data, next_data


def process_split_position(data, cgi_input, header):
    """Process CGI var where alleles are reported separately."""
    assert data[2] == "1"
    chrom = data[header['chromosome']]

    # Get all lines for each allele. Note that this means we'll end up with
    # data from one line ahead stored in 'next_data'; it will be handled at
    # the end.
    s1_data, s2_data, next_data = get_split_pos_lines(data, cgi_input, header)

    # Process all the lines to get concatenated sequences and other data.
    dbsnp_data = []
    a1_seq, ref_seq, start = process_allele(s1_data, dbsnp_data, header)
    a2_seq, r2_seq, a2_start = process_allele(s2_data, dbsnp_data, header)
    # clean dbsnp data
    dbsnp_data = [x for x in dbsnp_data if x]
    if (a1_seq or ref_seq) and (a2_seq or r2_seq):
        # Check that reference sequence and positions match.
        assert ref_seq == r2_seq
        assert start == a2_start
        yield (chrom, start, dbsnp_data, ref_seq, [a1_seq, a2_seq])

    # Handle the remaining line (may recursively call this function if it's
    # the start of a new region with separated allele calls).
    if next_data[2] == "all" or next_data[1] == "1":
        out = process_full_position(next_data, header)
    else:
        out = process_split_position(next_data, cgi_input, header)
    if out:
        for entry in out:
            yield entry


def vcf_line(input_data, twobit_ref):
    chrom, start, dbsnp_data, ref_allele, genome_alleles = input_data
    # VCF does not allow zero-length sequences. If we have this situation,
    # move the start backwards by one position, get that reference base,
    # and prepend this base to all sequences.
    if len(ref_allele) == 0 or 0 in [len(v) for v in genome_alleles]:
        start = str(int(start) - 1)
        prepend = get_reference_allele(
            chrom,
            int(start) - 1,
            twobit_ref
        )
        ref_allele = prepend + ref_allele
        genome_alleles = [prepend + v for v in genome_alleles]
    alt_alleles = []
    for allele in genome_alleles:
        if allele not in [ref_allele] + alt_alleles:
            alt_alleles.append(allele)
    alleles = [ref_allele] + alt_alleles
    genotype = '/'.join([str(alleles.index(x)) for x in genome_alleles])
    dbsnp_cleaned = []
    for dbsnp in dbsnp_data:
        if dbsnp not in dbsnp_cleaned:
            dbsnp_cleaned.append(dbsnp)
    if dbsnp_cleaned:
        id_field = ';'.join(dbsnp_cleaned)
    else:
        id_field = '.'
    return '\t'.join([chrom, start, id_field, ref_allele,
                      ','.join(alt_alleles), '.', '.', '.',
                      'GT', genotype])


def process_next_position(data, cgi_data, header, twobit_ref):
    if data[2] == "all" or data[1] == "1":
        # The output from process_full_position is a str.
        out = process_full_position(data, header)
    else:
        assert data[2] == "1"
        # The output from process_split_position is a str generator;
        # it may end up calling itself recursively.
        out = process_split_position(data, cgi_data, header)
    if out:
        return [vcf_line(l, twobit_ref) for l in out]


def convert(cgi_data, twobit_ref):
    """Generator that converts CGI var data to VCF-formated strings"""

    # Set up CGI input. Default is to assume a str generator.
    if isinstance(cgi_data, basestring):
        cgi_data = auto_zip_open(cgi_data, 'rb')

    for line in cgi_data:
        if re.search(r'^\W*$', line) or re.search("^#", line):
            continue
        if line.startswith('>'):
            header_data = line.lstrip('>').rstrip('\n').split('\t')
            header = {header_data[i]: i for i in range(len(header_data))}
            continue

        data = line.rstrip('\n').split("\t")

        out = process_next_position(data, cgi_data, header, twobit_ref)
        if out:
            for line in out:
                yield line


def convert_to_file(cgi_input, output_file, twobit_ref):
    """Convert a CGI var file and output VCF-formatted data to file"""

    if isinstance(output_file, basestring):
        output_file = auto_zip_open(output_file, 'wb')

    conversion = convert(cgi_input, twobit_ref)  # set up generator
    for line in conversion:
        output_file.write(line + "\n")
    output_file.close()


def main():
    # Parse options
    usage = "\n%prog -i inputfile [-o outputfile]\n" \
            + "%prog [-o outputfile] < inputfile"
    parser = OptionParser(usage=usage)
    parser.add_option("-i", "--input", dest="inputfile",
                      help="read CGI data from INFILE (uncompressed, .gz," +
                      " or .bz2)", metavar="INFILE")
    parser.add_option("-o", "--output", dest="outputfile",
                      help="write report to OUTFILE (uncompressed, " +
                      "*.gz, or *.bz2)", metavar="OUTFILE")
    parser.add_option("-r", "--ref2bit", dest="twobitref",
                      help="2bit reference genome file",
                      metavar="TWOBITREF")
    options, _ = parser.parse_args()
    # Handle input
    if sys.stdin.isatty():  # false if data is piped in
        var_input = options.inputfile
    else:
        var_input = sys.stdin
    # Handle output
    if options.outputfile:
        convert_to_file(var_input, options.outputfile, options.twobitref)
    else:
        for line in convert(var_input, options.twobitref):
            print line

if __name__ == "__main__":
    main()
