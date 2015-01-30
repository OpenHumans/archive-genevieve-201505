"""Tools for parsing and matching VCF files"""
import json
import re
import sys

CHROM_INDEX = {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5,
               "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
               "11": 11, "12": 12, "13": 13, "14": 14, "15": 15,
               "16": 16, "17": 17, "18": 18, "19": 19, "20": 20,
               "21": 21, "22": 22, "X": 23, "Y": 24, "M": 25, "MT": 25,
               "chr1": 1, "chr2": 2, "chr3": 3, "chr4": 4, "chr5": 5,
               "chr6": 6, "chr7": 7, "chr8": 8, "chr9": 9, "chr10": 10,
               "chr11": 11, "chr12": 12, "chr13": 13, "chr14": 14, "chr15": 15,
               "chr16": 16, "chr17": 17, "chr18": 18, "chr19": 19, "chr20": 20,
               "chr21": 21, "chr22": 22, "chrX": 23, "chrY": 24, "chrM": 25,
               }

CLNSIG_INDEX = {0: "unknown",
                1: "untested",
                2: "non-pathogenic",
                3: "probably non-pathogenic",
                4: "probably pathogenic",
                5: "pathogenic",
                6: "affecting drug response",
                7: "affecting histocompatibility",
                255: "other"}


class ClinVarRecord(object):
    """Store ClinVar data relating to one record."""
    def __init__(self, clndsdb, clndsdbid, clnacc, clndbn, clnsig):
        clndsdbs = clndsdb.split(':')
        clndsdbids = clndsdbid.split(':')
        self.dsdb = [(clndsdbs[i], clndsdbids[i]) for i
                     in range(len(clndsdbs))]
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


class Allele(object):
    """Store data relating to one allele."""
    def __init__(self, *args, **kwargs):
        """
        Initialize Allele object

        Required arguments:
        sequence:  Short string of DNA letters (ACGT) for the allele.
                   May be empty (to represent a deletion).

        Optional arguments:
        frequency: a string/float between 0 and 1, or string saying "NOT1000G"
        """
        sequence = kwargs['sequence']
        if 'frequency' in kwargs:
            frequency = kwargs['frequency']
        else:
            frequency = None

        if not (re.match('^[ACGTN]*$', sequence) or
                re.match('^<.*>$', sequence)):
            raise ValueError("Allele sequence isn't a standard DNA sequence")
        self.sequence = sequence
        if frequency:
            try:
                if (float(frequency) < 0.0 or
                        float(frequency) > 1.0):
                    raise ValueError('Allele frequency not between 0 and 1')
            except ValueError:
                if not frequency == 'NOT1000G':
                    raise ValueError('Allele frequency must be a number ' +
                                     'between 0 and 1, or the string ' +
                                     '"NOT1000G".')
            self.frequency = frequency

    def __str__(self):
        """Print Allele object as dict object data."""
        return json.dumps(self.as_dict(), ensure_ascii=True)

    def as_dict(self):
        """Return Allele data as dict object."""
        self_as_dict = dict()
        self_as_dict['sequence'] = self.sequence
        if hasattr(self, 'frequency'):
            self_as_dict['frequency'] = self.frequency
        return self_as_dict


class ClinVarAllele(Allele):
    """Store ClinVar data relating to one allele."""
    def __init__(self, *args, **kwargs):
        """
        Initialize ClinVarAllele object

        A ClinVarAllele is an allele for a genomic position that has data
        from ClinVar associated with it. ClinVar data in the VCF appears to
        exist at two levels: the allele, and records. A ClinVar "record"
        describes a reported effect, and any allele may have multiple
        records associated with it. An allele can also have other data
        returned by ClinVar (in the ClinVar VCF this appears to be separate
        to the Records).

        Required arguments:
        sequence:  String of DNA letters (A, C, G, or T) for the allele;
                   may be empty (to represent a deletion).
        records:   list of ClinVarRecord objects associated with this allele
        hgvs:      HGVS nomenclature for this allele
        clnsrcs:   list of ClinVar sources
        clnsrcids: list of IDs for the ClinVar sources

        Optional arguments:
        frequency: a float between 0 and 1, or string saying "NOT1000G"
        """
        clnsrcs, clnsrcids, clnhgvs, records = [kwargs[x] for x in
                                                ['clnsrcs', 'clnsrcids',
                                                 'clnhgvs', 'records']]
        self.src = [(clnsrcs[i], clnsrcids[i]) for i in range(len(clnsrcs))]
        self.hgvs = clnhgvs
        self.records = records
        super(ClinVarAllele, self).__init__(*args, **kwargs)

    def as_dict(self, *args, **kwargs):
        """Return ClinVarAllele data as dict object."""
        self_as_dict = super.ClinVarAllele.as_dict(*args, **kwargs)
        self_as_dict['hgvs'] = self.hgvs
        self_as_dict['src'] = self.src
        self_as_dict['records'] = [x.as_dict() for x in self.records]
        return self_as_dict


