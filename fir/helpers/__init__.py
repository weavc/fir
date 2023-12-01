def write_json_file(file_path, j):
    import json
    try:
        with open(file_path, 'w') as f:
            f.write(json.dumps(j, indent=2))
    except Exception as e:
        print(e)
        print(f'ERROR!\nCould not write to config location "{file_path}"!')
        raise SystemExit(1)

def read_json_file(file_path) -> dict:
    import json
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(e)
        print(f'ERROR!\nCould not read to config location "{file_path}"!')
        raise SystemExit(1)

def generate_id():
    import shortuuid
    return shortuuid.uuid()[:8]