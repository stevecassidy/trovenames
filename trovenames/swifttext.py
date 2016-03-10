
import swiftclient
import os
from cStringIO import StringIO

from util import readconfig

class SwiftTextContainer:

    def __init__(self):

        config = readconfig()
        user = config.get('default', "USERNAME")
        key = config.get('default', "PASSWORD")
        authurl = config.get('default', "AUTH_URL")
        tenant_name = config.get('default', 'TENANT_NAME')

        self.container = config.get('default', 'CONTAINER')
        self.conn = swiftclient.Connection(user=user,
                                           key=key,
                                           authurl=authurl,
                                           auth_version='2.0',
                                           tenant_name=tenant_name )



    def documents(self):
        """Return an iterator over the documents in this container
        each result is a dictionary containing keys for 'name', 'bytes', 'last_modified' and 'hash'"""

        headers, documents = self.conn.get_container(self.container)

        for document in documents:
            yield document

    def get_by_offset(self, objectname, offset, length):
        """Get the content of this file starting at the given offset, reading length
        bytes"""

        # need to subtract one from the end point since Range includes the last byte
        headers = {'Range': 'bytes=%d-%d' % (offset, offset+length-1)}
        responseheaders, content = self.conn.get_object(self.container, objectname, headers=headers)
        return content

    def document_lines(self, objectname):
        """An iterator over lines from an object in the Swift object store
        each result is a tuple (offset, line) where offset is the current
        offset into the document"""

        headers, content = self.conn.get_object(self.container, objectname, resp_chunk_size=10000)

        remainder = ""
        offset = 0

        for block in content:

            stream = StringIO(remainder + block)
            for line in stream:
                if line.endswith('}\n'):
                    yield (offset, line)
                    offset += len(line)
                else:
                    remainder = line


if __name__=='__main__':

    sw = SwiftTextContainer()
    for doc in sw.documents():
        print doc

    count = 0
    for line in sw.document_lines('trove-sample.dat'):
        print count, line[0], line[1][0:3], '...', line[1][-10:],
        count += 1
