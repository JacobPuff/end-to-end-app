# -*- coding: utf-8 -*-
"""
This file contains utility functions for use in the Pyramid view handling
"""

import csv
import cStringIO
import hashlib
from os.path import exists
import datetime
from sqlalchemy.ext.declarative import declarative_base


def error_dict(error_type='generic_errors', errors=''):
    """
    Create a basic error dictionary for standard use with the intent of being passed to some other outside
    API or whatnot.
    :param type: A plural string without spaces that describes the errors.  Only one type of error should be sent.
    :param errors: A list of error strings describing the problems. A single string will be converted to a single item
    list containing that string.
    :return: A dictionary for the error to be passed.
    """
    if isinstance(errors, basestring):
        errors = [errors]
    if not isinstance(errors, list):
        raise TypeError('Type for "errors" must be a string or list of strings')
    if not all(isinstance(item, basestring) for item in errors):
        raise TypeError('Type for "errors" in the list must be a string')
    error = {'error_type': error_type,
             'errors': errors,
             }
    return error


def hash_password(password, salt):
    """
    Hashes a password with the sale and returns the hash
    :param password: a password string
    :type password: basestring
    :param salt: a salt hash
    :type salt: assumed to be bytes
    :return: a password digest, NOT a hex digest string
    """
    m = hashlib.sha512()
    m.update(password.encode('utf-8'))
    m.update(salt)
    return m.digest()


format_datetime = lambda timez, dt : timez.localize(dt).strftime("%Y-%m-%d %H:%M:%S")


def lists_to_csv_memory(data, header=None, delimiter=','):
    """
    Creates and returns an in-memory "file" of csv parsed data
    :param data: a list of lists to write to CSV.  None parsed to '', and if a header is provided, only the
    first N items are added to the csv, where N is the length of the header list.
    :param header: An optional header list (must be less than or equal to length of data items)
    :param delimiter: Optional passthrough of delimiting character
    :return: A CSV datablock string in memory.
    """
    cstring = cStringIO.StringIO()
    writer = csv.writer(cstring, dialect='excel', delimiter=delimiter, lineterminator='\n')
    items_len = 0
    if header:
        items_len = len(header)
        writer.writerow(header)
    for x in data:
        if len(x) < items_len:
            raise ValueError('Not enough items in all rows of data')
    writer.writerows(data)
    retval = cstring.getvalue()
    cstring.truncate()
    return retval


def get_all_lines_tsv(filename=None, read_headers=False):
    """
    Get all the lines from a tsv by filename, ignoring lines beginning with #
    :param filename: A string of the name of a tsv file
    :param read_headers: boolean indicating if a header should be read first
    :return: A dictionary containing "headers" as a list of strings, and "values" containing a list of lists of values
    """
    if not isinstance(filename, basestring):
        raise ValueError('Invalid value for filename: %s' % str(type(filename)))
    if not exists(filename):
        raise ValueError('File %s does not exist!' % filename)

    retval = {'headers': None,
              'values': []}
    with open(filename, 'r') as tsv_file:
        reader = csv.reader(tsv_file, delimiter='\t')
        row_strip = lambda a: [x.strip() for x in a]
        for line in reader:
            if len(line) > 0 and not line[0].strip().startswith('#') and not line[0].strip() == '':
                if read_headers:
                    retval['headers'] = row_strip(line)
                    read_headers = False
                    continue
                retval['values'].append(row_strip(line))

    return retval


def date_serializer(the_date, request):
    if isinstance(the_date, datetime.date):
        return str(the_date.isoformat())
    raise TypeError('Can not determine rendering for data given')


def time_serializer(the_time, request):
    if isinstance(the_time, datetime.time):
        return str(the_time.isoformat())
    raise TypeError('Can not determine rendering for data given')


def make_set_of_field_names(field_names=None):
    """

    :param field_names:
    :return:
    """
    if field_names:
        field_names = [field_names] if not isinstance(field_names, list) else field_names
        if not all(isinstance(x, basestring) for x in field_names):
            # We don't care if it's a Column or an InstrumentedAttribute or whatever, so long as we get a key from it
            if not all(hasattr(x, 'key') for x in field_names):
                raise ValueError('not all fields are strings or have names')
            # Make everything a string instead of a column, just to make things simpler
            field_names = [x.key if hasattr(x, 'key') else x for x in field_names]
        return field_names
    else:
        return []


