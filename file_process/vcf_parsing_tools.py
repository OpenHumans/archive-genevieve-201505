import json
import re

CHROM_INDEX = {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5,
               "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
               "11": 11, "12": 12, "13": 13, "14": 14, "15": 15,
               "16": 16, "17": 17, "18": 18, "19": 19, "20": 20,
               "21": 21, "22": 22, "X": 23, "Y": 24, "M": 25,
           }

CLNSIG_INDEX = {0 : "unknown",
                1 : "untested",
                2 : "non-pathogenic",
                3 : "probably non-pathogenic",
                4 : "probably pathogenic",
                5 : "pathogenic",
                6 : "affecting drug response",
                7 : "affecting histocompatibility",
                255 : "other"
               }

class ClinVarEntry():
    """Store ClinVar data relating to one accession."""
    def __init__(self, clndsdb, clndsdbid, clnacc, clndbn, clnsig):
        clndsdbs = clndsdb.split(':')
        clndsdbids = clndsdbid.split(':')
        self.dsdb = [ (clndsdbs[i], clndsdbids[i]) for i
                      in range(len(clndsdbs)) ]
        self.acc = clnacc
        self.dbn = clndbn
        self.sig = clnsig

    def __str__(self):
        return json.dumps(self.as_dict(), ensure_ascii=True)

    def as_dict(self):
        return {'dsdb': self.dsdb,
                'acc': self.acc,
                'dbn': self.dbn,
                'sig': self.sig}

class ClinVarAllele():
    """Store ClinVar data relating to one allele."""
    def __init__(self, entries, clnhgvs, clnsrcs, clnsrcids):
        self.src = [ (clnsrcs[i], clnsrcids[i]) for i
                     in range(len(clnsrcs)) ]
        self.hgvs = clnhgvs
        self.entries = entries

    def __str__(self):
        return json.dumps(self.as_dict(), ensure_ascii=True)

    def as_dict(self):
        return {'hgvs': self.hgvs,
                'src': self.src,
                'entries': [x.as_dict() for x in self.entries]}

class ClinVarData():
    """Store ClinVar data from a VCF line."""
    def __init__(self, vcf_line):
        vcf_fields = vcf_line.strip().split('\t')
        self.chrom = vcf_fields[0]
        self.start = int(vcf_fields[1])
        self.ref_allele = vcf_fields[3]
        self.alt_alleles = vcf_fields[4].split(',')
        self.info = self._parse_info(vcf_fields[7])
        self.alleles = [[self.ref_allele, 0, None]] + [[x, 0, None] for x in
                                                       self.alt_alleles]
        self._parse_allele_data()

    def __str__(self):
        return json.dumps(self.as_dict(), ensure_ascii=True)

    def as_dict(self):
        return {'chrom': self.chrom,
                'start': self.start,
                'ref_allele': self.ref_allele,
                'alt_alleles': self.alt_alleles,
                'info': self.info,
                'alleles': [[x[0], x[1], x[2].as_dict()] if x[1] else
                            x for x in self.alleles],
                }

    def _parse_info(self, info_field):
        info = dict()
        for item in info_field.split(';'):
            # Info fields may be "foo=bar" or just "foo".
            # For the first case, store key "foo" with value "bar"
            # For the second case, store key "foo" with value True.
            info_item_data = item.split('=')
            # If length is one, just store as a key with value = true.
            if len(info_item_data) == 1:
                info[info_item_data[0]] = True
            elif len(info_item_data) == 2:
                info[info_item_data[0]] = info_item_data[1]
        return info

    def _parse_allele_data(self):
        # CLNALLE describes which allele ClinVar data correspond to.
        clnalle_keys = [int(x) for x in self.info['CLNALLE'].split(',')]
        info_clnvar_tags = ['CLNDSDB', 'CLNDSDBID', 'CLNACC', 'CLNDBN',
                            'CLNSIG', 'CLNHGVS', 'CLNSRC', 'CLNSRCID']
        clnvar_data = {x:[ y.split('|') for y in self.info[x].split(',') ]
                       for x in info_clnvar_tags}
        # For each clnalle_key, create a list of ClinVarEntries
        for i in range(len(clnalle_keys)):
            if int(clnalle_keys[i]) == -1:
                continue
            entries = []
            # Each ClinVarEntry has it's own CLNDSDB, CLNDSDBID, CLNACC,
            # CLNDBN, and CLNSIG.
            for j in range(len(clnvar_data['CLNACC'][i])):
                try:
                    entry = ClinVarEntry(clndsdb=clnvar_data['CLNDSDB'][i][j],
                                     clndsdbid=clnvar_data['CLNDSDBID'][i][j],
                                     clnacc=clnvar_data['CLNACC'][i][j],
                                     clndbn=clnvar_data['CLNDBN'][i][j],
                                     clnsig=clnvar_data['CLNSIG'][i][j])
                except IndexError:
                    # Skip inconsintent entries. At least one line in the
                    # ClinVar VCF as of 2014/06 has inconsistent CLNSIG and
                    # CLNACC information (rs799916).
                    pass
                entries.append(entry)
            self.alleles[int(clnalle_keys[i])][2] = ClinVarAllele(
                entries=entries,
                clnhgvs=clnvar_data['CLNHGVS'][i][0],
                clnsrcs=clnvar_data['CLNSRC'][i],
                clnsrcids=clnvar_data['CLNSRCID'][i])


