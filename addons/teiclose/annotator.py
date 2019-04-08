# -*- coding: utf-8 -*-
import re
import os
from lxml import etree
import xml.dom.minidom

from osf.models import (
    Guid,
    OSFUser
)


class Annotator:
    def __init__(self):
        self.text = ""
        self.tags = {}
        self.json = {}

        self.beginning = 0
        self.end = 0

        self.annotated_fragment = ""
        self.certainties = []
        self.certainty_to_add = None

        self.annotators_ids = []
        self.annotator_to_add = None

        self.first_free_certainty_id = 0
        self.annotation_ids = []

        self.list_of_inside_tags = []
        self.user_xml_id = ""

    def add_annotation(self, text, json, user_id):
        self.text = text
        self.json = json

        self.user_xml_id = 'person' + user_id

        # WYCIĄGANIE INFORMACJI Z XML-A
        self.beginning, self.end = self.convert_rows_and_columns_to_absolute_begin_and_end(self.text,
                                                                                           self.json["start_row"],
                                                                                           self.json["start_col"],
                                                                                           self.json["end_row"],
                                                                                           self.json["end_col"])

        # print "SELECTED FRAGMENT:", self.text[self.beginning:self.end]

        self.beginning, self.end = self.get_string_position_with_closest_matching_tags(self.text, self.beginning,
                                                                                       self.end)

        self.annotated_fragment = self.text[self.beginning: self.end]
        # print "Fragment: ", self.annotated_fragment

        self.tags = self.get_outer_tags_from_annotated_fragment(self.annotated_fragment)
        # print "Tags: ", self.tags

        self.certainties = self.get_certainties_from_file(self.text)
        self.annotators_ids = self.get_annotators_GUID_from_file(self.text)
        # self.get_annotators_GUID_from_file(self.text)
        self.first_free_certainty_id = self.get_first_free_certainty_number(self.certainties, self.json["tag"])
        # print self.first_free_certainty_id

        # PRZYGOTOWANIE INFORMACJI DO ZŁOŻENIA NOWEGO XML-A

        # self.list_of_inside_tags = self.reduce_inside_tags(self.list_of_inside_tags)


        # 1
        if not self.tags and self.json['tag'] and not self.json['certainty']:
            new_fragment, self.annotation_ids = self.add_tag(self.annotated_fragment, self.json["tag"])

        # 2
        elif not self.tags and not self.json['tag'] and self.json['certainty']:
            new_fragment, self.annotation_ids = self.add_tag(self.annotated_fragment, self.json["tag"], self.json['certainty'])

            self.certainty_to_add = self.create_certainty_description(self.json, self.annotation_ids, self.user_xml_id)
            self.annotator_to_add = self.create_annotator(self.user_xml_id)

        # 3
        elif not self.tags and self.json['tag'] and self.json['certainty']:
            new_fragment, self.annotation_ids = self.add_tag(self.annotated_fragment, self.json["tag"], self.json['certainty'])

            self.certainty_to_add = self.create_certainty_description(self.json, self.annotation_ids, self.user_xml_id)
            self.annotator_to_add = self.create_annotator(self.user_xml_id)

        # 4
        elif self.tags and self.json['tag'] and self.json['tag'] not in self.tags and not self.json['certainty']:
            new_fragment, self.annotation_ids = self.add_tag(self.annotated_fragment, self.json["tag"])

        # 5
        elif self.tags and self.json['tag'] and self.json['tag'] in self.tags and 'xml:id' not in self.tags[self.json['tag']] and not self.json['certainty']:
            new_fragment, self.annotation_ids = self.add_tag(self.annotated_fragment, self.json["tag"],
                                                             self.json['certainty'])

            new_json = {
                "source": "imprecision",
                "locus": "name",
                "certainty": "unknown",
                "asserted_value": "",
                "description": "",
                "tag": "place"
            }

            self.certainty_to_add = self.create_certainty_description(new_json, self.annotation_ids, self.user_xml_id)
            self.annotator_to_add = self.create_annotator(self.user_xml_id)

        # 6
        elif self.tags and self.json['tag'] and self.json['tag'] in self.tags and 'xml:id' not in self.tags[self.json['tag']] and self.json['certainty']:
            new_fragment, self.annotation_ids = self.add_tag(self.annotated_fragment, self.json["tag"], self.json['certainty'])

            self.certainty_to_add = self.create_certainty_description(self.json, self.annotation_ids, self.user_xml_id)
            self.annotator_to_add = self.create_annotator(self.user_xml_id)

        # 7
        elif self.tags and not self.json['tag'] and self.json['certainty']:
            new_fragment, self.annotation_ids = self.add_tag(self.annotated_fragment, self.json["tag"], self.json['certainty'])

            self.certainty_to_add = self.create_certainty_description(self.json, self.annotation_ids, self.user_xml_id)
            self.annotator_to_add = self.create_annotator(self.user_xml_id)

        # 8
        elif self.tags and self.json['tag'] and self.json['tag'] not in self.tags and self.json['certainty']:
            new_fragment, self.annotation_ids = self.add_tag(self.annotated_fragment, self.json["tag"],
                                                             self.json['certainty'])

            self.certainty_to_add = self.create_certainty_description(self.json, self.annotation_ids, self.user_xml_id)
            self.annotator_to_add = self.create_annotator(self.user_xml_id)

        # 9
        elif self.tags and not self.tags[self.json['tag']] and not self.json['certainty']:
            new_fragment = self.annotated_fragment
            self.annotation_ids.append('#' + self.tags[self.json['tag']]['xml:id'])

            self.certainty_to_add = self.create_certainty_description(self.json, self.annotation_ids, self.user_xml_id)
            self.annotator_to_add = self.create_annotator(self.user_xml_id)

        # 10
        elif self.tags and self.tags[self.json['tag']] and self.tags[self.json['tag']]['xml:id'] is not None and self.json['certainty']:
            new_fragment = self.annotated_fragment
            self.annotation_ids.append('#' + self.tags[self.json['tag']]['xml:id'])

            self.certainty_to_add = self.create_certainty_description(self.json, self.annotation_ids, self.user_xml_id)
            self.annotator_to_add = self.create_annotator(self.user_xml_id)








        # ZŁOŻENIE NOWEGO XML-A

        text_new = self.add_tagged_string(new_fragment)

        if self.user_xml_id not in self.annotators_ids and self.annotator_to_add is not None:
            text_new = self.add_annotator(text_new, self.annotator_to_add)

        if self.certainty_to_add is not None:
            text_new = self.add_certainty(text_new, self.certainty_to_add)



        # sformatowanie XML-a

        text_to_return = self.reformat_xml(text_new)

        return text_to_return

    # def get_user_guid(self):
    #     return 'fill_this_method'


    def reformat_xml(self, text):
        new_xml_in_lines = text.splitlines()
        if 'encoding=' in new_xml_in_lines[0]:
            text_to_parse = '\n'.join(new_xml_in_lines[1:])
        else:
            text_to_parse = text

        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.fromstring(text_to_parse, parser=parser)
        pretty_xml_etree = etree.tostring(tree, pretty_print=True, encoding="utf-8")

        if 'encoding=' in new_xml_in_lines[0]:
            pretty_xml_etree = '\n'.join((new_xml_in_lines[0], pretty_xml_etree))
        else:
            pretty_xml_etree = pretty_xml_etree

        return pretty_xml_etree


    def add_certainty(self, text, certainty):

        new_xml_in_lines = text.splitlines()
        if 'encoding=' in new_xml_in_lines[0]:
            text_to_parse = '\n'.join(new_xml_in_lines[1:])
        else:
            text_to_parse = text

        tree = etree.fromstring(text_to_parse)

        namespaces = {
            'default': 'http://www.tei-c.org/ns/1.0',
        }

        certainties = tree.xpath('//default:teiHeader'
                                 '//default:classCode[@scheme="http://providedh.eu/uncertainty/ns/1.0"]',
                                 namespaces=namespaces)

        if not certainties:
            tree = self.create_annotation_list(tree)
            certainties = tree.xpath('//default:teiHeader'
                                     '//default:classCode[@scheme="http://providedh.eu/uncertainty/ns/1.0"]',
                                     namespaces=namespaces)

        certainties[0].append(certainty)

        text = etree.tostring(tree, encoding="utf-8")

        if 'encoding=' in new_xml_in_lines[0]:
            text_to_return = '\n'.join((new_xml_in_lines[0], text))
        else:
            text_to_return = text

        return text_to_return





    def add_tagged_string(self, new_fragment):
        new_xml = self.text[:self.beginning] + new_fragment + self.text[self.end:]

        return new_xml

    def add_annotator(self, text, annotator):

        new_xml_in_lines = text.splitlines()
        if 'encoding=' in new_xml_in_lines[0]:
            text_to_parse = '\n'.join(new_xml_in_lines[1:])
        else:
            text_to_parse = text

        tree = etree.fromstring(text_to_parse)

        namespaces = {
            'default': 'http://www.tei-c.org/ns/1.0',
        }

        list_person = tree.xpath('//default:teiHeader'
                                 '//default:listPerson[@type="PROVIDEDH Annotators"]', namespaces=namespaces)

        # jesli nie ma listy annotatorów, to ją stwórz
        if not list_person:
            tree = self.create_list_person(tree)
            list_person = tree.xpath('//default:teiHeader'
                                     '//default:listPerson[@type="PROVIDEDH Annotators"]', namespaces=namespaces)

        list_person[0].append(annotator)

        text = etree.tostring(tree, encoding="utf-8")

        if 'encoding=' in new_xml_in_lines[0]:
            text_to_return = '\n'.join((new_xml_in_lines[0], text))
        else:
            text_to_return = text

        # dom = xml.dom.minidom.parseString(text_to_return)
        # pretty_xml_minidom = dom.toprettyxml(indent='  ')
        #
        #
        #
        # parser = etree.XMLParser(remove_blank_text=True)
        # tree = etree.fromstring(text_to_return, parser=parser)
        # pretty_xml_etree = etree.tostring(tree, pretty_print=True)

        return text_to_return


    def create_list_person(self, tree):

        namespaces = {
            'default': 'http://www.tei-c.org/ns/1.0',
        }

        default_namespace = "http://www.tei-c.org/ns/1.0"
        default = "{%s}" % default_namespace

        ns_map = {
            None: default_namespace
        }  # the default namespace (no prefix)

        profile_desc = tree.xpath('//default:teiHeader/default:profileDesc', namespaces=namespaces)

        if not profile_desc:
            tei_header = tree.xpath('//default:teiHeader', namespaces=namespaces)
            profile_desc = etree.Element(default + 'profileDesc', nsmap=ns_map)
            tei_header[0].append(profile_desc)

        partic_desc = tree.xpath('//default:teiHeader/default:profileDesc/default:particDesc', namespaces=namespaces)

        if not partic_desc:
            profile_desc = tree.xpath('//default:teiHeader/default:profileDesc', namespaces=namespaces)
            partic_desc = etree.Element(default + 'particDesc', nsmap=ns_map)
            profile_desc[0].append(partic_desc)

        # print etree.tostring(tree)

        list_person = tree.xpath('//default:teiHeader/default:profileDesc/default:particDesc/default:listPerson',
                                 namespaces=namespaces)

        if not list_person:
            partic_desc = tree.xpath('//default:teiHeader/default:profileDesc/default:particDesc', namespaces=namespaces)
            list_person = etree.Element(default + 'listPerson', type="PROVIDEDH Annotators", nsmap=ns_map)
            partic_desc[0].append(list_person)

        return tree

    def create_annotation_list(self, tree):

        namespaces = {
            'default': 'http://www.tei-c.org/ns/1.0',
        }

        default_namespace = "http://www.tei-c.org/ns/1.0"
        default = "{%s}" % default_namespace

        ns_map = {
            None: default_namespace
        }  # the default namespace (no prefix)

        profile_desc = tree.xpath('//default:teiHeader/default:profileDesc', namespaces=namespaces)

        if not profile_desc:
            tei_header = tree.xpath('//default:teiHeader', namespaces=namespaces)
            profile_desc = etree.Element(default + 'profileDesc', nsmap=ns_map)
            tei_header[0].append(profile_desc)

        text_class = tree.xpath('//default:teiHeader/default:profileDesc/default:textClass', namespaces=namespaces)

        if not text_class:
            profile_desc = tree.xpath('//default:teiHeader/default:profileDesc', namespaces=namespaces)
            text_class = etree.Element(default + 'textClass', nsmap=ns_map)
            profile_desc[0].append(text_class)

        class_code = tree.xpath('//default:teiHeader/default:profileDesc/default:textClass/default:classCode', namespaces=namespaces)

        if not class_code:
            text_class = tree.xpath('//default:teiHeader/default:profileDesc/default:textClass', namespaces=namespaces)
            class_code = etree.Element(default + 'classCode', scheme="http://providedh.eu/uncertainty/ns/1.0", nsmap=ns_map)
            text_class[0].append(class_code)

        return tree



    def create_annotator(self, user_xml_id):
        user_guid = user_xml_id.replace('person', '')

        annotator_data = self.get_user_data_from_db(user_guid)

        annotator = """
            <person xml:id="{0}">
              <persName>
                <forename>{1}</forename>
                <surname>{2}</surname>
                <email>{3}</email>
                <profile>{4}</profile>
              </persName>
            </person>
        """.format(user_xml_id, annotator_data['forename'], annotator_data['surname'], annotator_data['email'],
                   annotator_data['profile'])

        annotator_xml = etree.fromstring(annotator)

        return annotator_xml


    def get_user_data_from_db(self, user_guid):
        guid = Guid.objects.get(_id=user_guid)
        osf_user = OSFUser.objects.get(id=guid.id)

        
        data = {
            'forename': osf_user.given_name,
            'surname': osf_user.family_name,
            'email': osf_user.username,
            'profile': 'https://providedh.ehum.psnc.pl/' + user_guid + '/',
        }

        return data

    def create_certainty_description(self, json, annotation_ids, user_uuid):
        target = " ".join(annotation_ids)
        # new_element = etree.Element("certainty", source=json["source"], locus=json["locus"], cert=json["certainty"],
        #                             resp=user_uuid, target=target)

        certainty = '<certainty source="{0}" locus="{1}" cert="{2}" resp="#{3}" target="{4}"/>'.format(json['source'],
                                                                                                       json['locus'],
                                                                                                       json['certainty'],
                                                                                                       user_uuid,
                                                                                                       target)

        new_element = etree.fromstring(certainty)

        if json["asserted_value"]:
            new_element.set('assertedValue', json["asserted_value"])

        if json["description"]:
            description = etree.Element("desc")
            description.text = json["description"]

            new_element.append(description)

        return new_element






    def get_first_free_certainty_number(self, certainties, tag):
        if not tag:
            tag = 'ab'

        biggest_number = 0

        for cert in certainties:
            id_value = cert.attrib['target']

            if tag not in id_value:
                continue

            id_value = id_value.strip()

            splitted_values = id_value.split(' ')
            for value in splitted_values:
                number = value.replace('#' + tag, '')
                number = int(number)

                if number > biggest_number:
                    biggest_number = number

        return biggest_number + 1


    # def add_tag(self, annotated_fragment, tag, uncertainty=None):
    #     if tag == '':
    #         tag = 'ab'
    #
    #     new_annotated_fragment = ''
    #
    #     annotation_ids = []
    #
    #     while len(annotated_fragment) > 0:
    #         # jeśli znajdzie tag jakikolwiek
    #         if re.search(r'^\s*?<[^<>]*?>', annotated_fragment):
    #             match = re.search(r'^\s*?<[^<>]*?>', annotated_fragment)
    #             tag_to_move = match.group()
    #
    #             new_annotated_fragment += tag_to_move
    #
    #             annotated_fragment = annotated_fragment[len(tag_to_move):]
    #
    #         # jeśli znajdzie tekst bez tagu
    #         else:
    #             match = re.search(r'^\s*[^<>]+', annotated_fragment)
    #             text_to_move = match.group()
    #
    #             attribute = ""
    #
    #             if uncertainty:
    #                 id = '{0}{1:06d}'.format(tag, self.first_free_certainty_id)
    #                 attribute = ' xml:id="{0}"'.format(id)
    #
    #                 annotation_ids.append('#' + id)
    #
    #             tag_open = '<{0}{1}>'.format(tag, attribute)
    #             tag_close = '</{0}>'.format(tag)
    #
    #             new_annotated_fragment += tag_open + text_to_move + tag_close
    #
    #             annotated_fragment = annotated_fragment[len(text_to_move):]
    #
    #             if uncertainty:
    #                 self.first_free_certainty_id += 1
    #
    #     return new_annotated_fragment, annotation_ids


    def add_tag(self, annotated_fragment, tag, uncertainty=None):
        if not tag:
            tag = 'ab'


        new_annotated_fragment = ''

        annotation_ids = []

        while len(annotated_fragment) > 0:
            if re.search(r'^\s*?<[^<>]*?>', annotated_fragment):
                match = re.search(r'^\s*?<[^<>]*?>', annotated_fragment)
                tag_to_move = match.group()

                if tag in tag_to_move and '/' + tag not in tag_to_move:
                    match = re.search(r'<[^>\s]+', tag_to_move)
                    tag_begin = match.group()

                    id = '{0}{1:06d}'.format(tag, self.first_free_certainty_id)
                    attribute = ' xml:id="{0}"'.format(id)

                    annotation_ids.append('#' + id)

                    new_tag_to_move = "{0}{1}{2}".format(tag_to_move[:len(tag_begin)], attribute,
                                                         tag_to_move[len(tag_begin):])

                    new_annotated_fragment += new_tag_to_move

                    self.first_free_certainty_id += 1

                else:
                    new_annotated_fragment += tag_to_move

                annotated_fragment = annotated_fragment[len(tag_to_move):]

            # jeśli znajdzie tekst bez tagu
            else:
                match = re.search(r'^\s*[^<>]+', annotated_fragment)
                text_to_move = match.group()

                if tag in self.tags:
                    new_annotated_fragment += text_to_move

                    annotated_fragment = annotated_fragment[len(text_to_move):]

                else:
                    attribute = ""

                    if uncertainty:
                        id = '{0}{1:06d}'.format(tag, self.first_free_certainty_id)
                        attribute = ' xml:id="{0}"'.format(id)

                        annotation_ids.append('#' + id)

                    tag_open = '<{0}{1}>'.format(tag, attribute)
                    tag_close = '</{0}>'.format(tag)

                    new_annotated_fragment += tag_open + text_to_move + tag_close

                    annotated_fragment = annotated_fragment[len(text_to_move):]

                    if uncertainty:
                        self.first_free_certainty_id += 1

        return new_annotated_fragment, annotation_ids



    def get_certainties_from_file(self, text):

        text_in_lines = text.splitlines()

        if 'encoding=' in text_in_lines[0]:
            text_to_parse = '\n'.join(text_in_lines[1:])
        else:
            text_to_parse = text

        tree = etree.fromstring(text_to_parse)

        namespaces = {
            'default': 'http://www.tei-c.org/ns/1.0',
        }

        certainties = tree.xpath('//default:teiHeader'
                                 '//default:classCode[@scheme="http://providedh.eu/uncertainty/ns/1.0"]'
                                 '/default:certainty', namespaces=namespaces)

        return certainties

    def get_annotators_from_file(self, text):
        text_in_lines = text.splitlines()

        if 'encoding=' in text_in_lines[0]:
            text_to_parse = '\n'.join(text_in_lines[1:])
        else:
            text_to_parse = text

        tree = etree.fromstring(text_to_parse)

        namespaces = {
            'default': 'http://www.tei-c.org/ns/1.0',
        }

        annotators = tree.xpath('//default:teiHeader'
                                '//default:listPerson[@type="PROVIDEDH Annotators"]'
                                '/default:person', namespaces=namespaces)

        return annotators

    def get_annotators_GUID_from_file(self, text):
        text_in_lines = text.splitlines()

        if 'encoding=' in text_in_lines[0]:
            text_to_parse = '\n'.join(text_in_lines[1:])
        else:
            text_to_parse = text

        tree = etree.fromstring(text_to_parse)

        namespaces = {
            'default': 'http://www.tei-c.org/ns/1.0',
            'xml': 'http://www.w3.org/XML/1998/namespace',
            'xi': 'http://www.w3.org/2001/XInclude',
        }

        annotators = tree.xpath('//default:teiHeader'
                                '//default:listPerson[@type="PROVIDEDH Annotators"]'
                                '/default:person', namespaces=namespaces)

        uuids = []
        for annotator in annotators:
            # print etree.tostring(annotator, pretty_print=True)
            #
            # print annotator.tag

            # name_element = annotator.xpath('default:persName', namespaces=namespaces)

            uuid = annotator.get('{' + namespaces['xml'] + '}id')

            uuids.append(uuid)

        return uuids


    def get_string_position_with_closest_matching_tags(self, string, begining, end):
        # tag_open = ""
        # tag_close = ""
        # tag_open_name = ""
        # tag_close_name = ""
        #
        # text_przed = string[:begining]
        # text_po = string[end:]
        #
        # # szuka tagu przed zaznaczonym tekstem
        # if re.search(r'<[^<>]*?>\s*?$', text_przed):
        #     matches = re.search(r'<[^<>]*?>\s*?$', text_przed)
        #     tag_open = matches.group()
        #
        # # szuka tagu po zaznaczonym tekście
        # if re.search(r'^\s*?<[^<>]*?>', text_po):
        #     match = re.search(r'^\s*?<[^<>]*?>', text_po)
        #     tag_close = match.group()
        #
        # # szuka tagów wewnątrz zaznaczonego tekstu
        # if re.search(r'<[^<>]*?>', string[begining:end]):
        #     tags_inside = re.findall(r'<[^<>]*?>', string[begining:end])
        #
        #     for tag in tags_inside:
        #         tag = tag.replace('<', '')
        #         tag = tag.replace('>', '')
        #
        #         self.list_of_inside_tags.append(tag)
        #
        # marks_to_remove = ['</', '<', '/>', '>']
        #
        # pure_open_tag = re.search(r'<.*?>', tag_open)
        # if pure_open_tag:
        #     tag_open_name = pure_open_tag.group()
        #
        # pure_close_tag = re.search(r'<.*?>', tag_close)
        # if pure_close_tag:
        #     tag_close_name = pure_close_tag.group()
        #
        # for char in marks_to_remove:
        #     tag_open_name = tag_open_name.replace(char, '')
        #     tag_close_name = tag_close_name.replace(char, '')
        #
        # tag_open_name = tag_open_name.split(' ', 1)[0]
        # tag_close_name = tag_close_name.split(' ', 1)[0]
        #
        # if tag_open_name == tag_close_name and tag_open_name == tag_close_name != '':
        #     return self.get_string_position_with_closest_matching_tags(string, begining - len(tag_open),
        #                                                           end + len(tag_close))
        #
        # # POCZĄTEK TESTU
        # elif '/' + tag_open_name in self.list_of_inside_tags:
        #     for i in xrange(len(self.list_of_inside_tags)):
        #         if '/' + tag_open_name == self.list_of_inside_tags[i]:
        #             del self.list_of_inside_tags[i]
        #             break
        #
        #     return self.get_string_position_with_closest_matching_tags(string, begining - len(tag_open), end)
        #
        # elif tag_close_name in self.list_of_inside_tags:
        #     for i in xrange(len(self.list_of_inside_tags) - 1, -1, -1):
        #         if tag_close_name == self.list_of_inside_tags[i]:
        #             del self.list_of_inside_tags[i]
        #             break
        #
        #     return self.get_string_position_with_closest_matching_tags(string, begining, end + len(tag_close))
        #
        # # KONIEC TESTU
        # else:
        #     return begining, end

        found_tag = True

        while found_tag:
            found_tag = False

            text_przed = string[:begining]
            text_po = string[end:]

            # szuka tagu przed zaznaczonym tekstem
            if re.search(r'<[^<>]*?>\s*?$', text_przed):
                matches = re.search(r'<[^<>]*?>\s*?$', text_przed)
                tag_open = matches.group()
                begining -= len(tag_open)
                found_tag = True

            # szuka tagu po zaznaczonym tekście
            if re.search(r'^\s*?<[^<>]*?>', text_po):
                match = re.search(r'^\s*?<[^<>]*?>', text_po)
                tag_close = match.group()
                end += len(tag_close)
                found_tag = True

        return begining, end






    def get_outer_tags_from_annotated_fragment(self, fragment):

        tags = {}

        while re.match(r'^\s*?<[^<>]*?>', fragment):
            match = re.findall(r'^\s*?<[^<>]*?>', fragment)

            tag_raw = match[0]
            tag = tag_raw.strip()

            tag_name = tag
            marks_to_remove = ['</', '<', '/>', '>']

            for mark in marks_to_remove:
                tag_name = tag_name.replace(mark, '')

            tag_name = tag_name.split(' ')[0]

            tag_to_add = {tag_name: {}}

            arguments = re.findall(r'[\w:]+=".*?"', tag)
            for argument in arguments:
                arg_name = re.search(r'[\w:]+="', argument)
                arg_name = arg_name.group()
                arg_name = arg_name.replace('="', '')

                arg_value = re.search(r'".*?"', argument)
                arg_value = arg_value.group()
                arg_value = arg_value.replace('"', '')

                tag_to_add[tag_name].update({arg_name: arg_value})

            tags.update(tag_to_add)
            fragment = fragment[len(tag_raw):]

        return tags

    def convert_rows_and_columns_to_absolute_begin_and_end(self, string, start_row, start_col, end_row, end_col):
        text_in_lines = string.splitlines(True)

        chars_to_beginning = 0
        chars_to_end = 0

        i = 0
        while i + 1 < start_row:
            chars_to_beginning += len(text_in_lines[i])
            i += 1

        chars_to_beginning += start_col - 1

        j = 0
        while j + 1 < end_row:
            chars_to_end += len(text_in_lines[j])
            j += 1

        chars_to_end += end_col

        return chars_to_beginning, chars_to_end












    def reduce_inside_tags(self, tags):
        need_next_iteration = True

        while need_next_iteration:
            need_next_iteration = False

            for i in xrange(len(tags) - 1):
                tag_1 = tags[i]
                tag_2 = tags[i + 1]

                if tags[i][-1] == '/':
                    del tags[i]
                    break

                if '/' + tag_1 == tag_2:
                    del tags[i+1]
                    del tags[i]

                    need_next_iteration = True
                    break

        return tags







