from addons.teiclose.annotation_history_handler import AnnotationHistoryHandler
from mock import patch
import os


class FakeBaseFileNode:
    def __init__(self):
        self.provider = 'osfstorage'
        self._id = u'5c7fc7bd542d550011fd7603'

    def current_version_number(self):
        return 3

history_expected = [
    {
        "imprecision": 0,
         "completeness": 0,
         "url": "/abcde/teiclose/fghij/1/",
         "timestamp": "2001-01-01 01:01:01.000001+00:00",
         "ignorance": 0,
         "version": 1,
         "credibility": 0,
         "contributor": "jan.nowak@zmyslonymail.com"
    },
    {
        "imprecision": 1,
        "completeness": 1,
        "url": "/abcde/teiclose/fghij/2/",
        "timestamp": "2002-02-02 02:02:02.000002+00:00",
        "ignorance": 1,
        "version": 2,
        "credibility": 1,
        "contributor": "jan.nowak@zmyslonymail.com"
    },
    {
        "imprecision": 1,
        "completeness": 2,
        "url": "/abcde/teiclose/fghij/3/",
        "timestamp": "2003-03-03 03:03:03.000003+00:00",
        "ignorance": 3,
        "version": 3,
        "credibility": 1,
        "contributor": "jan.nowak@zmyslonymail.com"
    },
]

fake_versions_metadata = [
    {
        'version': '1',
        'created': '2001-01-01 01:01:01.000001+00:00',
        'author_email': 'jan.nowak@zmyslonymail.com',
    },
    {
        'version': '2',
        'created': '2002-02-02 02:02:02.000002+00:00',
        'author_email': 'jan.nowak@zmyslonymail.com',
    },
    {
        'version': '3',
        'created': '2003-03-03 03:03:03.000003+00:00',
        'author_email': 'jan.nowak@zmyslonymail.com',
    },
]

fake_base_file_node = FakeBaseFileNode()


def fake_get_file_text(version):
    filename = 'dep_835104r162_tei_certainty_v' + str(version) + '.xml'
    current_directory = os.path.dirname(__file__)

    file_path = os.path.join(current_directory, "test_annotation_history_handler_files", filename)

    with open(file_path) as file:
        text = file.read()

    return text


def fake_save_history_to_db():
    pass


def test_get_history__no_history_in_db__history_expected():
    annotation_history_handler = AnnotationHistoryHandler('abcde', 'fghij')

    with (patch.object(annotation_history_handler, '_AnnotationHistoryHandler__get_history_from_db',
                       return_value=[])):
        with (patch.object(annotation_history_handler, '_AnnotationHistoryHandler__get_base_file_node_from_db',
                           return_value=fake_base_file_node)):
            with (patch.object(annotation_history_handler, '_AnnotationHistoryHandler__get_versions_metadata_from_db',
                               return_value=fake_versions_metadata)):
                with (patch.object(annotation_history_handler, '_AnnotationHistoryHandler__get_file_text',
                                   side_effect=fake_get_file_text)):
                    with (patch.object(annotation_history_handler, '_AnnotationHistoryHandler__save_history_to_db',
                                       side_effect=fake_save_history_to_db)):
                        history = annotation_history_handler.get_history(3)

                        assert history == history_expected


def test_get_history__part_of_history_in_db__history_expected():
    annotation_history_handler = AnnotationHistoryHandler('abcde', 'fghij')

    with (patch.object(annotation_history_handler, '_AnnotationHistoryHandler__get_history_from_db',
                       return_value=history_expected[:1])):
        with (patch.object(annotation_history_handler, '_AnnotationHistoryHandler__get_base_file_node_from_db',
                           return_value=fake_base_file_node)):
            with (patch.object(annotation_history_handler, '_AnnotationHistoryHandler__get_versions_metadata_from_db',
                               return_value=fake_versions_metadata)):
                with (patch.object(annotation_history_handler, '_AnnotationHistoryHandler__get_file_text',
                                   side_effect=fake_get_file_text)):
                    with (patch.object(annotation_history_handler, '_AnnotationHistoryHandler__save_history_to_db',
                                       side_effect=fake_save_history_to_db)):
                        history = annotation_history_handler.get_history(3)

                        assert history == history_expected














