import unittest
import shutil

from index import TroveIndex


class testIndex(unittest.TestCase):



    def test_create_index(self):
        """Create an index"""

        outdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, outdir)

        index = TroveIndex("test/short.dat", chunksize=2, outdir=outdir)

        docs = sorted([doc for doc in index.documents()])
        self.assertEquals(10, len(docs))

        self.assertEquals(['1', '10', '2', '3', '4', '5', '6', '7', '8', '9'], docs)

        doc = index.get_document('1')
        ref = {"id":"1","titleName":"Hello"}
        self.assertDictEqual(ref, doc)

        doc = index.get_document('10')
        ref = {"id":"10","titleName":"Hello"}
        self.assertNotEquals(None, doc)
        self.assertDictEqual(ref, doc)

if __name__=='__main__':
    unittest.main()
