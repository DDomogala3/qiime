#!/usr/bin/env python

__author__ = "William Walters"
__copyright__ = "Copyright 2011, The QIIME Project"
__credits__ = ["William Walters"] #remember to add yourself
__license__ = "GPL"
__version__ = "1.5.0-dev"
__maintainer__ = "William Walters"
__email__ = "william.a.walters@colorado.edu"
__status__ = "Development"

from os.path import join, basename, exists
from shutil import rmtree

from cogent.util.unit_test import TestCase, main
from cogent.util.misc import remove_files, get_random_directory_name

from qiime.util import create_dir, get_tmp_filename
from qiime.add_qiime_labels import (add_qiime_labels, check_mapping_data,
 get_fasta_fps, write_combined_fasta, check_fasta_fps)

class AddQiimeLabelsTests(TestCase):
    def setUp(self):
        # create the temporary input files that will be used
        
        self._files_to_remove = []
        
        # Need an empty input directory to control fasta files present
        
        self.input_dir = get_random_directory_name(prefix = '/tmp/') + "/"
        # Input data
        self.sample_fasta1 = sample_fasta1
        self.sample_fasta2 = sample_fasta2
        self.sample_fasta3 = sample_fasta3
        
        self.fasta1_fp = join(self.input_dir, "fasta1.fasta")
        map_file = open(self.fasta1_fp, 'w')
        map_file.write(self.sample_fasta1)
        map_file.close()
        
        self.fasta2_fp = join(self.input_dir, "fasta2.fna")
        map_file = open(self.fasta2_fp, 'w')
        map_file.write(self.sample_fasta2)
        map_file.close()
        
        self.fasta3_fp = join(self.input_dir, "fasta3.fa")
        map_file = open(self.fasta3_fp, 'w')
        map_file.write(self.sample_fasta3)
        map_file.close()
        
        # Output data
        
        self.output_dir = get_random_directory_name(prefix = '/tmp/')
        self.output_dir += '/'
        
        create_dir(self.output_dir)
        
        self._files_to_remove =\
         [self.fasta1_fp, self.fasta2_fp, self.fasta3_fp]
        
    def tearDown(self):
        if self._files_to_remove:
            remove_files(self._files_to_remove)
        if exists(self.output_dir):
            rmtree(self.output_dir)
        if exists(self.input_dir):
            rmtree(self.input_dir)
            
    def test_add_qiime_labels_valid_data(self):
        """ Tests overall script functionality """
        
        # With valid data should not raise any errors
        
        mapping_data = ['Sample1\t%s' % basename(self.fasta1_fp),
                        'Sample2\t%s' % basename(self.fasta2_fp),
                        'Sample3\t%s' % basename(self.fasta3_fp)
                        ]
                        
        add_qiime_labels(mapping_data, self.input_dir, 
        self.output_dir)
        
        output_fp = open(join(self.output_dir, "combined_seqs.fna"), "U")
        output_lines = [line.strip() for line in output_fp]
        
        expected_output_lines = ['>Sample2_0 label3 ZZZ', 'AACGYAACGAGA',
         '>Sample2_1 label4', 'ACAGAGAGAGGGGAGA',
         '>Sample3_2 label5 ;LKJ', 'ACAGGGATTTTTAT',
         '>Sample1_3 label1 XXX', 'ACAGATTACGA',
         '>Sample1_4 label2 YYY', 'ACATAAAATAGCCGGAG']
         
        self.assertEqual(output_lines, expected_output_lines)
        
    def test_add_qiime_labels_invalid_data(self):
        """ Tests overall script functionality """
        
        # Should raise error with duplicated fasta path used.
        
        mapping_data = ['Sample1\t%s' % basename(self.fasta1_fp),
                        'Sample2\t%s' % basename(self.fasta2_fp),
                        'Sample3\t%s' % basename(self.fasta1_fp)
                        ]
                        
        self.assertRaises(ValueError, add_qiime_labels, mapping_data,
         self.input_dir, self.output_dir)
         
    def test_check_mapping_data_valid_data(self):
        """ Returns expected dict with valid data supplied """
        
        mapping_data = ['Sample1\tFile1',
                        'Sample2\tFile2',
                        'Sample3\tFile3'
                        ]
                        
        expected_data = {'File3': 'Sample3',
                         'File2': 'Sample2',
                         'File1': 'Sample1'}
        
        actual_data = check_mapping_data(mapping_data)
        
        self.assertEqual(actual_data, expected_data)
        
    def test_check_mapping_data_dups(self):
        """ Raises errors if duplicate file names supplied """
        
        mapping_data = ['Sample1\tFile3',
                        'Sample2\tFile2',
                        'Sample3\tFile3'
                        ]
        
        self.assertRaises(ValueError, check_mapping_data, mapping_data)
        
    def test_check_mapping_data_invalid_sampleids(self):
        """ Raises errors if invalid SampleIDs supplied """
        
        mapping_data = ['Sa!mple1\tFile1',
                        'Sample2\tFile2',
                        'Sample3\tFile3'
                        ]
        
        self.assertRaises(ValueError, check_mapping_data, mapping_data)
        
    def test_check_mapping_data_invalid_mapping_file_format(self):
        """ Raises errors if missing data from mapping file """
        
        mapping_data = ['Sample1\tFile1',
                        'Sample2',
                        'Sample3\tFile3'
                        ]
        
        self.assertRaises(IndexError, check_mapping_data, mapping_data)
        
    def test_get_fasta_fps(self):
        """ Properly returns fasta files from given directory """
        
        actual_fastas = get_fasta_fps(self.input_dir)
        
        expected_fasta = [self.fasta2_fp, self.fasta3_fp, self.fasta1_fp]
        
        self.assertEqual(actual_fastas, expected_fasta)
        
    def test_write_combined_fasta(self):
        """ Properly writes combined fasta data """
        
        mapping_data = {'%s' % basename(self.fasta1_fp):'Sample1',
                        '%s' % basename(self.fasta2_fp):'Sample2',
                        '%s' % basename(self.fasta3_fp):'Sample3'
                        }
                        
        fasta_fps = [self.fasta2_fp, self.fasta3_fp, self.fasta1_fp]
        
        write_combined_fasta(mapping_data, fasta_fps, self.output_dir, 
         counter = 100)
        
        output_fp = open(join(self.output_dir, "combined_seqs.fna"), "U")
        output_lines = [line.strip() for line in output_fp]
        
        expected_output_lines = ['>Sample2_100 label3 ZZZ', 'AACGYAACGAGA',
                                 '>Sample2_101 label4', 'ACAGAGAGAGGGGAGA',
                                 '>Sample3_102 label5 ;LKJ', 'ACAGGGATTTTTAT',
                                 '>Sample1_103 label1 XXX', 'ACAGATTACGA',
                                 '>Sample1_104 label2 YYY', 'ACATAAAATAGCCGGAG'
                                ]
         
        self.assertEqual(output_lines, expected_output_lines)
        
    def test_check_fasta_fps(self):
        """ Checks that all fasta files are found in mapping data """
        
        mapping_data = {'%s' % basename(self.fasta1_fp):'Sample1',
                        '%s' % basename(self.fasta2_fp):'Sample2',
                        '%s' % basename(self.fasta3_fp):'Sample3'
                        }
                        
        fasta_fps = [self.fasta2_fp, self.fasta3_fp, self.fasta1_fp]
        
        # Should return True for all fasta files found
        self.assertTrue(check_fasta_fps(mapping_data, fasta_fps))
        
        mapping_data = {'%s' % basename(self.fasta1_fp):'Sample1',
                        '%s' % basename(self.fasta1_fp):'Sample2',
                        '%s' % basename(self.fasta3_fp):'Sample3'
                        }
                        
        fasta_fps = [self.fasta2_fp, self.fasta3_fp, self.fasta1_fp]
        
        # Should raise error due to fasta file found but not defined in mapping
        self.assertRaises(ValueError,check_fasta_fps,mapping_data, fasta_fps)

            
sample_fasta1 = """>label1 XXX
ACAGATTACGA
>label2 YYY
ACATAAAATAGCCGGAG
"""

sample_fasta2 = """>label3 ZZZ
AACGYAACGAGA
>label4
ACAGAGAGAGGGGAGA
"""

sample_fasta3 = """>label5 ;LKJ
ACAGGGATTTTTAT
"""

if __name__ =='__main__':
    main()