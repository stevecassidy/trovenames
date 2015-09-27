
import swiftclient
import os
from ConfigParser import ConfigParser
import StringIO


class SwiftTextContainer:

    def __init__(self):

        config = self.readconfig()
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

    def readconfig(self):
        configfile = os.path.join(os.path.dirname(__file__), 'config.ini')
        config = ConfigParser()
        config.read(configfile)

        return config

    def documents(self):
        """Return an iterator over the documents in this container
        each result is a dictionary containing keys for 'name', 'bytes', 'last_modified' and 'hash'"""

        headers, documents = self.conn.get_container(self.container)

        for document in documents:
            yield document

    def document_lines(self, objectname):
        """An iterator over lines from an object in the Swift object store
        each result is a tuple (offset, line) where offset is the current
        offset into the document"""

        headers, content = self.conn.get_object(self.container, objectname, resp_chunk_size=10000)

        remainder = ""
        offset = 0

        for block in content:

            stream = StringIO.StringIO(remainder + block)
            for line in stream:
                if line.endswith('\n'):
                    yield (offset, line)
                    offset += len(line)
                else:
                    remainder = line


if __name__=='__main__':

    sw = SwiftTextContainer()
    for doc in sw.documents():
        print doc

    for line in sw.document_lines('trove-small.dat'):
        print line
