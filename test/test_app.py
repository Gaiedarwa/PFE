import unittest
from drax import app

class FlaskAppTests(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_cv_upload(self):
        with open("tests/sample_cv.pdf", "rb") as cv_file:
            data = {
                'cv': (cv_file, 'sample_cv.pdf')
            }
            response = self.app.post('/upload-cv', data=data, content_type='multipart/form-data')
            self.assertEqual(response.status_code, 200)
            self.assertIn('cv_text', response.json)

    def test_job_offer_upload(self):
        with open("tests/sample_offer.pdf", "rb") as offer_file:
            data = {
                'job_offer': (offer_file, 'sample_offer.pdf')
            }
            response = self.app.post('/upload-offer', data=data, content_type='multipart/form-data')
            self.assertEqual(response.status_code, 200)
            self.assertIn('offer_text', response.json)

    def test_similarity(self):
        payload = {
            'cv_text': 'Python, Flask, Docker',
            'offer_text': 'Looking for a developer with Flask and Docker experience.'
        }
        response = self.app.post('/similarity', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn('similarity_score', response.json)

if __name__ == '__main__':
    unittest.main()
