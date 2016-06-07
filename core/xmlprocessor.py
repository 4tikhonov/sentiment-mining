#!/usr/bin/python

import xml.etree.ElementTree
import urllib
import re
 
def make_dict_from_tree(element_tree):
    """Traverse the given XML element tree to convert it into a dictionary.
 
    :param element_tree: An XML element tree
    :type element_tree: xml.etree.ElementTree
    :rtype: dict
    """
    def internal_iter(tree, accum):
        """Recursively iterate through the elements of the tree accumulating
        a dictionary result.
 
        :param tree: The XML element tree
        :type tree: xml.etree.ElementTree
        :param accum: Dictionary into which data is accumulated
        :type accum: dict
        :rtype: dict
        """
        if tree is None:
            return accum
 
        if tree.getchildren():
            accum[tree.tag] = {}
            for each in tree.getchildren():
                result = internal_iter(each, {})
                if each.tag in accum[tree.tag]:
                    if not isinstance(accum[tree.tag][each.tag], list):
                        accum[tree.tag][each.tag] = [
                            accum[tree.tag][each.tag]
                        ]
                    accum[tree.tag][each.tag].append(result[each.tag])
                else:
                    accum[tree.tag].update(result)
        else:
            accum[tree.tag] = tree.text
 
        return accum
 
    return internal_iter(element_tree, {})
 
def request_xml(url):
    page = urllib.urlopen(url)
    xml_string = page.read()
    return xml_string

def convertrecords(items):
    records = {}
    result = []
    for item in items:
        for name in items[item]:
	    if name == '{http://www.loc.gov/zing/srw/}records':
		for record in items[item][name]:
		    records = items[item][name][record]
		    for row in records:
			for token in row: # == '{http://www.loc.gov/zing/srw/}recordData':
			    if token == '{http://www.loc.gov/zing/srw/}recordData':
				#print row[token]
				data = {}
				for nameitem in row[token]:
			            clearname = re.sub(r'\{.+?\}', '', nameitem)
				    #print "%s %s" % (clearname, row[token][nameitem])
				    data[clearname] = row[token][nameitem]
			        result.append(data)
    return result


