class DMHandle:
  """
  Data Manager handle points to a separate thing in the database
  that tracks completeness and holds the keys for all the elements
  of the dataset and the ddict assocatied with the DataManger.

  keys are soemthing like UUID-{record}-{part}
  """

  def is_complete(record):
    if record in self.complete_records:
      return True
    else:
      all_keys = ddict.contains(self.keys(record, range(nparts)))
      if all_keys:
        self.complete_records.append(record)
        return True


class AppHandle:
  """
  Similar to DMHandle but just holds one key. On registering, the client interacts with the
  frontend of the SQL server to get the UUID. It will construct the key based on record and part
  """

class DataManager:

  def register_data_descriptor():
    pass
    # Write description to database


def driver():

  dm = DataManager()

  metadata = json.load(metadata.json)

  h = dm.register_data_descriptor(metadata, nparts=num_mpi_procs)
  task_producer = ComputeTask("producer", nparts=num_mpi_procs)
  task_consumer = ComputeTask("consumer")

def producer():
  def init():
    metadata = json.load(metadata.json)
    h = client.register_outgoing_data_descriptor(metadata, rank) # If not registered in the driver, throw an error
    return h

  def make_data(iteration, h):
    data = random(100,100)
    h.put(data, part=rank, record=iteration) # Key constructed based on part and record

  def main():
    h = init()

    for iteration in range(10):
      make_data(iteration, h)

def consumer():

  def init():
    metadata = json.load(metadata.json)
    h = client.register_incoming_data_descriptor(metadata) # If not registered in the driver, throw an error
    return h

  def consume_data(iteration, h):
    h.get(iteration)
    print(iteration.mean())

  def main():
    h = init()
    for in range(10):
      consume_data(iteration, h)