def main():
    # json = {
    #     "start_row": 9,
    #     "start_col": 82,
    #     "end_row": 9,
    #     "end_col": 90,
    # }

    # json_withstats2 = {
    #     "start_row": 104,
    #     "start_col": 27,
    #     "end_row": 104,
    #     "end_col": 49,
    #     "tag": ""
    # }

    # json_withstats2 = {
    #     "start_row": 2,
    #     "start_col": 1,
    #     "end_row": 2,
    #     "end_col": 8,
    # }

    # 1.Goły tekst, dodaję goły tag
    json_1 = {
        "start_row": 105,
        "start_col": 1,
        "end_row": 105,
        "end_col": 9,
        "tag": "place",
        "certainty": "",
    }

    # 1.1.Goły tekst, dodaję goły tag, w tagu
    json_1_1 = {
        "start_row": 98,
        "start_col": 73,
        "end_row": 98,
        "end_col": 92,
        "tag": "name",
        "certainty": "",
    }

    # 1.2.Goły tekst, dodaję goły tag, rozdzielony tagiem
    json_1_2 = {
        "start_row": 98,
        "start_col": 49,
        "end_row": 98,
        "end_col": 81,
        "tag": "name",
        "certainty": "",
    }

    # 1.3.Goły tekst, dodaję goły tag, rozdzielony tagiem, w tagu
    json_1_3 = {
        "start_row": 98,
        "start_col": 302,
        "end_row": 98,
        "end_col": 342,
        "tag": "name",
        "certainty": "",
    }

    # 1.3.Goły tekst, dodaję goły tag, rozdzielony tagiem, w tagu
    json_1_4 = {
        "start_row": 98,
        "start_col": 296,
        "end_row": 98,
        "end_col": 335,
        "tag": "name",
        "certainty": "",
    }

    # 2.1.Goły tekst, dodaję niepewność bez tagu
    json_2_1 = {
        "start_row": 98,
        "start_col": 7,
        "end_row": 98,
        "end_col": 12,
        "source": "variability",
        "locus": "value",
        "certainty": "high",
        "asserted_value": "",
        "description": "",
        "tag": ""
    }

    # 2.2.Goły tekst, dodaję niepewność bez tagu, z opisem
    json_2_2 = {
        "start_row": 98,
        "start_col": 7,
        "end_row": 98,
        "end_col": 12,
        "source": "variability",
        "locus": "value",
        "certainty": "high",
        "asserted_value": "",
        "description": "testowy opis",
        "tag": ""
    }

    # 2.3.Goły tekst, dodaję niepewność bez tagu, z assert value
    json_2_3 = {
        "start_row": 98,
        "start_col": 7,
        "end_row": 98,
        "end_col": 12,
        "source": "variability",
        "locus": "value",
        "certainty": "high",
        "asserted_value": "lalala",
        "description": "",
        "tag": ""
    }

    # 98.Goły tekst, dodaję niepewność bez tagu, z assert value
    json_98 = {
        "start_row": 1,
        "start_col": 3,
        "end_row": 1,
        "end_col": 5,
        "source": "",
        "locus": "",
        "certainty": "",
        "asserted_value": "",
        "description": "",
        "tag": "test"
    }

    # 99.Goły tekst, dodaję niepewność bez tagu, z assert value
    json_99 = {
        "start_row": 217,
        "start_col": 7,
        "end_row": 217,
        "end_col": 11,
        "source": "",
        "locus": "",
        "certainty": "",
        "asserted_value": "",
        "description": "",
        "tag": "test"
    }

    json_100 = {
        "start_row": 217,
        "start_col": 7,
        "end_row": 217,
        "end_col": 11,
        "source": "ignorance",
        "locus": "value",
        "certainty": "high",
        "asserted_value": "",
        "description": "",
        "tag": ""
    }

    # with open('proba.xml', 'r') as file:
    #     text = file.read()

    with open('source_file.xml', 'r') as file:
        text = file.read()

    annotator = Annotator()
    result = annotator.add_annotation(text, json_100)

    print result

    with open('wynik.xml', 'w') as file:
        file.write(result)

if __name__ == '__main__':
    main()
