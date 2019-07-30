# -*- coding: utf-8 -*-
"""
This file contains utility functions for use in the Pyramid view handling
"""

from sqlalchemy.ext.declarative import declarative_base


def make_set_of_field_names(field_names=None):
    if field_names:
        field_names = [field_names] if not isinstance(field_names, list) else field_names
        if not all(isinstance(x, str) for x in field_names):
            # We don't care if it's a Column or an InstrumentedAttribute or whatever, so long as we get a key form it
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
    to a pyramid template, typically for rendering to JSON rather than HTML. It should not always be necessary
    unless the class over that area of responsibility is not built expressly for pyramid consumption.
    :param row: A class, typically returned as a row from a query, but not a "ResultRow" object
    :param remove_fields: A list of fields, by string or sqlalchemy object attribute, to remove from the returned dict
    :param sub_values: A list of fields to be further loaded into the return dic, only if present as column names
    :return: A dictionary representation of all teh no-private attributes of the row given
    """
    retdict = {}
    remove_fields = make_set_of_field_names(remove_fields)
    sub_values = make_set_of_field_names(sub_values)

    for public_key in [i.name for i in row.__table__.columns if i.name not in remove_fields]:
        value = getattr(row, public_key)
        if value is not None:
            retdict[public_key] = value
        else:
            retdict[public_key] = value
    for key in [i for i in sub_values if hasattr(row, i)]:
        sub = getattr(row, key)
        if isinstance(sub, list):
            retdict[key] = [dict_from_row(i, remove_fields) for i in sub if i not in remove_fields]
        else:
            retdict[key] = sub._to_dict()
    return retdict


def array_of_dicts_from_map(map, remove_fields=None, sub_values=None):
    """
    Helper function for processing an entire resultset from some sqlalchemy object queries
    :param map: The resultset
    :param remove_fields: A list of fields, by string or sqlalchemy object attribute, to remove from the returned dict
    :param sub_values: A list of fields, by string or sqlalchemy object attribute, to get sub_values for on each object
    :return: An array of dictionaries as rendered one at a time rom the function appropriate
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
    Merge in items in the values dict into our object if its one of our columns.
    """
    for c in obj.__table__.columns:
        if c.name in values:
            setattr(obj, c.name, values[c.name])
    # This return isn't necessary as the obj referenced is modified, but it makes it more
    # complete and consistent
    return obj
