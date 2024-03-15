from google.cloud import datastore


class Datastore:
# Instantiates a client
    def __init__(self) -> None:
        self.client = datastore.Client()
        self.kind = "ChatDetails"

    def create(self, sender_id, details, chat ):
        create_key = self.client.key(self.kind, sender_id)
        if chat:
            create_key = self.client.key(self.kind, sender_id, "chats")
        
        create_key = self.client.key(self.kind, sender_id )
        entity = datastore.Entity(key=create_key)
        entity.update(details)
        self.client.put(entity)
        return "Created"

    def get_thread(self, sender_id):
        filter_Key = self.client.key(self.kind,sender_id)
    
        query = self.client.query(kind=self.kind)
        query.add_filter('__key__', '=', filter_Key)
    
        results = list(query.fetch(limit=1))
        if results:
            entity = results[0]
            try:
                thread_id = entity['thread_id']
                return thread_id
            except:
                return
        else:
            return
    
    def get_chats(self, sender_id):
        parent_key = self.client.key(self.kind, sender_id)
        query = self.client.query(kind='chats', ancestor=parent_key)
        return list(query.fetch())

if __name__ == "__main__":
    ds = Datastore()