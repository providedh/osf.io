# -*- coding: utf-8 -*-
import re
from lxml import etree

from osf.models import Guid, OSFUser

NAMESPACES = {
    'default': 'http://www.tei-c.org/ns/1.0',
    'xml': 'http://www.w3.org/XML/1998/namespace',
    'xi': 'http://www.w3.org/2001/XInclude',
}


class Annotator:
    def __init__(self):
        self.__xml = ""
        self.__json = {}
        self.__annotator_xml_id = ""

        self.__start = 0
        self.__end = 0
        self.__fragment_to_annotate = ""
        self.__tags = {}
        self.__annotators_xml_ids = []
        self.__first_free_certainty_number = 0

        self.__fragment_annotated = ""
        self.__certainty_to_add = None
        self.__annotator_to_add = None

        self.__xml_annotated = ""

    def add_annotation(self, xml, json, annotator_guid):
        self.__xml = xml
        self.__annotator_xml_id = 'person' + annotator_guid

        self.__json = self.__validate_request(json)

        self.__get_data_from_xml()
        self.__prepare_xml_parts()
        self.__create_new_xml()

        return self.__xml_annotated

    def __validate_request(self, json):
        position_params_v1 = [
            'start_row',
            'start_col',
            'end_row',
            'end_col',
        ]

        position_params_v2 = [
            'start_pos',
            'end_pos',
        ]

        optional_params = [
            'source',
            'locus',
            'certainty',
            'asserted_value',
            'description',
            'tag'
        ]

        position_v1 = all(elements in json.keys() for elements in position_params_v1)
        position_v2 = all(elements in json.keys() for elements in position_params_v2)

        if not (position_v1 or position_v2):
            raise ValueError("No position arguments in request.")

        positions_to_check = position_params_v1 if position_v1 else position_params_v2

        for position in positions_to_check:
            if not isinstance(json[position], (int, long)):
                raise TypeError("Value of '{}' is not a integer.".format(position))

            if json[position] <= 0:
                raise ValueError("Value of '{}' must be a positive number.".format(position))

        validated_json = {}

        if position_v1:
            start, end = self.__get_fragment_position(self.__xml, json)

            validated_json.update({'start_pos': start, 'end_pos': end})
        else:
            validated_json.update({'start_pos': json['start_pos'], 'end_pos': json['end_pos']})

        if validated_json['start_pos'] >= validated_json['end_pos']:
            raise ValueError("Start position of annotating fragment is greater or equal to end position.")

        for param in optional_params:
            if param in json:
                validated_json.update({param: json[param]})
            else:
                validated_json.update({param: ''})

        return validated_json

    def __get_data_from_xml(self):
        self.__start, self.__end = self.__get_fragment_position(self.__xml, self.__json)

        if self.__start >= self.__end:
            raise ValueError("Start position of annotating fragment is greater or equal to end position.")

        self.__start, self.__end = self.__get_fragment_position_with_adhering_tags(self.__xml, self.__start, self.__end)
        self.__fragment_to_annotate = self.__xml[self.__start: self.__end]

        self.__tags = self.__get_adhering_tags_from_annotated_fragment(self.__fragment_to_annotate)
        self.__annotators_xml_ids = self.__get_annotators_xml_ids_from_file(self.__xml)
        certainties = self.__get_certainties_from_file(self.__xml)
        self.__first_free_certainty_number = self.__get_first_free_certainty_number(certainties, self.__json["tag"])

    def __get_fragment_position(self, xml, json):
        if 'start_pos' in json and json['start_pos'] is not None and 'end_pos' in json and json['end_pos'] is not None:
            start = json['start_pos']
            end = json['end_pos']

        else:
            start, end = self.__convert_rows_and_cols_to_start_and_end(xml, json["start_row"], json["start_col"],
                                                                       json["end_row"], json["end_col"])

        return start, end

    def __convert_rows_and_cols_to_start_and_end(self, text, start_row, start_col, end_row, end_col):
        text_in_lines = text.splitlines(True)

        chars_to_start = 0
        chars_to_end = 0

        i = 0
        while i + 1 < start_row:
            chars_to_start += len(text_in_lines[i])
            i += 1

        chars_to_start += start_col - 1

        j = 0
        while j + 1 < end_row:
            chars_to_end += len(text_in_lines[j])
            j += 1

        chars_to_end += end_col

        return chars_to_start, chars_to_end

    def __get_fragment_position_with_adhering_tags(self, string, start, end):
        found_tag = True

        while found_tag:
            found_tag = False

            text_before = string[:start]
            text_after = string[end:]

            if re.search(r'<[^<>]*?>\s*?$', text_before):
                match = re.search(r'<[^<>]*?>\s*?$', text_before)
                tag_open = match.group()
                start -= len(tag_open)
                found_tag = True

            if re.search(r'^\s*?<[^<>]*?>', text_after):
                match = re.search(r'^\s*?<[^<>]*?>', text_after)
                tag_close = match.group()
                end += len(tag_close)
                found_tag = True

        return start, end

    def __get_adhering_tags_from_annotated_fragment(self, fragment):
        tags = {}

        while re.search(r'^\s*?<[^<>]*?>', fragment):
            match = re.search(r'^\s*?<[^<>]*?>', fragment)

            tag_raw = match.group()
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

    def __get_certainties_from_file(self, text):
        text_in_lines = text.splitlines()

        if 'encoding=' in text_in_lines[0]:
            text_to_parse = '\n'.join(text_in_lines[1:])
        else:
            text_to_parse = text

        tree = etree.fromstring(text_to_parse)

        certainties = tree.xpath('//default:teiHeader'
                                 '//default:classCode[@scheme="http://providedh.eu/uncertainty/ns/1.0"]'
                                 '/default:certainty', namespaces=NAMESPACES)

        return certainties

    def __get_annotators_xml_ids_from_file(self, text):
        text_in_lines = text.splitlines()

        if 'encoding=' in text_in_lines[0]:
            text_to_parse = '\n'.join(text_in_lines[1:])
        else:
            text_to_parse = text

        tree = etree.fromstring(text_to_parse)

        annotators = tree.xpath('//default:teiHeader'
                                '//default:listPerson[@type="PROVIDEDH Annotators"]'
                                '/default:person', namespaces=NAMESPACES)

        xml_ids = []
        for annotator in annotators:
            prefix = '{%s}' % NAMESPACES['xml']
            xml_id = annotator.get(prefix + 'id')

            xml_ids.append(xml_id)

        return xml_ids

    def __get_first_free_certainty_number(self, certainties, tag):
        if not tag:
            tag = 'ab'

        biggest_number = 0

        for certainty in certainties:
            id_value = certainty.attrib['target']

            if tag not in id_value:
                continue

            id_value = id_value.strip()

            split_values = id_value.split(' ')
            for value in split_values:
                number = value.replace('#' + tag, '')
                number = int(number)

                if number > biggest_number:
                    biggest_number = number

        return biggest_number + 1

    def __prepare_xml_parts(self):
        # 1. Add_tag to text (2.4.1 remark)
        if not self.__tags and self.__json['tag'] and not self.__json['certainty']:
            self.__fragment_annotated, annotation_ids = self.__add_tag(self.__fragment_to_annotate,
                                                                       self.__json["tag"])

        # 2. Add certainty to text (2.1)
        elif not self.__tags and not self.__json['tag'] and self.__json['certainty']:
            self.__fragment_annotated, annotation_ids = self.__add_tag(self.__fragment_to_annotate,
                                                                       self.__json["tag"],
                                                                       self.__json['certainty'])

            self.__certainty_to_add = self.__create_certainty_description(self.__json, annotation_ids,
                                                                          self.__annotator_xml_id)
            self.__annotator_to_add = self.__create_annotator(self.__annotator_xml_id)

        # 3. Add tag and certainty to text (2.4.1)
        elif not self.__tags and self.__json['tag'] and self.__json['certainty']:
            self.__fragment_annotated, annotation_ids = self.__add_tag(self.__fragment_to_annotate,
                                                                       self.__json["tag"],
                                                                       self.__json['certainty'])

            self.__certainty_to_add = self.__create_certainty_description(self.__json, annotation_ids,
                                                                          self.__annotator_xml_id)
            self.__annotator_to_add = self.__create_annotator(self.__annotator_xml_id)

        # 4. Add tag to text with tag
        # 9. Add tag to text with tag and certainty
        elif (self.__tags and self.__json['tag'] and self.__json['tag'] not in self.__tags and not
        self.__json['certainty']):
            self.__fragment_annotated, annotation_ids = self.__add_tag(self.__fragment_to_annotate,
                                                                       self.__json["tag"])

        # 5. Add tag to text with same tag (2.4.2 remark)
        elif self.__tags and self.__json['tag'] and self.__json['tag'] in self.__tags and \
                'xml:id' not in self.__tags[self.__json['tag']] and not self.__json['certainty']:
            self.__fragment_annotated, annotation_ids = self.__add_tag(self.__fragment_to_annotate,
                                                                       self.__json["tag"],
                                                                       self.__json['certainty'])

            new_json = {
                "source": "imprecision",
                "locus": "name",
                "certainty": "unknown",
                "asserted_value": "",
                "description": "",
                "tag": "place"
            }

            self.__certainty_to_add = self.__create_certainty_description(new_json, annotation_ids,
                                                                          self.__annotator_xml_id)
            self.__annotator_to_add = self.__create_annotator(self.__annotator_xml_id)

        # 6. Add certainty to text with same tag (2.2)
        elif self.__tags and self.__json['tag'] and self.__json['tag'] in self.__tags and \
                'xml:id' not in self.__tags[self.__json['tag']] and self.__json['certainty']:
            self.__fragment_annotated, annotation_ids = self.__add_tag(self.__fragment_to_annotate,
                                                                       self.__json["tag"],
                                                                       self.__json['certainty'])

            self.__certainty_to_add = self.__create_certainty_description(self.__json, annotation_ids,
                                                                          self.__annotator_xml_id)
            self.__annotator_to_add = self.__create_annotator(self.__annotator_xml_id)

        # 7. Add certainty to text with tag
        # 11. Add certainty to text with tag and certainty
        elif self.__tags and not self.__json['tag'] and self.__json['certainty']:
            self.__fragment_annotated, annotation_ids = self.__add_tag(self.__fragment_to_annotate,
                                                                       self.__json["tag"],
                                                                       self.__json['certainty'])

            self.__certainty_to_add = self.__create_certainty_description(self.__json, annotation_ids,
                                                                          self.__annotator_xml_id)
            self.__annotator_to_add = self.__create_annotator(self.__annotator_xml_id)

        # 8. Add tag and certainty to text with other tag
        # 12. Add tag and certainty to text with other tag and certainty
        elif self.__tags and self.__json['tag'] and self.__json['tag'] not in self.__tags and self.__json['certainty']:
            self.__fragment_annotated, annotation_ids = self.__add_tag(self.__fragment_to_annotate,
                                                                       self.__json["tag"],
                                                                       self.__json['certainty'])

            self.__certainty_to_add = self.__create_certainty_description(self.__json, annotation_ids,
                                                                          self.__annotator_xml_id)
            self.__annotator_to_add = self.__create_annotator(self.__annotator_xml_id)

        # 10. Add certainty to text with same tag and certainty (2.3)
        elif (self.__tags and self.__tags[self.__json['tag']] and
              self.__tags[self.__json['tag']]['xml:id'] is not None and self.__json['certainty']):
            self.__fragment_annotated = self.__fragment_to_annotate

            annotation_ids = list()
            annotation_ids.append('#' + self.__tags[self.__json['tag']]['xml:id'])

            self.__certainty_to_add = self.__create_certainty_description(self.__json, annotation_ids,
                                                                          self.__annotator_xml_id)
            self.__annotator_to_add = self.__create_annotator(self.__annotator_xml_id)

        else:
            raise ValueError("There is no method to modify xml according to given parameters.")

    def __add_tag(self, annotated_fragment, tag, uncertainty=None):
        if not tag:
            tag = 'ab'

        new_annotated_fragment = ''
        annotation_ids = []

        while len(annotated_fragment) > 0:
            # handle xml tag
            if re.search(r'^\s*?<[^<>]*?>', annotated_fragment):
                match = re.search(r'^\s*?<[^<>]*?>', annotated_fragment)
                tag_to_move = match.group()

                if tag in tag_to_move and '/' + tag not in tag_to_move:
                    match = re.search(r'<[^>\s]+', tag_to_move)
                    tag_begin = match.group()

                    id = '{0}{1:06d}'.format(tag, self.__first_free_certainty_number)
                    attribute = ' xml:id="{0}"'.format(id)

                    annotation_ids.append('#' + id)

                    new_tag_to_move = "{0}{1}{2}".format(tag_to_move[:len(tag_begin)], attribute,
                                                         tag_to_move[len(tag_begin):])

                    new_annotated_fragment += new_tag_to_move

                    self.__first_free_certainty_number += 1

                else:
                    new_annotated_fragment += tag_to_move

                annotated_fragment = annotated_fragment[len(tag_to_move):]

            # handle text
            else:
                match = re.search(r'^\s*[^<>]+', annotated_fragment)
                text_to_move = match.group()

                if tag in self.__tags:
                    new_annotated_fragment += text_to_move

                    annotated_fragment = annotated_fragment[len(text_to_move):]

                else:
                    attribute = ""

                    if uncertainty:
                        id = '{0}{1:06d}'.format(tag, self.__first_free_certainty_number)
                        attribute = ' xml:id="{0}"'.format(id)

                        annotation_ids.append('#' + id)

                    tag_open = '<{0}{1}>'.format(tag, attribute)
                    tag_close = '</{0}>'.format(tag)

                    new_annotated_fragment += tag_open + text_to_move + tag_close

                    annotated_fragment = annotated_fragment[len(text_to_move):]

                    if uncertainty:
                        self.__first_free_certainty_number += 1

        return new_annotated_fragment, annotation_ids

    def __create_certainty_description(self, json, annotation_ids, user_uuid):
        target = " ".join(annotation_ids)

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

    def __create_annotator(self, user_xml_id):
        user_guid = user_xml_id.replace('person', '')

        annotator_data = self.__get_user_data_from_db(user_guid)

        annotator = """
            <person xml:id="{0}">
              <persName>
                <forename>{1}</forename>
                <surname>{2}</surname>
                <email>{3}</email>
              </persName>
              <link>{4}</link>
            </person>
        """.format(user_xml_id, annotator_data['forename'], annotator_data['surname'], annotator_data['email'],
                   annotator_data['link'])

        annotator_xml = etree.fromstring(annotator)

        return annotator_xml

    def __get_user_data_from_db(self, user_guid):
        guid = Guid.objects.get(_id=user_guid)
        osf_user = OSFUser.objects.get(id=guid.id)

        data = {
            'forename': osf_user.given_name,
            'surname': osf_user.family_name,
            'email': osf_user.username,
            'link': 'https://providedh.ehum.psnc.pl/' + user_guid + '/',
        }

        return data

    def __create_new_xml(self):
        self.__xml_annotated = self.__add_tagged_string(self.__xml, self.__fragment_annotated)

        if self.__annotator_xml_id not in self.__annotators_xml_ids and self.__annotator_to_add is not None:
            self.__xml_annotated = self.__add_annotator(self.__xml_annotated, self.__annotator_to_add)

        if self.__certainty_to_add is not None:
            self.__xml_annotated = self.__add_certainty(self.__xml_annotated, self.__certainty_to_add)

        self.__xml_annotated = self.__reformat_xml(self.__xml_annotated)

    def __add_tagged_string(self, xml, new_fragment):
        new_xml = xml[:self.__start] + new_fragment + xml[self.__end:]

        return new_xml

    def __add_annotator(self, text, annotator):
        new_xml_in_lines = text.splitlines()
        if 'encoding=' in new_xml_in_lines[0]:
            text_to_parse = '\n'.join(new_xml_in_lines[1:])
        else:
            text_to_parse = text

        text_to_parse = text_to_parse.encode('utf-8')

        tree = etree.fromstring(text_to_parse)

        list_person = tree.xpath('//default:teiHeader'
                                 '//default:listPerson[@type="PROVIDEDH Annotators"]', namespaces=NAMESPACES)

        if not list_person:
            tree = self.__create_list_person(tree)
            list_person = tree.xpath('//default:teiHeader'
                                     '//default:listPerson[@type="PROVIDEDH Annotators"]', namespaces=NAMESPACES)

        list_person[0].append(annotator)

        text = etree.tostring(tree, encoding="utf-8")

        if 'encoding=' in new_xml_in_lines[0]:
            text_to_return = '\n'.join((new_xml_in_lines[0], text))
        else:
            text_to_return = text

        return text_to_return

    def __create_list_person(self, tree):
        prefix = "{%s}" % NAMESPACES['default']

        ns_map = {
            None: NAMESPACES['default']
        }

        profile_desc = tree.xpath('//default:teiHeader/default:profileDesc', namespaces=NAMESPACES)

        if not profile_desc:
            tei_header = tree.xpath('//default:teiHeader', namespaces=NAMESPACES)
            profile_desc = etree.Element(prefix + 'profileDesc', nsmap=ns_map)
            tei_header[0].append(profile_desc)

        partic_desc = tree.xpath('//default:teiHeader/default:profileDesc/default:particDesc', namespaces=NAMESPACES)

        if not partic_desc:
            profile_desc = tree.xpath('//default:teiHeader/default:profileDesc', namespaces=NAMESPACES)
            partic_desc = etree.Element(prefix + 'particDesc', nsmap=ns_map)
            profile_desc[0].append(partic_desc)

        list_person = tree.xpath('//default:teiHeader/default:profileDesc/default:particDesc/default:listPerson[@type="PROVIDEDH Annotators"]',
                                 namespaces=NAMESPACES)

        if not list_person:
            partic_desc = tree.xpath('//default:teiHeader/default:profileDesc/default:particDesc', namespaces=NAMESPACES)
            list_person = etree.Element(prefix + 'listPerson', type="PROVIDEDH Annotators", nsmap=ns_map)
            partic_desc[0].append(list_person)

        return tree

    def __add_certainty(self, text, certainty):
        new_xml_in_lines = text.splitlines()
        if 'encoding=' in new_xml_in_lines[0]:
            text_to_parse = '\n'.join(new_xml_in_lines[1:])
        else:
            text_to_parse = text

        text_to_parse = text_to_parse.encode('utf-8')

        tree = etree.fromstring(text_to_parse)

        certainties = tree.xpath('//default:teiHeader'
                                 '//default:classCode[@scheme="http://providedh.eu/uncertainty/ns/1.0"]',
                                 namespaces=NAMESPACES)

        if not certainties:
            tree = self.__create_annotation_list(tree)
            certainties = tree.xpath('//default:teiHeader'
                                     '//default:classCode[@scheme="http://providedh.eu/uncertainty/ns/1.0"]',
                                     namespaces=NAMESPACES)

        certainties[0].append(certainty)

        text = etree.tostring(tree, encoding="utf-8")

        if 'encoding=' in new_xml_in_lines[0]:
            text_to_return = '\n'.join((new_xml_in_lines[0], text))
        else:
            text_to_return = text

        return text_to_return

    def __create_annotation_list(self, tree):
        default_namespace = NAMESPACES['default']
        default = "{%s}" % default_namespace

        ns_map = {
            None: default_namespace
        }

        profile_desc = tree.xpath('//default:teiHeader/default:profileDesc', namespaces=NAMESPACES)

        if not profile_desc:
            tei_header = tree.xpath('//default:teiHeader', namespaces=NAMESPACES)
            profile_desc = etree.Element(default + 'profileDesc', nsmap=ns_map)
            tei_header[0].append(profile_desc)

        text_class = tree.xpath('//default:teiHeader/default:profileDesc/default:textClass', namespaces=NAMESPACES)

        if not text_class:
            profile_desc = tree.xpath('//default:teiHeader/default:profileDesc', namespaces=NAMESPACES)
            text_class = etree.Element(default + 'textClass', nsmap=ns_map)
            profile_desc[0].append(text_class)

        class_code = tree.xpath('//default:teiHeader/default:profileDesc/default:textClass/default:classCode',
                                namespaces=NAMESPACES)

        if not class_code:
            text_class = tree.xpath('//default:teiHeader/default:profileDesc/default:textClass', namespaces=NAMESPACES)
            class_code = etree.Element(default + 'classCode', scheme="http://providedh.eu/uncertainty/ns/1.0",
                                       nsmap=ns_map)
            text_class[0].append(class_code)

        return tree

    def __reformat_xml(self, text):
        new_xml_in_lines = text.splitlines()
        if 'encoding=' in new_xml_in_lines[0]:
            text_to_parse = '\n'.join(new_xml_in_lines[1:])
        else:
            text_to_parse = text

        text_to_parse = text_to_parse.encode('utf-8')

        #parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.fromstring(text_to_parse)
        pretty_xml = etree.tostring(tree, pretty_print=True, encoding="utf-8").decode('utf-8')

        if 'encoding=' in new_xml_in_lines[0]:
            pretty_xml = '\n'.join((new_xml_in_lines[0], pretty_xml))

        return pretty_xml
