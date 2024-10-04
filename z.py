import vercel_blob
import pprint

resp = vercel_blob.list()

pprint.pprint(
    resp
)

filename = resp.get('blobs')[0].get('contentDisposition').split('filename=')[1]

print(filename)
