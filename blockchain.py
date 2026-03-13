import datetime
import hashlib
import json
import os

class Blockchain:

    def __init__(self):
        self.file_name = "blockchain_data.json"

        # If file exists load it
        if os.path.exists(self.file_name):
            with open(self.file_name, "r") as file:
                self.chain = json.load(file)
        else:
            self.chain = []
            self.create_block(proof=1, previous_hash='0')

    def create_block(self, proof, previous_hash, data=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
            'data': data
        }

        self.chain.append(block)
        self.save_chain()
        return block

    def save_chain(self):
        with open(self.file_name, "w") as file:
            json.dump(self.chain, file, indent=4)

    def get_previous_block(self):
        return self.chain[-1]

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()