import unittest
import GoProController

class GoProControllerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.gopro = GoProController()
    
    def tearDown(self) -> None:
        self.gopro