"""
Unit tests for backend.upload()
"""
import unittest
from unittest.mock import patch, MagicMock

# Mock the crucible client at import time so backend.py doesn't
# need a live Crucible connection to be imported in a test environment.
with patch('crucible.CrucibleClient', return_value=MagicMock(api_key='test')):
    import backend


ORCID           = "0009-0001-9493-2006"
PROJECT_ID      = "MFP00000"
INSTRUMENT      = "titanx"
SAMPLE_UID      = "0tdr7d6dysyz3000bkjay95zr8"
SESSION_FOLDER  = "/Users/mkwall/Git/crucible-upload-ui/test-data"


class TestUpload(unittest.TestCase):

    @patch('backend.process_each_file', return_value="mock-dataset-id")
    @patch('backend.create_session', return_value=("test-data", "mock-session-id"))
    @patch('backend.identify_session_files', return_value=["file1.emd", "file2.dm3"])
    @patch('backend.copy_all_files_to_gdrive')
    def test_upload_calls_pipeline(self, mock_gdrive, mock_identify, mock_create, mock_process):
        backend.upload(
            orcid=ORCID,
            project_id=PROJECT_ID,
            instrument_name=INSTRUMENT,
            sample_unique_id=SAMPLE_UID,
            session_folder_path=SESSION_FOLDER,
        )

        mock_gdrive.assert_called_once_with(SESSION_FOLDER, INSTRUMENT)

        mock_identify.assert_called_once_with(SESSION_FOLDER)

        mock_create.assert_called_once_with(
            SESSION_FOLDER, [], '', ORCID, PROJECT_ID, INSTRUMENT, SAMPLE_UID
        )

        self.assertEqual(mock_process.call_count, 2)
        mock_process.assert_any_call(
            "file1.emd", INSTRUMENT, PROJECT_ID, ORCID,
            "test-data", "mock-session-id", SAMPLE_UID, [], ''
        )
        mock_process.assert_any_call(
            "file2.dm3", INSTRUMENT, PROJECT_ID, ORCID,
            "test-data", "mock-session-id", SAMPLE_UID, [], ''
        )

    @patch('backend.process_each_file')
    @patch('backend.create_session', side_effect=Exception("API error"))
    @patch('backend.identify_session_files', return_value=["file1.emd"])
    @patch('backend.copy_all_files_to_gdrive')
    def test_upload_stops_if_create_session_fails(self, mock_gdrive, mock_identify, mock_create, mock_process):
        backend.upload(
            orcid=ORCID,
            project_id=PROJECT_ID,
            instrument_name=INSTRUMENT,
            sample_unique_id=SAMPLE_UID,
            session_folder_path=SESSION_FOLDER,
        )

        mock_process.assert_not_called()

    @patch('backend.process_each_file')
    @patch('backend.create_session', return_value=("test-data", "mock-session-id"))
    @patch('backend.identify_session_files', return_value=[])
    @patch('backend.copy_all_files_to_gdrive')
    def test_upload_no_files_found(self, mock_gdrive, mock_identify, mock_create, mock_process):
        backend.upload(
            orcid=ORCID,
            project_id=PROJECT_ID,
            instrument_name=INSTRUMENT,
            sample_unique_id=SAMPLE_UID,
            session_folder_path=SESSION_FOLDER,
        )

        mock_process.assert_not_called()


if __name__ == '__main__':
    unittest.main()