class VCFLine(object):
    """Process data from a VCF line."""

    def __init__(self, *args, **kwargs):
        """Store data from a VCF line."""
        vcf_line = kwargs['vcf_line']
        skip_info = ('skip_info' in kwargs and kwargs['skip_info'])

        vcf_fields = vcf_line.strip().split('\t')
        self.chrom = vcf_fields[0]
        self.start = int(vcf_fields[1])
        self.ref_allele = vcf_fields[3]
        if vcf_fields[4] == '.':
            self.alt_alleles = []
        else:
            self.alt_alleles = vcf_fields[4].split(',')
        if not skip_info:
            self.info = self._parse_info(vcf_fields[7])
        self.alleles = self._parse_allele_data()

    def _parse_allele_data(self):
        """Create list of Alleles from VCF line data"""
        return [Allele(sequence=x) for x in
                [self.ref_allele] + self.alt_alleles]

    def _parse_info(self, info_field):
        """Parse the VCF info field"""
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

    def __str__(self):
        """String representation of parsed VCF data"""
        return json.dumps(self.as_dict(), ensure_ascii=True)

    def as_dict(self):
        """Dict representation of parsed VCF data"""
        self_as_dict = {'chrom': self.chrom,
                        'start': self.start,
                        'ref_allele': self.ref_allele,
                        'alt_alleles': self.alt_alleles,
                        'alleles': [x.as_dict() for x in self.alleles]}
        try:
            self_as_dict['info'] = self.info
        except AttributeError:
            pass
        return self_as_dict

    @staticmethod
    def get_pos(vcf_line):
        """
        Very lightweight parsing of a vcf line to get position.

        Returns a dict containing:
        'chrom': index of chromosome (int), indicates sort order
        'pos': position on chromosome (int)
        """
        if not vcf_line:
            return None
        vcf_data = vcf_line.strip().split("\t")
        return_data = dict()
        return_data['chrom'] = vcf_data[0]
        return_data['chrom_idx'] = CHROM_INDEX[vcf_data[0]]
        return_data['pos'] = int(vcf_data[1])
        return return_data


class GenomeVCFLine(VCFLine):
    """Store Genome data from a VCF line."""
    def __init__(self, *args, **kwargs):
        super(GenomeVCFLine, self).__init__(self, *args, **kwargs)
        vcf_line = kwargs['vcf_line']
        vcf_fields = vcf_line.strip().split('\t')
        self.genotype_allele_indexes = self._parse_genotype(vcf_fields)

    def _parse_genotype(self, vcf_fields):
        """Parse genotype from VCF line data"""
        format_col = vcf_fields[8].split(':')
        genome_data = vcf_fields[9].split(':')
        try:
            gt_idx = format_col.index('GT')
        except ValueError:
            return []
        return [int(x) for x in re.split(r'[\|/]', genome_data[gt_idx]) if
                x != '.']


