from google.cloud import datastore


class Datastore:
# Instantiates a client
    def __init__(self) -> None:
        self.client = datastore.Client()
        self.kind = "ChatDetails"

    def create(self, sender_id, details ):
        create_key = self.client.key(self.kind, sender_id )
        entity = datastore.Entity(key=create_key)
        entity.update(details)
        self.client.put(entity)
        return "Created"

    def get(self, sender_id):
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
    
    def create_chats(self, sender_id, details):
        create_key = self.client.key(self.kind, sender_id, "chats" )
        entity = datastore.Entity(key=create_key)
        entity.update(details)
        self.client.put(entity)
        return "Created"

    def get_chats(self, sender_id):

        parent_key = self.client.key(self.kind, sender_id)
        
        query = self.client.query(kind='chats', ancestor=parent_key)
        chats = list(query.fetch())
        
        return chats

if __name__ == "__main__":
    ds = Datastore()