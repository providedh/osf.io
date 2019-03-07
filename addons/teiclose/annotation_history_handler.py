# -*- coding: utf-8 -*-

import httplib as http

from lxml import etree
from flask import request
from django.db import connection
from osf.models import Guid, BaseFileNode
from framework.exceptions import HTTPError
from api.base.utils import waterbutler_api_url_for
from addons.teiclose.models import AnnotationHistory
from addons.teistats.tasks import call_waterbutler_quietly


class AnnotationHistoryHandler:
    def __init__(self, project_guid, file_guid):
        self.project_guid = project_guid
        self.file_guid = file_guid

        self.base_file_node = None

        self.authors = []
        self.history = []

        self.file_versions = 0


    def update_history(self):
        # pobranie histrii z bazy
        try:
            annotation_history = AnnotationHistory.objects.get(project_guid=self.project_guid, file_guid=self.file_guid)

        except AnnotationHistory.DoesNotExist:
            self.__create_history(self.project_guid, self.file_guid)
            annotation_history = AnnotationHistory.objects.get(project_guid=self.project_guid, file_guid=self.file_guid)

        try:
            guid = Guid.objects.get(_id=self.file_guid)
            self.base_file_node = BaseFileNode.objects.get(id=guid.object_id)

        except (Guid.DoesNotExist, BaseFileNode.DoesNotExist) as e:
            raise HTTPError(http.NOT_FOUND)

        self.history = annotation_history.history
        history_length = len(self.history)
        self.file_versions = self.base_file_node.current_version_number

        if history_length == self.file_versions:
            return

        elif history_length < self.file_versions:
            self.authors = self.get_authors_and_dates()

            for version_number in range(history_length + 1, self.file_versions + 1):
                new_entry = self.generate_analysis(version_number)
                self.history.append(new_entry)

            self.__save_history()
            return

        else:
            raise Exception("Number of file versions in annotation history are greater than number of existing file versions.")







        # TEST POBRANIA PLIKU



    def __create_history(self, project_guid, file_id):

        history = AnnotationHistory(project_guid=project_guid, file_guid=file_id, history=[])
        history.save()


    def __save_history(self):
        annotation_history = AnnotationHistory.objects.get(project_guid=self.project_guid, file_guid=self.file_guid)
        # annotation_history.history = json.dumps(self.history, cls=DjangoJSONEncoder)
        annotation_history.history = self.history
        annotation_history.save()



    def get_authors_and_dates(self):
        # wyciągnięcie maili autorów wszystkich wersji z bazy
        # TODO: refactor this 3 queries into one
        with connection.cursor() as cursor:
            query = """
                SELECT fileversion_id
                FROM public.osf_basefilenode_versions
                WHERE basefilenode_id = {0}
                ORDER BY fileversion_id
            """.format(self.base_file_node.id)

            cursor.execute(query)

            result = cursor.fetchall()

            authors = []

            for i, row in enumerate(result):
                fileversion_id = row[0]

                query = """
                    SELECT creator_id, created
                    FROM public.osf_fileversion
                    WHERE id = {0}
                """.format(fileversion_id)

                cursor.execute(query)

                result = cursor.fetchone()

                creator_id = result[0]
                created = result[1]

                query = """
                    SELECT username
                    FROM public.osf_osfuser
                    WHERE id = {0}
                """.format(creator_id)

                cursor.execute(query)

                result = cursor.fetchone()
                author = result[0]

                entry = {
                    'version': i + 1,
                    'author_email': author,
                    'created': created
                }

                authors.append(entry)

        return authors




    def generate_analysis(self, version):
        kwargs_1 = {
            'version': version
        }

        provider = self.base_file_node.provider
        file_path = '/' + self.base_file_node._id

        waterbutler_url = waterbutler_api_url_for(self.project_guid, provider, file_path, True, **kwargs_1)

        cookies = request.cookies
        auth_header = request.headers.get('HTTP_AUTHORIZATION')
        file_response = call_waterbutler_quietly(waterbutler_url, cookies, auth_header)

        text = file_response.content

        uncertainties = self.count_uncertainties(text)

        print(self.authors[version - 1]['created'])

        entry = {
            'version': version,
            'url': '/' + self.project_guid + '/' + 'teiclose/' + self.file_guid + '/' + str(version) + '/',
            'timestamp': str(self.authors[version - 1]['created']),
            'contributor': self.authors[version - 1]['author_email'],
            'imprecision': uncertainties['imprecision'],
            'ignorance': uncertainties['ignorance'],
            'credibility': uncertainties['credibility'],
            'completeness': uncertainties['completeness']
        }

        return entry



    def count_uncertainties(self, text):

        text_in_lines = text.splitlines()

        first_line = text_in_lines[0]

        if "encoding=" in first_line:
            text_to_parse = text_in_lines[1:]
            text_to_parse = "\n".join(text_to_parse)

        else:
            text_to_parse = text

        tree = etree.fromstring(text_to_parse)

        namespaces = {
            'default': "http://www.tei-c.org/ns/1.0",
            'xi': "http://www.w3.org/2001/XInclude",
        }

        uncertainties = {
            'completeness': 0,
            'credibility': 0,
            'ignorance': 0,
            'imprecision': 0,
        }

        for key, value in uncertainties.items():
            number_of_uncertainties = len(
                tree.xpath("//default:certainty[@source='" + key + "']", namespaces=namespaces))

            uncertainties[key] = number_of_uncertainties

        return uncertainties


    def get_history(self, version):
        self.update_history()

        if version > len(self.history):
            message = {
                "message_long": "There is no version {0} for this file. Latest file version is {1}.".format(version, self.file_versions),
                "message_short": "Not found",
                "code": 404,
                "referrer": None
            }

            return message

        else:
            history = self.history[:version]

            return history



