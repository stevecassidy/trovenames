import unittest
import shutil
import os
import tempfile

from trovenames.index import TroveIndexBuilder, TroveIndex, TroveSwiftIndexBuilder


class testIndex(unittest.TestCase):

    def test_create_index(self):
        """Create an index"""

        indexfile = tempfile.mktemp()
        self.addCleanup(os.unlink, indexfile)

        index = TroveIndexBuilder("test/short.dat", out=indexfile)

        # read the index file that was created
        with open(indexfile, 'r+b') as fd:
            indextext = fd.read()
            indexlines = indextext.split('\n')

        # 11 lines includes on blank line at the end
        self.assertEquals(11, len(indexlines))
        del indexlines[10]

        # check the first character of each line
        docs = [line[0] for line in indexlines]
        self.assertEquals(['1', '2', '3', '4', '5', '6', '7', '8', '9', '1'], docs)

        # check some lines from the index
        ref = "1, 0, 31, test/short.dat"
        self.assertEqual(ref, indexlines[0])
        ref = "10, 279, 32, test/short.dat"
        self.assertEqual(ref, indexlines[9])

    def test_read_index(self):
        """Read an index from a file"""

        indexfile = tempfile.mktemp()
        self.addCleanup(os.unlink, indexfile)

        TroveIndexBuilder("test/short.dat", out=indexfile)

        index = TroveIndex(indexfile)

        docs = sorted([doc for doc in index.documents])
        self.assertEquals(10, len(docs))

        self.assertEquals(['1', '10', '2', '3', '4', '5', '6', '7', '8', '9'], docs)

        doc = index.get_document('1')
        ref = {"id":"1","titleName":"Hello"}
        self.assertDictEqual(ref, doc)

        doc = index.get_document('10')
        ref = {"id":"10","titleName":"Hello"}
        self.assertNotEquals(None, doc)
        self.assertDictEqual(ref, doc)


    def test_create_index_swift(self):
        """Create an index of a swift document"""

        indexfile = tempfile.mktemp()
        self.addCleanup(os.unlink, indexfile)

        index = TroveSwiftIndexBuilder("short.dat", out=indexfile)

        # read the index file that was created
        with open(indexfile, 'r+b') as fd:
            indextext = fd.read()
            indexlines = indextext.split('\n')

        # 11 lines includes on blank line at the end
        self.assertEquals(11, len(indexlines))
        del indexlines[10]

        # check the first character of each line
        docs = [line[0] for line in indexlines]
        self.assertEquals(['1', '2', '3', '4', '5', '6', '7', '8', '9', '1'], docs)

        # check some lines from the index
        ref = "1, 0, 31, short.dat"
        self.assertEqual(ref, indexlines[0])
        ref = "10, 279, 32, short.dat"
        self.assertEqual(ref, indexlines[9])


if __name__=='__main__':
    unittest.main()
