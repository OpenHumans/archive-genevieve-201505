import json

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