class ClinVarVCFLine(VCFLine):
    """Store ClinVar data from a VCF line."""

    def __init__(self, *args, **kwargs):
        """Initialize ClinVarVCFLine with VCF line"""
        kwargs['skip_info'] = False
        super(ClinVarVCFLine, self).__init__(self, *args, **kwargs)

    def as_dict(self):
        """Dict representation of parsed ClinVar VCF line"""
        return {'chrom': self.chrom,
                'start': self.start,
                'ref_allele': self.ref_allele,
                'alt_alleles': self.alt_alleles,
                'info': self.info,
                'alleles': [[x[0], x[1], x[2].as_dict()] if x[1] else
                            x for x in self.alleles]}

    def _parse_frequencies(self):
        """Parse frequency data in ClinVar VCF"""
        given_freqs = self.info['CAF'].rstrip(']').lstrip('[').split(',')
        parsed_freqs = ['0' if x == '.' else x for x in given_freqs]
        return parsed_freqs

    def _parse_clinvar_allele(self, *args, **kwargs):
        """Parse ClinVar records for each allele"""
        cln_data, cln_idx, allele_idx = [kwargs[x] for x in
                                         ['cln_data', 'cln_idx', 'allele_idx']]
        if 'frequency' in kwargs:
            frequency = kwargs['frequency']
        else:
            frequency = None

        if allele_idx == 0:
            sequence = self.ref_allele
        else:
            sequence = self.alt_alleles[allele_idx - 1]
        clnsrcs = cln_data['CLNSRC'][cln_idx]
        clnsrcids = cln_data['CLNSRCID'][cln_idx]
        clnhgvs = cln_data['CLNHGVS'][cln_idx][0]

        # Process all the ClinVar records for this allele.
        records = []
        for record_idx in range(len(cln_data['CLNACC'])):
            try:
                record = ClinVarRecord(
                    clndsdb=cln_data['CLNDSDB'][cln_idx][record_idx],
                    clndsdbid=cln_data['CLNDSDBID'][cln_idx][record_idx],
                    clnacc=cln_data['CLNACC'][cln_idx][record_idx],
                    clndbn=cln_data['CLNDBN'][cln_idx][record_idx],
                    clnsig=cln_data['CLNSIG'][cln_idx][record_idx])
            except IndexError:
                # Skip inconsintent entries. At least one line in the
                # ClinVar VCF as of 2014/06 has inconsistent CLNSIG and
                # CLNACC information (rs799916).
                return self._parse_allele(*args, **kwargs)
            records.append(record)
        if frequency:
            return ClinVarAllele(sequence=sequence,
                                 clnhgvs=clnhgvs,
                                 clnsrcs=clnsrcs,
                                 clnsrcids=clnsrcids,
                                 records=records,
                                 frequency=frequency)
        else:
            return ClinVarAllele(sequence=sequence,
                                 clnhgvs=clnhgvs,
                                 clnsrcs=clnsrcs,
                                 clnsrcids=clnsrcids,
                                 records=records)

    def _parse_allele(self, *args, **kwargs):
        """Create an Allele, with optional frequency data."""
        allele_idx = kwargs['allele_idx']
        try:
            frequency = kwargs['frequency']
        except KeyError:
            frequency = None

        if allele_idx == 0:
            sequence = self.ref_allele
        else:
            sequence = self.alt_alleles[allele_idx - 1]
        if frequency:
            return Allele(sequence=sequence,
                          frequency=frequency)
        else:
            return Allele(sequence=sequence)

    def _parse_allele_data(self):
        """Parse alleles, overrides parent method."""
        # Get allele frequencies if they exist.
        frequencies = []
        if 'CAF' in self.info:
            frequencies = self._parse_frequencies()

        # CLNALLE describes which allele ClinVar data correspond to.
        clnalle_keys = [int(x) for x in self.info['CLNALLE'].split(',')]
        info_clnvar_tags = ['CLNDSDB', 'CLNDSDBID', 'CLNACC', 'CLNDBN',
                            'CLNSIG', 'CLNHGVS', 'CLNSRC', 'CLNSRCID']
        # Clinvar data is split first by comma, then by pipe.
        cln_data = {x: [y.split('|') for y in self.info[x].split(',')]
                    for x in info_clnvar_tags if x}

        # Iterate over all alleles, if index is in clnallele_keys then
        # create a ClinVarAllele, otherwise create an Allele.
        alleles = []
        for i in range(len(self.alt_alleles) + 1):
            if i in clnalle_keys and frequencies:
                cln_idx = clnalle_keys.index(i)
                allele = self._parse_clinvar_allele(allele_idx=i,
                                                    cln_idx=cln_idx,
                                                    cln_data=cln_data,
                                                    frequency=frequencies[i])
            elif i in clnalle_keys:
                cln_idx = clnalle_keys.index(i)
                allele = self._parse_clinvar_allele(allele_idx=i,
                                                    cln_idx=cln_idx,
                                                    cln_data=cln_data)
            elif frequencies:
                allele = self._parse_allele(allele_idx=i,
                                            frequency=frequencies[i])
            else:
                allele = self._parse_allele(allele_idx=i)
            alleles.append(allele)
        return alleles


