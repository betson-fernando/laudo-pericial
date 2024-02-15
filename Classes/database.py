import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from pathlib import Path
from google.cloud.firestore_v1.base_query import FieldFilter


# Use a service account.
cred = credentials.Certificate(Path(__file__).parent.parent.joinpath(r'env_var/firestore_credentials.json'))

app = firebase_admin.initialize_app(cred)

db = firestore.client()

col = db.collection('casos_col')
docs = col.where(filter=FieldFilter('num_caso','==', '9999.9/9999')).stream()

for doc in docs:
    print(f"{doc.id} => {doc.to_dict()}")
