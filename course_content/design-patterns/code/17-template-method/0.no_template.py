"""Without Template Method: the same pipeline skeleton is copied into every source."""


def csv_pipeline(lines):
    print("connecting...")
    data = list(lines)                         # extract (differs)
    data = [row.upper() for row in data]       # transform
    print(f"saving {len(data)} rows")          # load
    print("closing...")


def api_pipeline():
    print("connecting...")
    data = ["row1", "row2"]                    # extract (differs): pretend API call
    data = [row.upper() for row in data]       # transform (copied)
    print(f"saving {len(data)} rows")          # load (copied)
    print("closing...")


csv_pipeline(["a,1", "b,2", "c,3"])
api_pipeline()
