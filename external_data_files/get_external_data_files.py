"""Get external data files used by Genevieve"""

from ftplib import FTP


def get_hgnc_gene_names():
    """Download official gene symbols from HGNC"""
    # According to http://www.genenames.org/about/overview (copied 2013/07/08)
    # "No restrictions are imposed on access to, or use of, the data provided
    # by the HGNC, which are provided to enhance knowledge and encourage
    # progress in the scientific community. The HGNC provide these data in good
    # faith, but make no warranty, express or implied, nor assume any legal
    # liability or responsibility for any purpose for which they are used."
    hgnc_ftp = FTP('ftp.ebi.ac.uk')
    hgnc_ftp.login()
    with open('hgnc_gene_with_protein_product.txt.gz', 'wb') as outfile:
        hgnc_ftp.retrbinary('RETR pub/databases/genenames/locus_types/' +
                            'gene_with_protein_product.txt.gz',
                            outfile.write)
    hgnc_ftp.quit()


def get_ncbi_genetic_testing_registry(ncbi_ftp_login=None):
    """Download data about the Genetic Testing Registry from NCBI

    These report when testing is available for a gene, referencing genes by
    NCBI Gene ID.
    """
    if ncbi_ftp_login:
        ncbi_ftp = ncbi_ftp_login
    else:
        ncbi_ftp = FTP('ftp.ncbi.nih.gov')
        ncbi_ftp.login()
    with open('ncbi_gene_testing_registry.txt', 'wb') as outfile:
        ncbi_ftp.retrbinary('RETR pub/GTR/data/test_condition_gene.txt',
                            outfile.write)
    if not ncbi_ftp_login:
        ncbi_ftp.quit()


def get_ncbi_gene_id_mapping(ncbi_ftp_login=None):
    """Download data mapping NCBI Gene IDs to HGNC Gene Symbols"""
    if ncbi_ftp_login:
        ncbi_ftp = ncbi_ftp_login
    else:
        ncbi_ftp = FTP('ftp.ncbi.nih.gov')
        ncbi_ftp.login()
    with open('ncbi_homo_sapiens_gene_info.txt.gz', 'wb') as outfile:
        ncbi_ftp.retrbinary(
            'RETR gene/DATA/GENE_INFO/Mammalia/Homo_sapiens.gene_info.gz',
            outfile.write)
    if not ncbi_ftp_login:
        ncbi_ftp.quit()


def get_ncbi_mim2gene_mapping(ncbi_ftp_login=None):
    """Get mapping between NCBI Gene IDs and MIM IDs used by OMIM"""
    # The following download links NCBI Gene IDs with MIM IDs.
    if ncbi_ftp_login:
        ncbi_ftp = ncbi_ftp_login
    else:
        ncbi_ftp = FTP('ftp.ncbi.nih.gov')
        ncbi_ftp.login()
    with open('ncbi_mim2gene.txt', 'wb') as outfile:
        ncbi_ftp.retrbinary('RETR gene/DATA/mim2gene_medgen', outfile.write)
    if not ncbi_ftp_login:
        ncbi_ftp.quit()


def get_ncbi_clinvar_vcf(ncbi_ftp_login=None):
    """Get mapping Gene IDs and CUIs to MIM IDs used by OMIM"""
    # The following download links NCBI Gene IDs with MIM IDs.
    if ncbi_ftp_login:
        ncbi_ftp = ncbi_ftp_login
    else:
        ncbi_ftp = FTP('ftp.ncbi.nih.gov')
        ncbi_ftp.login()
    with open('clinvar-latest-b37.vcf.gz', 'wb') as outfile:
        ncbi_ftp.retrbinary(
            'RETR pub/clinvar/vcf_GRCh37/clinvar-latest.vcf.gz',
            outfile.write)
    if not ncbi_ftp_login:
        ncbi_ftp.quit()


def get_ncbi_files():
    """Retrieve files from NCBI"""
    # There was no data use, copyright, or licensing information found on the
    # NCBI FTP site (checked 2013/07/08). We believe these files are work
    # produced by the US government and thus public domain under Section 105
    # of the Copyright Act.
    ncbi_ftp = FTP('ftp.ncbi.nih.gov')
    ncbi_ftp.login()
    get_ncbi_genetic_testing_registry(ncbi_ftp)
    get_ncbi_gene_id_mapping(ncbi_ftp)
    get_ncbi_mim2gene_mapping(ncbi_ftp)
    get_ncbi_clinvar_vcf(ncbi_ftp)


def get_ucsc_hg19_2bit():
    """Get 2bit representation of hg19 reference genome"""
    # According to
    # ftp://hgdownload.soe.ucsc.edu/goldenPath/hg19/database/README.txt
    # (copied 2013/07/08): "All the files and tables in this directory are
    # freely usable for any purpose."
    ucsc_ftp = FTP('hgdownload.cse.ucsc.edu')
    ucsc_ftp.login()
    with open('hg19.2bit', 'wb') as outfile:
        ucsc_ftp.retrbinary('RETR goldenPath/hg19/bigZips/hg19.2bit',
                            outfile.write)
    ucsc_ftp.quit()

if __name__ == ('__main__'):
    get_hgnc_gene_names()
    get_ncbi_files()
    get_ucsc_hg19_2bit()