def dict_from_row(row, remove_fields=None, sub_values=None):
    """
    Pyramid is not aware of the model classes used for our database structures, and it should not be, so
    this function translates between an arbitrary class and a dictionary of field: value pairs for passing
    to a pyramid template, typically for rendering to JSON rather than HTML.  It should not always be necessary
    unless the class over that area of responsibility is not built expressly for pyramid consumption.
    :param row: A class, typically returned as a row from a query, but not a "ResultRow" object
    :param remove_fields: A list of fields, by string or sqlalchemy object attribute, to remove from the returned dict
    :param sub_values: A list of fields to be further loaded into the return dict, only if present as column names
    :return: A dictionary representation of all the non-private attributes of the row given
    """
    retdict = {}
    remove_fields = make_set_of_field_names(remove_fields)
    sub_values = make_set_of_field_names(sub_values)

    for public_key in [i.name for i in row.__table__.columns if i.name not in remove_fields]:
        value = getattr(row, public_key)
        if value is not None:
            retdict[public_key] = value
        else:
            retdict[public_key] = None
    for key in [i for i in sub_values if hasattr(row, i)]:
        sub = getattr(row, key)
        # This used to be the way it was, but Tod didn't know why it would be a list but also a dict
        # if isinstance(sub, list) and not isinstance(sub, dict):
        if isinstance(sub, list):
            retdict[key] = [dict_from_row(i, remove_fields=remove_fields) for i in sub if i not in remove_fields]
        else:
            retdict[key] = sub._to_dict()
    return retdict


def array_of_dicts_from_map(map, remove_fields=None, sub_values=None):
    """
    Helper function for processing an entire resultset from some sqlalchemy object queries, assuming
    :param map: The resultset
    :param remove_fields: A list of fields, by string or sqlalchemy object attribute, to remove from the returned dict
    :param sub_values: A list of fields, by string or sqlalchemy object attribute, to get sub_values for on each object
    :return: An array of dictionaries as rendered one at a time from the function appropriate
    """
    # It's faster to do this once ahead of the dataset instead of redoing it every call
    remove_fields = make_set_of_field_names(remove_fields)
    sub_values = make_set_of_field_names(sub_values)
    return [x if not isinstance(x, declarative_base())
            else dict_from_row(x, remove_fields, sub_values)
            for x in map.values()]


def array_of_dicts_from_array_of_models(models, remove_fields=None, sub_values=None):
    """
    Helper function for processing an entire resultset from some sqlalchemy object queries
    :param models: The resultset
    :param remove_fields: A list of fields, by string or sqlalchemy object attribute, to remove from the returned dict
    :param sub_values: A list of fields, by string or sqlalchemy object attribute, to get sub_values for on each object
    :return: An array of dictionaries as rendered one at a time from the function appropriate
    """
    # It's faster to do this once ahead of the dataset instead of redoing it every call
    remove_fields = make_set_of_field_names(remove_fields)
    sub_values = make_set_of_field_names(sub_values)
    return [dict_from_row(x, remove_fields, sub_values) for x in models]


def array_of_dicts_from_array_of_keyed_tuples(keyed_tuples):
    """
    Helper function for processing an entire resultset of a query that touched multiple tables,
    resulting in a list of keyed tuples
    :param keyed_tuples: The resultset, as a list of keyed tuples
    :return: An array of dictionaries as rendered one at a time from the function appropriate
    """
    return [x._asdict() for x in keyed_tuples]


def sqlobj_from_dict(obj, values):
    """
    Merge in items in the values dict into our object if it's one of our columns.
    """
    for c in obj.__table__.columns:
        if c.name in values:
            setattr(obj, c.name, values[c.name])
    # This return isn't necessary as the obj referenced is modified, but it makes it more
    # complete and consistent
    return obj