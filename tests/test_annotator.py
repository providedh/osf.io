import os
import pytest
import mock

from addons.teiclose.annotator import Annotator

def read_file(path):
    with open(path, 'r') as file:
        text = file.read()

    return text

def fake_get_user_data_from_db(guid):
    data = {
        'forename': 'Tony',
        'surname': 'Stark',
        'email': 'tony.stark@zmyslonymail.com',
        'profile': 'https://providedh.ehum.psnc.pl/abcde/',
    }

    return data


@mock.patch('addons.teiclose.annotator.Annotator.get_user_data_from_db',
            side_effect=fake_get_user_data_from_db)
# @mock.patch('addons.teiclose.annotator.Annotator.get_user_guid',
#             return_value='abcde')
class TestAnnotator:
    def test_add_annotation__add_tag_to_text__string(self, mock_get_user_data_from_db):
        json = {
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

        dirname = os.path.dirname(__file__)
        input_file_path = os.path.join(dirname, "test_annotator_files", "source_files", "source_file.xml")
        expected_file_path = os.path.join(dirname, "test_annotator_files", "result_files", "add_tag_to_text__result.xml")

        input_text = read_file(input_file_path)
        expected_text = read_file(expected_file_path)

        user_guid = 'abcde'

        annotator = Annotator()
        result = annotator.add_annotation(input_text, json, user_guid)

        assert result == expected_text

    def test_add_annotation__add_certainty_to_text__string(self, mock_get_user_data_from_db):
        json = {
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

        dirname = os.path.dirname(__file__)
        input_file_path = os.path.join(dirname, "test_annotator_files", "source_files", "source_file.xml")
        expected_file_path = os.path.join(dirname, "test_annotator_files", "result_files", "add_certainty_to_text__result.xml")

        input_text = read_file(input_file_path)
        expected_text = read_file(expected_file_path)

        user_guid = 'abcde'

        annotator = Annotator()
        result = annotator.add_annotation(input_text, json, user_guid)

        assert result == expected_text

    def test_add_annotation__add_tag_and_certainty_to_text__string(self, mock_get_user_data_from_db):
        json = {
            "start_row": 217,
            "start_col": 7,
            "end_row": 217,
            "end_col": 11,
            "source": "ignorance",
            "locus": "value",
            "certainty": "high",
            "asserted_value": "",
            "description": "",
            "tag": "test"
        }

        dirname = os.path.dirname(__file__)
        input_file_path = os.path.join(dirname, "test_annotator_files", "source_files", "source_file.xml")
        expected_file_path = os.path.join(dirname, "test_annotator_files", "result_files", "add_tag_and_certainty_to_text__result.xml")

        input_text = read_file(input_file_path)
        expected_text = read_file(expected_file_path)

        user_guid = 'abcde'

        annotator = Annotator()
        result = annotator.add_annotation(input_text, json, user_guid)

        assert result == expected_text

    def test_add_annotation__add_tag_to_text_with_tag__string(self, mock_get_user_data_from_db):
        json = {
            "start_row": 217,
            "start_col": 73,
            "end_row": 217,
            "end_col": 92,
            "source": "",
            "locus": "",
            "certainty": "",
            "asserted_value": "",
            "description": "",
            "tag": "test"
        }

        dirname = os.path.dirname(__file__)
        input_file_path = os.path.join(dirname, "test_annotator_files", "source_files", "source_file.xml")
        expected_file_path = os.path.join(dirname, "test_annotator_files", "result_files", "add_tag_to_text_with_tag__result.xml")

        input_text = read_file(input_file_path)
        expected_text = read_file(expected_file_path)

        user_guid = 'abcde'

        annotator = Annotator()
        result = annotator.add_annotation(input_text, json, user_guid)

        assert result == expected_text

    def test_add_annotation__add_tag_to_text_with_same_tag__string(self, mock_get_user_data_from_db):
        json = {
            "start_row": 217,
            "start_col": 73,
            "end_row": 217,
            "end_col": 92,
            "source": "",
            "locus": "",
            "certainty": "",
            "asserted_value": "",
            "description": "",
            "tag": "place"
        }

        dirname = os.path.dirname(__file__)
        input_file_path = os.path.join(dirname, "test_annotator_files", "source_files", "source_file.xml")
        expected_file_path = os.path.join(dirname, "test_annotator_files", "result_files", "add_tag_to_text_with_same_tag__result.xml")

        input_text = read_file(input_file_path)
        expected_text = read_file(expected_file_path)

        user_guid = 'abcde'

        annotator = Annotator()
        result = annotator.add_annotation(input_text, json, user_guid)

        assert result == expected_text

    def test_add_annotation__add_certainty_to_text_with_same_tag__string(self,  mock_get_user_data_from_db):
        json = {
            "start_row": 217,
            "start_col": 73,
            "end_row": 217,
            "end_col": 92,
            "source": "ignorance",
            "locus": "value",
            "certainty": "high",
            "asserted_value": "",
            "description": "",
            "tag": "place"
        }

        dirname = os.path.dirname(__file__)
        input_file_path = os.path.join(dirname, "test_annotator_files", "source_files", "source_file.xml")
        expected_file_path = os.path.join(dirname, "test_annotator_files", "result_files", "add_certainty_to_text_with_same_tag__result.xml")

        input_text = read_file(input_file_path)
        expected_text = read_file(expected_file_path)

        user_guid = 'abcde'

        annotator = Annotator()
        result = annotator.add_annotation(input_text, json, user_guid)

        assert result == expected_text

    def test_add_annotation__add_certainty_to_text_with_tag__string(self, mock_get_user_data_from_db):
        json = {
            "start_row": 217,
            "start_col": 73,
            "end_row": 217,
            "end_col": 92,
            "source": "ignorance",
            "locus": "value",
            "certainty": "high",
            "asserted_value": "",
            "description": "",
            "tag": ""
        }

        dirname = os.path.dirname(__file__)
        input_file_path = os.path.join(dirname, "test_annotator_files", "source_files", "source_file.xml")
        expected_file_path = os.path.join(dirname, "test_annotator_files", "result_files", "add_certainty_to_text_with_tag__result.xml")

        input_text = read_file(input_file_path)
        expected_text = read_file(expected_file_path)

        user_guid = 'abcde'

        annotator = Annotator()
        result = annotator.add_annotation(input_text, json, user_guid)

        assert result == expected_text

    def test_add_annotation__add_tag_and_certainty_to_text_with_other_tag__string(self, mock_get_user_data_from_db):
        json = {
            "start_row": 218,
            "start_col": 115,
            "end_row": 218,
            "end_col": 121,
            "source": "ignorance",
            "locus": "value",
            "certainty": "high",
            "asserted_value": "",
            "description": "",
            "tag": "test"
        }

        dirname = os.path.dirname(__file__)
        input_file_path = os.path.join(dirname, "test_annotator_files", "source_files", "source_file.xml")
        expected_file_path = os.path.join(dirname, "test_annotator_files", "result_files", "add_tag_and_certainty_to_text_with_other_tag__result.xml")

        input_text = read_file(input_file_path)
        expected_text = read_file(expected_file_path)

        user_guid = 'abcde'

        annotator = Annotator()
        result = annotator.add_annotation(input_text, json, user_guid)

        assert result == expected_text

    def test_add_annotation__add_tag_to_text_with_tag_and_certainty__string(self, mock_get_user_data_from_db):
        json = {
            "start_row": 218,
            "start_col": 115,
            "end_row": 218,
            "end_col": 121,
            "source": "",
            "locus": "",
            "certainty": "",
            "asserted_value": "",
            "description": "",
            "tag": "test"
        }

        dirname = os.path.dirname(__file__)
        input_file_path = os.path.join(dirname, "test_annotator_files", "source_files", "source_file.xml")
        expected_file_path = os.path.join(dirname, "test_annotator_files", "result_files", "add_tag_to_text_with_tag_and_certainty__result.xml")

        input_text = read_file(input_file_path)
        expected_text = read_file(expected_file_path)

        user_guid = 'abcde'

        annotator = Annotator()
        result = annotator.add_annotation(input_text, json, user_guid)

        assert result == expected_text

    def test_add_annotation__add_tag_and_certainty_to_text_with_same_tag_and_certainty__string(self, mock_get_user_data_from_db):
        json = {
            "start_row": 218,
            "start_col": 115,
            "end_row": 218,
            "end_col": 121,
            "source": "ignorance",
            "locus": "value",
            "certainty": "high",
            "asserted_value": "",
            "description": "",
            "tag": "date"
        }

        dirname = os.path.dirname(__file__)
        input_file_path = os.path.join(dirname, "test_annotator_files", "source_files", "source_file.xml")
        expected_file_path = os.path.join(dirname, "test_annotator_files", "result_files", "add_tag_and_certainty_to_text_with_same_tag_and_certainty__result.xml")

        input_text = read_file(input_file_path)
        expected_text = read_file(expected_file_path)

        user_guid = 'abcde'

        annotator = Annotator()
        result = annotator.add_annotation(input_text, json, user_guid)

        assert result == expected_text

    def test_add_annotation__add_certainty_to_text_with_tag_and_certainty__string(self, mock_get_user_data_from_db):
        json = {
            "start_row": 218,
            "start_col": 115,
            "end_row": 218,
            "end_col": 121,
            "source": "ignorance",
            "locus": "value",
            "certainty": "high",
            "asserted_value": "",
            "description": "",
            "tag": ""
        }

        dirname = os.path.dirname(__file__)
        input_file_path = os.path.join(dirname, "test_annotator_files", "source_files", "source_file.xml")
        expected_file_path = os.path.join(dirname, "test_annotator_files", "result_files", "add_certainty_to_text_with_tag_and_certainty__result.xml")

        input_text = read_file(input_file_path)
        expected_text = read_file(expected_file_path)

        user_guid = 'abcde'

        annotator = Annotator()
        result = annotator.add_annotation(input_text, json, user_guid)

        assert result == expected_text

    def test_add_annotation__add_tag_and_certainty_to_text_with_other_tag_and_certainty__string(self, mock_get_user_data_from_db):
        json = {
            "start_row": 218,
            "start_col": 115,
            "end_row": 218,
            "end_col": 121,
            "source": "ignorance",
            "locus": "value",
            "certainty": "high",
            "asserted_value": "",
            "description": "",
            "tag": "test"
        }

        dirname = os.path.dirname(__file__)
        input_file_path = os.path.join(dirname, "test_annotator_files", "source_files", "source_file.xml")
        expected_file_path = os.path.join(dirname, "test_annotator_files", "result_files", "add_tag_and_certainty_to_text_with_other_tag_and_certainty__result.xml")

        input_text = read_file(input_file_path)
        expected_text = read_file(expected_file_path)

        user_guid = 'abcde'

        annotator = Annotator()
        result = annotator.add_annotation(input_text, json, user_guid)

        assert result == expected_text

    def test_add_annotation__add_certainty_to_text_with_same_tag_separated__string(self, mock_get_user_data_from_db):
        json = {
            "start_row": 218,
            "start_col": 444,
            "end_row": 218,
            "end_col": 482,
            "source": "ignorance",
            "locus": "value",
            "certainty": "high",
            "asserted_value": "",
            "description": "",
            "tag": "person"
        }

        dirname = os.path.dirname(__file__)
        input_file_path = os.path.join(dirname, "test_annotator_files", "source_files", "source_file.xml")
        expected_file_path = os.path.join(dirname, "test_annotator_files", "result_files", "add_certainty_to_text_with_same_tag_separated__result.xml")

        input_text = read_file(input_file_path)
        expected_text = read_file(expected_file_path)

        user_guid = 'abcde'

        annotator = Annotator()
        result = annotator.add_annotation(input_text, json, user_guid)

        assert result == expected_text

    def test_add_annotation__add_first_annotator_and_certainty__string(self, mock_get_user_data_from_db):
        json = {
            "start_row": 54,
            "start_col": 7,
            "end_row": 54,
            "end_col": 11,
            "source": "ignorance",
            "locus": "value",
            "certainty": "high",
            "asserted_value": "",
            "description": "",
            "tag": ""
        }

        dirname = os.path.dirname(__file__)
        input_file_path = os.path.join(dirname, "test_annotator_files", "source_files", "source_file_without_annotators_and_certainties.xml")
        expected_file_path = os.path.join(dirname, "test_annotator_files", "result_files", "add_first_annotator_and_certainty__result.xml")

        input_text = read_file(input_file_path)
        expected_text = read_file(expected_file_path)

        user_guid = 'abcde'

        annotator = Annotator()
        result = annotator.add_annotation(input_text, json, user_guid)

        assert result == expected_text





