
def write_toml_file(file_path, to: dict, test_write: bool = True):
    import tomli_w
    if test_write:
        write_toml_file(file_path + '.tmp', to, test_write=False)

    try:
        with open(file_path, "wb") as f:
            toml = tomli_w.dump(to, f)
    except Exception as e:
        print(e)
        print(f'ERROR!\nCould not write to config location "{file_path}"!')
        raise SystemExit(1)


def read_toml_file(file_path):
    import tomllib
    try:
        with open(file_path, "rb") as f:
            return tomllib.load(f)
    except Exception as e:
        print(e)
        print(f'ERROR!\nCould not read from config location "{file_path}"!')
        raise SystemExit(1)


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
