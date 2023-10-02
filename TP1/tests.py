import unittest
import upload


class ParsingTests(unittest.TestCase):
    def test_identifies_ipv4(self):
        self.assertTrue(upload.is_ip("127.0.0.1"))

    def test_identifies_ipv6(self):
        self.assertTrue(upload.is_ip("1050:0000:0000:0000:0005:0600:300c:326b"))

    def test_identifies_nonip_addresses(self):
        self.assertFalse(upload.is_ip("hola como andas"))
        self.assertFalse(upload.is_ip("127.0.0.10000"))


if __name__ == "__main__":
    unittest.main()
