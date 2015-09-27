# cut a large data file into chunks but preserve lines - that is, cut at a line ending

import os


def chunk_filename(datafile, outdir, chunkid):
    """Generate an output chunk filename given this chunk id"""

    name, ext = os.path.splitext(os.path.basename(datafile))
    name += "-%d" % chunkid + ext

    return os.path.join(outdir, name)

def chunk(datafile, outdir, chunksize):
    """Cut datafile into chunks of approximately chunksize bytes
    but make sure cuts occur on a line break

    Return a list of chunk files created"""

    write_size = min(100000,chunksize)
    files = []

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    with open(datafile, 'r+b') as fd:
        offset = 0

        eof = False
        chunkid = 1

        while not eof:
            chunk_end = offset + chunksize
            chunkfile = chunk_filename(datafile, outdir, chunkid)

            # test to see if we're at the ending
            if fd.readline() == '':
                break
            else:
                fd.seek(offset)

            with open(chunkfile, 'w+b') as out:
                # first write out chunksize bytes
                for i in range(offset, chunk_end, write_size):
                    if (chunk_end-i) >= write_size:
                        data = fd.read(write_size)
                    else:
                        data = fd.read(chunk_end-i)
                    eof = (data == '')
                    out.write(data)

                if not eof:
                    # now find a line ending
                    line = fd.readline()
                    out.write(line)

            offset = fd.tell()
            chunkid += 1
            files.append(chunkfile)



    return files


if __name__=='__main__':

    import optparse
    import sys

    parser = optparse.OptionParser()
    parser.add_option("-c", "--chunksize",
                      action="store", dest="chunksize", type=int, default=1000000,
                      help="Chunk size for splitting data files (bytes), default 1000000")
    parser.add_option("-o", "--outdir", dest="outdir", action="store", default='chunks',
                      help="write split files out to OUTDIR, default 'chunks'")

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.print_help(sys.stdout)
        exit()
    filename = args[0]

    files = chunk(filename, options.outdir, options.chunksize)

    print "Wrote %d files to directory '%s'" % (len(files), options.outdir)
