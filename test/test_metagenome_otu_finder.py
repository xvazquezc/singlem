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


import sys, os, unittest
sys.path = [os.path.join(os.path.dirname(os.path.realpath(__file__)),'..')]+sys.path

from singlem.metagenome_otu_finder import MetagenomeOtuFinder
from singlem.sequence_classes import AlignedProteinSequence

class Tests(unittest.TestCase):
    def test__nucleotide_alignment(self):
        m = MetagenomeOtuFinder()
        self.assertEqual(('AAATTT---GGG',9),\
            m._nucleotide_alignment(AlignedProteinSequence('name','AC-D'), 'AAATTTGGG', [0,1,2,3]))
        
        
    def test__nucleotide_alignment_include_inserts(self):
        m = MetagenomeOtuFinder()
        self.assertEqual(('AAA---GGG',9),\
            m._nucleotide_alignment(AlignedProteinSequence('name','AC-D'), 'AAATTTGGG', [0,2,3]))
        self.assertEqual(('AAAttt---GGG',9),\
            m._nucleotide_alignment(AlignedProteinSequence('name','AC-D'), 'AAATTTGGG', [0,2,3], include_inserts=True))
        self.assertEqual(('AAAtttGGG',9),\
            m._nucleotide_alignment(AlignedProteinSequence('name','AC-D'), 'AAATTTGGG', [0,3], include_inserts=True))
                            
if __name__ == "__main__":
    unittest.main()
