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
        self.__project_guid = project_guid
        self.__file_guid = file_guid

        self.__last_file_version_nr = 0
        self.__base_file_node = None

        self.__history = []

    def get_history(self, version):
        self.update_history()

        if version > len(self.__history):
            message = {
                "message_long": "There is no version {0} for this file. Latest file version is {1}.".format(
                    version,
                    self.__last_file_version_nr
                ),
                "message_short": "Not found",
                "code": 404,
                "referrer": None
            }

            return message

        else:
            history = self.__history[:version]

            return history

    def update_history(self):
        self.__history = self.__get_history_from_db()
        self.__base_file_node = self.__get_base_file_node_from_db()
        self.__last_file_version_nr = self.__base_file_node.current_version_number

        if len(self.__history) == self.__last_file_version_nr:
            return

        elif len(self.__history) < self.__last_file_version_nr:
            self.__append_missing_history_steps()
            self.__save_history_to_db()
            return

        else:
            raise Exception("Number of file versions in annotation history are greater than number of existing "
                            "file versions.")

    def __get_history_from_db(self):
        try:
            annotation_history = AnnotationHistory.objects.get(project_guid=self.__project_guid,
                                                               file_guid=self.__file_guid)

        except AnnotationHistory.DoesNotExist:
            self.__create_history_in_db(self.__project_guid, self.__file_guid)
            annotation_history = AnnotationHistory.objects.get(project_guid=self.__project_guid,
                                                               file_guid=self.__file_guid)

        return annotation_history.history

    def __create_history_in_db(self, project_guid, file_id):
        history = AnnotationHistory(project_guid=project_guid, file_guid=file_id, history=[])
        history.save()

    def __get_base_file_node_from_db(self):
        try:
            guid = Guid.objects.get(_id=self.__file_guid)
            base_file_node = BaseFileNode.objects.get(id=guid.object_id)

        except (Guid.DoesNotExist, BaseFileNode.DoesNotExist):
            raise HTTPError(http.NOT_FOUND)

        return base_file_node

    def __append_missing_history_steps(self):
        versions_metadata = self.__get_versions_metadata_from_db()

        first_missing_version = len(self.__history) + 1
        last_missing_version = self.__last_file_version_nr

        for version_nr in range(first_missing_version, last_missing_version + 1):
            version_metadata = versions_metadata[version_nr - 1]
            history_step = self.__create_history_step(version_nr, version_metadata)
            self.__history.append(history_step)

    def __get_versions_metadata_from_db(self):
        versions_metadata = []

        with connection.cursor() as cursor:
            query = """
                SELECT F.identifier, F.created, U.username
                FROM public.osf_osfuser AS U
                INNER JOIN public.osf_fileversion AS F
                    ON U.id = F.creator_id
                    INNER JOIN public.osf_basefilenode_versions AS V
                        ON F.id = V.fileversion_id
                WHERE V.basefilenode_id = {0}
                ORDER BY F.identifier
            """.format(self.__base_file_node.id)

            cursor.execute(query)
            results = cursor.fetchall()

            for result in results:
                metadata = {
                    'version': result[0],
                    'created': result[1],
                    'author_email': result[2],
                }

                versions_metadata.append(metadata)

        return versions_metadata

    def __create_history_step(self, version, version_metadata):
        text = self.__get_file_text(version)
        uncertainties = self.__count_uncertainties(text)

        history_step = {
            'version': version,
            'contributor': version_metadata['author_email'],
            'timestamp': str(version_metadata['created']),
            'url': '/' + self.__project_guid + '/' + 'teiclose/' + self.__file_guid + '/' + str(version) + '/',
            'credibility': uncertainties['credibility'],
            'ignorance': uncertainties['ignorance'],
            'imprecision': uncertainties['imprecision'],
            'incompleteness': uncertainties['incompleteness'],
            'variation': uncertainties['variation'],
        }

        return history_step

    def __get_file_text(self, version):
        provider = self.__base_file_node.provider
        file_path = '/' + self.__base_file_node._id

        waterbutler_url = waterbutler_api_url_for(self.__project_guid, provider, file_path, True, version=version)

        cookies = request.cookies
        auth_header = request.headers.get('HTTP_AUTHORIZATION')
        file_response = call_waterbutler_quietly(waterbutler_url, cookies, auth_header)

        text = file_response.content

        return text

    def __count_uncertainties(self, text):
        text = self.__remove_encoding_line(text)
        tree = etree.fromstring(text)

        namespaces = {
            'default': "http://www.tei-c.org/ns/1.0",
        }

        uncertainties = {
            'credibility': 0,
            'ignorance': 0,
            'imprecision': 0,
            'incompleteness': 0,
            'variation': 0,
        }

        for key, value in uncertainties.items():
            number_of_uncertainties = len(
                tree.xpath("//default:classCode[@scheme=\"http://providedh.eu/uncertainty/ns/1.0\"]/"
                           "default:certainty[@source='" + key + "']", namespaces=namespaces))

            uncertainties[key] = number_of_uncertainties

        return uncertainties

    def __remove_encoding_line(self, text):
        text_in_lines = text.splitlines()
        first_line = text_in_lines[0]

        if "encoding=" in first_line:
            text_to_parse = text_in_lines[1:]
            text_to_parse = "\n".join(text_to_parse)

        else:
            text_to_parse = text

        return text_to_parse

    def __save_history_to_db(self):
        annotation_history = AnnotationHistory.objects.get(project_guid=self.__project_guid, file_guid=self.__file_guid)
        annotation_history.history = self.__history
        annotation_history.save()