def match_to_clinvar(genome_file, clin_file):
    """Match a genome VCF to variants in the ClinVar VCF file"""
    clin_curr_line = clin_file.next()
    genome_curr_line = genome_file.next()

    # Ignores all the lines that start with a hashtag
    while clin_curr_line.startswith("#"):
        clin_curr_line = clin_file.next()
    while genome_curr_line.startswith("#"):
        genome_curr_line = genome_file.next()

    # Advance through both files simultaneously to find matches
    while clin_curr_line or genome_curr_line:

        # Advance a file when positions aren't equal.
        clin_curr_pos = VCFLine.get_pos(clin_curr_line)
        genome_curr_pos = VCFLine.get_pos(genome_curr_line)
        try:
            if clin_curr_pos['chrom_idx'] > genome_curr_pos['chrom_idx']:
                genome_curr_line = genome_file.next()
                continue
            elif clin_curr_pos['chrom_idx'] < genome_curr_pos['chrom_idx']:
                clin_curr_line = clin_file.next()
                continue
            if clin_curr_pos['pos'] > genome_curr_pos['pos']:
                genome_curr_line = genome_file.next()
                continue
            elif clin_curr_pos['pos'] < genome_curr_pos['pos']:
                clin_curr_line = clin_file.next()
                continue
        except StopIteration:
            break

        # If we get here, start positions match.
        # Look for allele matching.

        genome_vcf_line = GenomeVCFLine(vcf_line=genome_curr_line,
                                        skip_info=True)
        # We can skip if genome has no allele information for this point.
        if not genome_vcf_line.genotype_allele_indexes:
            genome_curr_line = genome_file.next()
            continue
        clinvar_vcf_line = ClinVarVCFLine(vcf_line=clin_curr_line)

        genotype_allele_indexes = genome_vcf_line.genotype_allele_indexes
        genome_alleles = [genome_vcf_line.alleles[x] for
                          x in genotype_allele_indexes]

        # Determine zygosity. Zygosity is assumed to be exclusive
        # (heterozygous, homozygous, or hemizygous).
        if len(genome_alleles) == 1:
            zygosity = 'Hem'
        elif len(genome_alleles) == 2:
            if genome_alleles[0].sequence == genome_alleles[1].sequence:
                zygosity = 'Hom'
                genome_alleles = [genome_alleles[0]]
            else:
                zygosity = 'Het'
        else:
            raise ValueError('This code only expects to work on genomes with ' +
                             'one or two alleles called at each location.' +
                             'The following line violates this:' +
                             str(genome_vcf_line))

        # Match only if ClinVar and Genome ref_alleles match.
        if not (genome_vcf_line.ref_allele == clinvar_vcf_line.ref_allele):
            try:
                genome_curr_line = genome_file.next()
                clin_curr_line = clin_file.next()
                continue
            except StopIteration:
                break

        for genome_allele in genome_alleles:
            for allele in clinvar_vcf_line.alleles:
                if genome_allele.sequence == allele.sequence:
                    # The 'records' attribute is specific to ClinVarAlleles.
                    if hasattr(allele, 'records'):
                        try:
                            frequency = allele.frequency
                        except AttributeError:
                            frequency = 'Unknown'

                        clnsig = [int(allele.records[x].sig) for
                                  x in range(len(allele.records))]
                        data = [(allele.records[n].acc,
                                 allele.records[n].dbn,
                                 clnsig[n]) for n in
                                range(len(clnsig))]
                        if data:
                            yield (genome_curr_pos['chrom'],
                                   genome_curr_pos['pos'],
                                   clinvar_vcf_line.alleles[0].sequence,
                                   allele.sequence,
                                   data,
                                   frequency,
                                   zygosity)

        # Done matching, move on.
        try:
            genome_curr_line = genome_file.next()
            clin_curr_line = clin_file.next()
        except StopIteration:
            break


if __name__ == "__main__":
    input_clinvar_file = open(sys.argv[1])
    input_genome_file = open(sys.argv[2])
    matching = match_to_clinvar(input_genome_file, input_clinvar_file)
    for match_var in matching:
        print match_var
