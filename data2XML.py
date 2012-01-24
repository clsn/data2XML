#!/usr/bin/env python

# Goal: an XML format that's easy to write as a data structure in Python
# (or in JSON/YAML?)
# Motivation: Crafting XML strings by hand is just asking for a missed
# slash or close-tag.  Building big structures laboriously using DOM is
# big and laborious.  Python has a reasonable syntax for dictionary
# and list literals which can be used for the purpose.
# Limitations: doesn't have to be perfect.

# But this looks pretty good!


from xml.dom.minidom import getDOMImplementation
impl=getDOMImplementation()

def handleContent(content, doc):
    # Content coming in will look like:
    # Case 1: text.  Return a text node containing this text.
    # Case 2: A dictionary.  use data2XML to get the element for that.
    # Case 3: An array. Return an array of what you get from
    # applying handleContent recursively.
    if content is None:
        return None
    if isinstance(content, basestring):
        return doc.createTextNode(content)
    if isinstance(content, dict):
        return data2XML(content,doc)
    if isinstance(content, list):
        return [handleContent(x, doc) for x in content]
    else:
        raise Exception("handleContent: Unknown type %s"%str(type(content)))

def data2XML(data, doc=None):
    # OK.  Let's go through cases.
    # Data comes in as a dictionary.
    # Dictionary should have at most ONE element.
    # Return a DOM element with tag=dictionary's lone key,
    # and contents=handleContent of the value of the key.
    # UNLESS the value is a dictionary containing '__attrs__'
    # and '__content__', in which case put the attrs into
    # the element's attributes and pass the value of
    # __content__ to the handleContent routine.
    #
    # If handleContent returns an array, the elements of that array
    # are the children of this node.

    if not isinstance(data, dict):
        raise Exception("data2XML: Not a dictionary.")
    if len(data.keys())==1:
        # Normal case
        tag=data.keys()[0]
        value=data[tag]
        if not doc:
            # We're at the top level
            doc=impl.createDocument(None, tag, None)
            rv=doc.documentElement
        else:
            rv=doc.createElement(tag)
        if isinstance(value, dict):
            # __attr__/__content__ case
            content=handleContent(value['__content__'], doc)
            attrs=value['__attrs__']
            for k, v in attrs.iteritems():
                rv.setAttribute(k,v)
        else:
            content=handleContent(value, doc)
        if isinstance(content, list):
            for elt in content:
                rv.appendChild(elt)
        elif content:
            rv.appendChild(content)
    else:
        raise Exception("data2XML: too many keys %d."%len(data.keys()))
    return rv


if __name__=='__main__':
    data={
        "response": [
            { "field1": "foo"} ,
            { "field2": [
                    {"subfield": "text"},
                    {"subfield2": "text"},
                    ]},
            { "field3": [
                    "Some text",
                    {"subfield": "subtext"},
                    "some more text"
                    ]},
            { "field3": {
                    '__attrs__': {
                        "id": "foo",
                        "endian": "big",
                        },
                    '__content__': [
                        # Actual content if any goes here.
                        # need a wrapper in case it's text or whatever.
                        { "foo": "bar"},
                        { "baz": "quux"},
                        ]
                    }
              },
            { "field4": {
                    '__attrs__': {
                        "id": "somethingorother",
                        },
                    '__content__': "text"
                    # Or an array of subelements.
                    }
              }
            ]
        }
    doc=data2XML(data, None)
    print doc.toprettyxml()

