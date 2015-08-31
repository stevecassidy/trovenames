
import unittest
import tempfile
import shutil

from chunk import chunk



class ChunkTest(unittest.TestCase):


    def test_chunk_tiny(self):

        datafile = "test/short.dat"
        outdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, outdir)


        # chunk into 60 byte files, should be two lines
        # per chunk
        files = chunk(datafile, outdir, 60)

        self.assertEquals(5, len(files))

        # each file should have two lines

        concat = []
        for f in files:
            with open(f, 'r+b') as fd:
                lines = fd.readlines()
                self.assertEquals(2, len(lines))
                concat.extend(lines)

        # joining them together should give the same
        # as the original file
        with open(datafile, 'r+b') as fd:
            lines = fd.readlines()
            self.assertEquals(len(lines), len(concat))
            self.assertEquals(lines, concat)


if __name__=='__main__':

    unittest.main()
