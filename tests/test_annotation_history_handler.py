import os
import mock
from addons.teiclose.annotation_history_handler import AnnotationHistoryHandler


history_expected = [
    {
        "version": 1,
        "contributor": "jan.nowak@zmyslonymail.com",
        "timestamp": "2001-01-01 01:01:01.000001+00:00",
        "url": "/abcde/teiclose/fghij/1/",
        "credibility": 0,
        "ignorance": 0,
        "imprecision": 0,
        "incompleteness": 0,
        "variation": 0
    },
    {
        "version": 2,
        "contributor": "jan.nowak@zmyslonymail.com",
        "timestamp": "2002-02-02 02:02:02.000002+00:00",
        "url": "/abcde/teiclose/fghij/2/",
        "credibility": 1,
        "ignorance": 1,
        "imprecision": 1,
        "incompleteness": 1,
        "variation": 2
    },
    {
        "version": 3,
        "contributor": "jan.nowak@zmyslonymail.com",
        "timestamp": "2003-03-03 03:03:03.000003+00:00",
        "url": "/abcde/teiclose/fghij/3/",
        "credibility": 1,
        "ignorance": 3,
        "imprecision": 1,
        "incompleteness": 2,
        "variation": 3
    },
]

history_error_expected = {
    "code": 404,
    "referrer": None,
    "message_short": "Not found",
    "message_long": "There is no version 4 for this file. Latest file version is 3."
}

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


class FakeBaseFileNode:
    def __init__(self):
        self.provider = 'osfstorage'
        self._id = u'5c7fc7bd542d550011fd7603'

        self.current_version_number = 3


def fake_get_file_text(version):
    filename = 'dep_835104r162_tei_certainty_v' + str(version) + '.xml'
    current_directory = os.path.dirname(__file__)

    file_path = os.path.join(current_directory, "test_annotation_history_handler_files", filename)

    with open(file_path) as file:
        text = file.read()

    return text


def fake_save_history_to_db():
    pass


@mock.patch('addons.teiclose.annotation_history_handler.AnnotationHistoryHandler._AnnotationHistoryHandler__save_history_to_db',
            side_effect=fake_save_history_to_db)
@mock.patch('addons.teiclose.annotation_history_handler.AnnotationHistoryHandler._AnnotationHistoryHandler__get_file_text',
            side_effect=fake_get_file_text)
@mock.patch('addons.teiclose.annotation_history_handler.AnnotationHistoryHandler._AnnotationHistoryHandler__get_versions_metadata_from_db',
            return_value=fake_versions_metadata)
@mock.patch('addons.teiclose.annotation_history_handler.AnnotationHistoryHandler._AnnotationHistoryHandler__get_base_file_node_from_db',
            return_value=FakeBaseFileNode())
@mock.patch('addons.teiclose.annotation_history_handler.AnnotationHistoryHandler._AnnotationHistoryHandler__get_history_from_db',
            return_value=history_expected)
class TestAnnotationHistoryHandler:
    def setup(self):
        project_guid = 'abcde'
        file_guid = 'fghij'

        self.annotation_history_handler = AnnotationHistoryHandler(project_guid, file_guid)

    def test_get_history__no_history_in_db__history_expected(self, mock_get_history_from_db,
                                                                   mock_get_base_file_node_from_db,
                                                                   mock_get_versions_metadata_from_db,
                                                                   mock_get_fiel_text,
                                                                   mock_save_history_to_db):
        history_in_db = []

        with (mock.patch.object(self.annotation_history_handler, '_AnnotationHistoryHandler__get_history_from_db',
                                return_value=history_in_db)):
            history = self.annotation_history_handler.get_history(3)

            assert history == history_expected

    def test_get_history__part_of_history_in_db__history_expected(self, mock_get_history_from_db,
                                                                  mock_get_base_file_node_from_db,
                                                                  mock_get_versions_metadata_from_db,
                                                                  mock_get_fiel_text,
                                                                  mock_save_history_to_db):
        history_in_db = history_expected[:1]

        with (mock.patch.object(self.annotation_history_handler, '_AnnotationHistoryHandler__get_history_from_db',
                                return_value=history_in_db)):
            history = self.annotation_history_handler.get_history(3)

            assert history == history_expected

    def test_get_history__full_history_in_db__history_expected(self, mock_get_history_from_db,
                                                               mock_get_base_file_node_from_db,
                                                               mock_get_versions_metadata_from_db,
                                                               mock_get_fiel_text,
                                                               mock_save_history_to_db):
        history_in_db = history_expected

        with (mock.patch.object(self.annotation_history_handler, '_AnnotationHistoryHandler__get_history_from_db',
                                return_value=history_in_db)):
            history = self.annotation_history_handler.get_history(3)

            assert history == history_expected

    def test_get_history__get_history_for_older_version__history_expected(self, mock_get_history_from_db,
                                                                          mock_get_base_file_node_from_db,
                                                                          mock_get_versions_metadata_from_db,
                                                                          mock_get_fiel_text,
                                                                          mock_save_history_to_db):
        history = self.annotation_history_handler.get_history(2)

        assert history == history_expected[:2]

    def test_get_history__get_history_for_not_created_version__history_expected(self, mock_get_history_from_db,
                                                                                mock_get_base_file_node_from_db,
                                                                                mock_get_versions_metadata_from_db,
                                                                                mock_get_fiel_text,
                                                                                mock_save_history_to_db):
        history = self.annotation_history_handler.get_history(4)

        assert history == history_error_expected