def vcf_line_pos(vcf_line):
    """
    Very lightweight processing of vcf line to enable position matching.

    Returns a dict containing:
        'chrom': index of chromosome (int), indicates sort order
        'pos': position on chromosome (int)
    """
    if not vcf_line:
        return None
    vcf_data = vcf_line.strip().split("\t")
    return_data = dict()
    return_data['chrom'] = CHROM_INDEX[vcf_data[0]]
    return_data['pos'] = int(vcf_data[1])
    return return_data


def genome_vcf_line_alleles(vcf_line):
    if not vcf_line:
        return None
    vcf_data = vcf_line.strip().split("\t")
    possible_alleles = [vcf_data[3]] + vcf_data[4].split(',')
    format_tags = vcf_data[8].split(":")
    genome_values = vcf_data[9].split(":")
    genome_data = { format_tags[i]:genome_values[i] for i in
                    range(len(genome_values)) }
    alleles = [possible_alleles[int(x)] for x in
               re.split('[|/]', genome_data['GT'])
               if x != '.']
    return alleles


def match_to_clinvar(genome_file, clin_file):

    clin_curr_line = clin_file.next()
    genome_curr_line = genome_file.next()

    # Ignores all the lines that start with a hashtag
    while clin_curr_line.startswith("#"):
        clin_curr_line = clin_file.next()
    while genome_curr_line.startswith("#"):
        genome_curr_line = genome_file.next()

    # Advance through both files simultaneously to find matches
    while clin_curr_line or genome_curr_line:

        clin_curr_pos = vcf_line_pos(clin_curr_line)
        genome_curr_pos = vcf_line_pos(genome_curr_line)
        if clin_curr_pos['chrom'] > genome_curr_pos['chrom']:
            # If the ClinVar chromosome is greater, advance the genome's file
            try:
                genome_curr_line = genome_file.next()
            except StopIteration:
                break

        elif clin_curr_pos['chrom'] < genome_curr_pos['chrom']:
            # If the genome's chromosome is greater, advance the ClinVar file
            try:
                clin_curr_line = clin_file.next()
            except StopIteration:
                break

        if clin_curr_pos['chrom'] == genome_curr_pos['chrom']:

            if clin_curr_pos['pos'] > genome_curr_pos['pos']:
                # If the ClinVar position is greater, advance the genome's file
                try:
                    genome_curr_line = genome_file.next()
                except StopIteration:
                    break
            elif clin_curr_pos['pos'] < genome_curr_pos['pos']:
                # If the genome's position is greater, advance the ClinVar file
                try:
                    clin_curr_line = clin_file.next()
                except StopIteration:
                    break
            # Start positions match, look for allele matching.
            else:
                # Figure out what alleles the genome has
                genome_alleles = genome_vcf_line_alleles(genome_curr_line)

                # Because ClinVar records can match ref allele, include
                # checks for both ref and alt alleles in both records.
                clinvar_data = ClinVarData(clin_curr_line)

                for genome_allele in genome_alleles:
                    # Using index so we can call up relevant ClinVarEntries
                    for i in range(len(clinvar_data.alleles)):
                        is_same_len_change = (
                            len(genome_allele) - len(genome_alleles[0]) ==
                             len(clinvar_data.alleles[i][0]) -
                             len(clinvar_data.alleles[0][0]))
                        is_match = (is_same_len_change and
                            (genome_allele.startswith(
                                clinvar_data.alleles[i][0])) or
                            (clinvar_data.alleles[i][0].startswith(
                                genome_allele)))
                        if is_match:
                            clinvar_data.alleles[i][1] += 1

                for i in range(len(clinvar_data.alleles)):
                    zygosity = "???"
                    if (clinvar_data.alleles[i][1] and
                        clinvar_data.alleles[i][2]):
                        if len(genome_alleles) == 2:
                            if clinvar_data.alleles[i][1] == 1:
                                zygosity = "Het"
                            elif clinvar_data.alleles[i][1] == 2:
                                zygosity = "Hom"
                        elif len(genome_alleles) == 1:
                            if clinvar_data.alleles[i][1] == 1:
                                # Hemizygous, e.g. X chrom when XY.
                                zygosity = "Hem"

                        clnsig = [int(clinvar_data.alleles[i][2].entries[x].sig) \
                                  for x in range(len(clinvar_data.alleles[i][2].entries))]

                        acc = [clinvar_data.alleles[i][2].entries[n].acc \
                               for n in range(len(clnsig)) \
                               if clnsig[n] == 4 or clnsig[n] == 5]
                        if acc:
                            # acc is a list of accession numbers for this variant
                            yield (genome_curr_pos['chrom'],
                                   genome_curr_pos['pos'],
                                   zygosity,
                                   acc)
                # Known bug: A couple ClinVar entries are swapped
                # relative to the genome: what the genome calls
                # reference, ClinVar calls alternate (and visa versa).
                # Currently these rare situations result in a non-match.
                try:
                    genome_curr_line = genome_file.next()
                    clin_curr_line = clin_file.next()
                except StopIteration:
                    break

