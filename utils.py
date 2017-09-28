import codecs
import json


def read_file(file_path, mode='r'):
    """Generic function to read from a file"""
    with codecs.open(file_path, mode) as fp:
        return fp.read().strip()


def write_file(content, file_path, mode='w'):
    """Generic function to write to a file"""
    with codecs.open(file_path, mode) as fid:
        fid.write(content)


def write_json(content, file_path, mode='w'):
    """Generic function to write JSON to a file"""
    with codecs.open(file_path, mode) as fid:
        json.dump(content, fid)


def read_json(file_path, mode='r'):
    """Generic function to write JSON to a file"""
    file = read_file(file_path)
    return json.loads(file)
