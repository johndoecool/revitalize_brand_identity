import chromadb

# Initialize chromadb client
chroma_client = chromadb.Client()

# Delete existing collection if it exists
if "my_collection" in [col.name for col in chroma_client.list_collections()]:
    chroma_client.delete_collection(name="my_collection")

# Create a new collection
collection = chroma_client.create_collection(name="my_collection")

# Delete specific documents by IDs
# Assuming "id1", "id2" are the IDs of the documents you want to delete
collection.delete(ids=["id1", "id2"])

# Add new documents to the collection
collection.add(
    documents=["This is a document", "This is another document"],
    metadatas=[{"source": "my_source"}, {"source": "my_source"}],
    ids=["id1", "id2"]
)

# Retrieve documents by IDs
results = collection.get(ids=["id1", "id2"])

# Print retrieved documents
print(results)

