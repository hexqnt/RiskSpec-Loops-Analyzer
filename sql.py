def read_file(filename):
    with open(f'sql/{filename}', 'r') as file:
        return file.read()


getFTGraph = read_file('GetFTGraph.sql')
getAvailableDB = read_file('GetAvailableDB.sql')
