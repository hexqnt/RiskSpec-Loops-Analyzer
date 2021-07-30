
def read_file(filename):
    with open(f'sql/{filename}', 'r') as file:
        return file.read()


def init_sql_queries():
    global getFTGraph
    getFTGraph = read_file('GetFTGraph.sql')
    global getAvailableDB
    getAvailableDB = read_file('GetAvailableDB.sql')
