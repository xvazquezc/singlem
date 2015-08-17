#!/usr/bin/env python

#=======================================================================
# Authors: Ben Woodcroft
#
# Unit tests.
#
# Copyright
#
# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License.
# If not, see <http://www.gnu.org/licenses/>.
#=======================================================================

import unittest
import subprocess
import os.path
import tempfile
import tempdir
from string import split

path_to_script = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..','bin','singlem')
path_to_data = os.path.join(os.path.dirname(os.path.realpath(__file__)),'data')

class Tests(unittest.TestCase):
    headers = split('gene sample sequence num_hits coverage taxonomy')

    def test_minimal(self):
        expected = [self.headers,['ribosomal_protein_L11_rplK_gpkg','minimal','GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC','7','17.07','Root; k__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales'],
['ribosomal_protein_S2_rpsB_gpkg','minimal','CGTCGTTGGAACCCAAAAATGAAAAAATATATCTTCACTGAGAGAAATGGTATTTATATC','6','14.63','Root; k__Bacteria; p__Firmicutes; c__Bacilli'],
['ribosomal_protein_S17_gpkg','minimal','GCTAAATTAGGAGACATTGTTAAAATTCAAGAAACTCGTCCTTTATCAGCAACAAAACGT','9','21.95','Root; k__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales; f__Staphylococcaceae; g__Staphylococcus']]
        exp = sorted(["\t".join(x) for x in expected]+[''])

        cmd = "%s --quiet pipe --forward %s/1_pipe/minimal.fa --otu_table /dev/stdout --threads 4" % (path_to_script,
                                                                                                    path_to_data)
        self.assertEqual(exp, sorted(subprocess.check_output(cmd, shell=True).split("\n")))
        
    def test_no_hits(self):
        expected = []
        exp = sorted(["\t".join(x) for x in expected]+[''])
        
        with tempfile.NamedTemporaryFile(prefix='singlem_test',suffix='.fasta') as f:
            f.write(">seq\n")
            f.write("ATG"+'A'*300+"\n")
            f.flush()
            
            cmd = "%s --debug pipe --forward %s --otu_table /dev/stdout --threads 4 2>/dev/null" % (path_to_script,
                                                                                                    f.name)
            self.assertEqual(exp, sorted(subprocess.check_output(cmd, shell=True).split("\n")))
        
    def test_insert(self):
        expected = [self.headers,['ribosomal_protein_S17_gpkg','insert','GCTAAATTAGGAGACATTGTTAAAATTCAAGAAACTCGTCCTTTATCAGCAACAAAACGT','2','4.95','Root; k__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales; f__Staphylococcaceae; g__Staphylococcus']]
        exp = sorted(["\t".join(x) for x in expected]+[''])

        cmd = "%s --quiet pipe --forward %s/1_pipe/insert.fna --otu_table /dev/stdout --threads 4 2>/dev/null" % (path_to_script,
                                                                                                    path_to_data)
        self.assertEqual(exp, sorted(subprocess.check_output(cmd, shell=True).split("\n")))
        
    def test_makedb_query(self):
        otu_table = [self.headers,['ribosomal_protein_L11_rplK_gpkg','minimal','GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC','7','4.95','Root; k__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales'],
['ribosomal_protein_S2_rpsB_gpkg','minimal','CGTCGTTGGAACCCAAAAATGAAAAAATATATCTTCACTGAGAGAAATGGTATTTATATC','6','4.95','Root; k__Bacteria; p__Firmicutes; c__Bacilli'],
['ribosomal_protein_S17_gpkg','minimal','GCTAAATTAGGAGACATTGTTAAAATTCAAGAAACTCGTCCTTTATCAGCAACAAAACGT','9','4.95','Root; k__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales; f__Staphylococcaceae; g__Staphylococcus']]
        otu_table = "\n".join(["\t".join(x) for x in otu_table])
        
        with tempfile.NamedTemporaryFile() as f:
            f.write(otu_table)
            f.flush()
            
            with tempdir.TempDir() as d:
                #d = '/tmp/d'
                cmd = "%s makedb --db_path %s/db --otu_table %s" %(path_to_script,
                                                                d,
                                                                f.name)
                subprocess.check_call(cmd, shell=True)
                
                cmd = "%s query --query_sequence %s --db %s/db --otu_table_type sparse" % (path_to_script,
                                                                'CGTCGTTGGAACCCAAAAATGAAAAAATATATCTTCACTGAGAGAAATGGTATTTATATCA', # second sequence with an extra A at the end
                                                                d)
                
                expected = [['query_name','query_sequence','divergence','num_hits','sample','marker','hit_sequence','taxonomy'],
                            ['unnamed_sequence','CGTCGTTGGAACCCAAAAATGAAAAAATATATCTTCACTGAGAGAAATGGTATTTATATCA','1','6','minimal','ribosomal_protein_S2_rpsB_gpkg','CGTCGTTGGAACCCAAAAATGAAAAAATATATCTTCACTGAGAGAAATGGTATTTATATC','Root; k__Bacteria; p__Firmicutes; c__Bacilli']]
                expected = ["\t".join(x) for x in expected]+['']
                self.assertEqual(expected,
                                 subprocess.check_output(cmd, shell=True).split("\n"))
                
    def test_query_with_otu_table(self):
        with tempfile.NamedTemporaryFile() as f:
            query = [self.headers,
                     # second sequence with an extra A at the end
                     ['ribosomal_protein_L11_rplK_gpkg','minimal','CGTCGTTGGAACCCAAAAATGAAAAAATATATCTTCACTGAGAGAAATGGTATTTATATCA','7','4.95','Root; k__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales']]
            query = "\n".join(["\t".join(x) for x in query])
            f.write(query)
            f.flush()
            
            cmd = "%s query --query_otu_table %s --db %s --otu_table_type sparse" % (path_to_script,
                                                            f.name, 
                                                            os.path.join(path_to_data,'a.sdb'))
            
            expected = [['query_name','query_sequence','divergence','num_hits','sample','marker','hit_sequence','taxonomy'],
                        ['minimal;ribosomal_protein_L11_rplK_gpkg','CGTCGTTGGAACCCAAAAATGAAAAAATATATCTTCACTGAGAGAAATGGTATTTATATCA','1','6','minimal','ribosomal_protein_S2_rpsB_gpkg','CGTCGTTGGAACCCAAAAATGAAAAAATATATCTTCACTGAGAGAAATGGTATTTATATC','Root; k__Bacteria; p__Firmicutes; c__Bacilli']]
            expected = ["\t".join(x) for x in expected]+['']
            self.assertEqual(expected,
                             subprocess.check_output(cmd, shell=True).split("\n"))
            
    def test_query_with_otu_table_two_samples(self):
        with tempfile.NamedTemporaryFile() as f:
            query = [self.headers,
                     # second sequence with an extra A at the end
                     ['ribosomal_protein_L11_rplK_gpkg','minimal','CGTCGTTGGAACCCAAAAATGAAAAAATATATCTTCACTGAGAGAAATGGTATTTATATCA','7','4.95','Root; k__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales'],
                     ['ribosomal_protein_L11_rplK_gpkg','maximal','CGTCGTTGGAACCCAAAAATGAAATAATATATCTTCACTGAGAGAAATGGTATTTATATCA','7','4.95','Root; k__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales']] # converted A to T in the middle
            query = "\n".join(["\t".join(x) for x in query])
            f.write(query)
            f.flush()
            
            cmd = "%s query --query_otu_table %s --db %s --otu_table_type sparse" % (path_to_script,
                                                            f.name, 
                                                            os.path.join(path_to_data,'a.sdb'))
            
            expected = [['query_name','query_sequence','divergence','num_hits','sample','marker','hit_sequence','taxonomy'],
                        ['minimal;ribosomal_protein_L11_rplK_gpkg','CGTCGTTGGAACCCAAAAATGAAAAAATATATCTTCACTGAGAGAAATGGTATTTATATCA','1','6','minimal','ribosomal_protein_S2_rpsB_gpkg','CGTCGTTGGAACCCAAAAATGAAAAAATATATCTTCACTGAGAGAAATGGTATTTATATC','Root; k__Bacteria; p__Firmicutes; c__Bacilli'],
                        ['maximal;ribosomal_protein_L11_rplK_gpkg','CGTCGTTGGAACCCAAAAATGAAATAATATATCTTCACTGAGAGAAATGGTATTTATATCA','2','6','minimal','ribosomal_protein_S2_rpsB_gpkg','CGTCGTTGGAACCCAAAAATGAAAAAATATATCTTCACTGAGAGAAATGGTATTTATATC','Root; k__Bacteria; p__Firmicutes; c__Bacilli']]
            expected = ["\t".join(x) for x in expected]+['']
            observed = subprocess.check_output(cmd, shell=True).split("\n")
            self.assertEqual(expected, observed)
        
    def test_fasta_query(self):
        with tempfile.NamedTemporaryFile() as f:
            query = "\n".join([">seq1 comment",'CGTCGTTGGAACCCAAAAATGAAAAAATATATCTTCACTGAGAGAAATGGTATTTATATCA',
                               ">sseq4",       'CGTCGTTGGAACCCAAAAATGAAATAATATATCTTCACTGAGAGAAATGGTATTTATATCA',''])
            f.write(query)
            f.flush()
            
            cmd = "%s query --query_fasta %s --db %s --otu_table_type sparse" % (path_to_script,
                                                            f.name, 
                                                            os.path.join(path_to_data,'a.sdb'))
            
            expected = [['query_name','divergence','num_hits','sample','marker','hit_sequence','taxonomy'],
                        ['seq1','1','6','minimal','ribosomal_protein_S2_rpsB_gpkg','CGTCGTTGGAACCCAAAAATGAAAAAATATATCTTCACTGAGAGAAATGGTATTTATATC','Root; k__Bacteria; p__Firmicutes; c__Bacilli'],
                        ['sseq4','2','6','minimal','ribosomal_protein_S2_rpsB_gpkg','CGTCGTTGGAACCCAAAAATGAAAAAATATATCTTCACTGAGAGAAATGGTATTTATATC','Root; k__Bacteria; p__Firmicutes; c__Bacilli']]
            expected = ["\t".join(x) for x in expected]+['']
            observed = subprocess.check_output(cmd, shell=True).split("\n")
            self.assertEqual(expected, observed)
            
    def test_known_tax_table(self):
        expected = [self.headers,['ribosomal_protein_L11_rplK_gpkg','minimal','GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC','7','17.07','some1'],
['ribosomal_protein_S2_rpsB_gpkg','minimal','CGTCGTTGGAACCCAAAAATGAAAAAATATATCTTCACTGAGAGAAATGGTATTTATATC','6','14.63','some3'],
['ribosomal_protein_S17_gpkg','minimal','GCTAAATTAGGAGACATTGTTAAAATTCAAGAAACTCGTCCTTTATCAGCAACAAAACGT','9','21.95','Root; k__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales; f__Staphylococcaceae; g__Staphylococcus']]
        exp = sorted(["\t".join(x) for x in expected]+[''])
        
        with tempfile.NamedTemporaryFile(prefix='singlem_test_known') as t:
            t.write('\n'.join(["\t".join(x) for x in expected[:3]]))
            t.flush() 

            cmd = "%s --quiet pipe --forward %s/1_pipe/minimal.fa --otu_table /dev/stdout --threads 4 --known_otu_tables %s"\
                 % (path_to_script,
                    path_to_data,
                    t.name)
            self.assertEqual(exp, sorted(subprocess.check_output(cmd, shell=True).split("\n")))
        
    #     @unittest.skip
    #     def test_bootstrap(self):
    #         self.assertEqual(True, False)
                            
if __name__ == "__main__":
    unittest.main()
