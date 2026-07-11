import datetime
import os
from types import SimpleNamespace
from asn1crypto.core import UTF8String
from cryptography import x509
from cryptography.x509.oid import ExtensionOID
from django.test import SimpleTestCase
from zentral.utils.certificates import (is_ca, iter_cert_trees, iter_certificates, parse_apple_dev_id,
                                        parse_dn, parse_text_dn)


class _FakeCert:
    """Stand-in exposing .extensions.get_extension_for_oid for is_ca(); missing oids raise
    ExtensionNotFound like cryptography does."""
    def __init__(self, extensions):
        self._extensions = extensions

    @property
    def extensions(self):
        extensions = self._extensions

        class _Extensions:
            def get_extension_for_oid(self, oid):
                try:
                    return extensions[oid]
                except KeyError:
                    raise x509.ExtensionNotFound("not found", oid)

        return _Extensions()


class CertificatesTestCate(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        tlsdir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "../../conf/start/docker/tls/")
        with open(os.path.join(tlsdir, "zentral.crt")) as f:
            cls.cert = f.read()
        with open(os.path.join(tlsdir, "zentral_ca.crt")) as f:
            cls.ca_cert = f.read()
        cls.fullchain = cls.cert + cls.ca_cert

    def test_is_ca(self):
        cert, ca_cert = list(iter_certificates(self.fullchain))
        self.assertEqual(is_ca(cert), False)
        self.assertEqual(is_ca(ca_cert), True)

    def test_is_ca_unparseable_extensions(self):
        class Cert:
            @property
            def extensions(self):
                raise ValueError('error parsing asn1 value: ParseError { kind: EncodedDefault, '
                                 'location: ["BasicConstraints::ca"] }')
        self.assertEqual(is_ca(Cert()), False)

    def test_is_ca_key_usage_fallback(self):
        # no BasicConstraints -> fall back to KeyUsage.key_cert_sign
        for key_cert_sign in (True, False):
            cert = _FakeCert({ExtensionOID.KEY_USAGE:
                              SimpleNamespace(value=SimpleNamespace(key_cert_sign=key_cert_sign))})
            self.assertEqual(is_ca(cert), key_cert_sign)

    def test_is_ca_no_relevant_extensions(self):
        # neither BasicConstraints nor KeyUsage -> not a CA
        self.assertEqual(is_ca(_FakeCert({})), False)

    def test_dev_id_match(self):
        self.assertEqual(
            parse_apple_dev_id("Developer ID Application: Mozilla Corporation (43AQ936H96)"),
            ('Mozilla Corporation', '43AQ936H96')
        )

    def test_dev_id_no_match(self):
        with self.assertRaises(ValueError) as cm:
            parse_apple_dev_id("le temps des cerises")
        self.assertEqual(cm.exception.args[0], "Not an Apple developer ID")

    def test_iter_cert_trees(self):
        self.assertEqual(
            list(iter_cert_trees(self.fullchain)),
            [{'common_name': 'zentral',
              'sha_1': 'f373928e75dfa460726c92c3263e664816b504d5',
              'signed_by': {'common_name': 'Zentral CA',
                            'organization': 'Zentral',
                            'organizational_unit': 'IT'},
              'valid_from': datetime.datetime(2019, 6, 27, 10, 56, 5),
              'valid_until': datetime.datetime(2029, 6, 24, 10, 56, 5)},
             {'common_name': 'Zentral CA',
              'organization': 'Zentral',
              'organizational_unit': 'IT',
              'sha_1': '9a2dc1b26c23776aa828aaaae6d5284981e81f8a',
              'signed_by': {'common_name': 'Zentral CA',
                            'organization': 'Zentral',
                            'organizational_unit': 'IT'},
              'valid_from': datetime.datetime(2017, 10, 16, 15, 14, 38),
              'valid_until': datetime.datetime(2027, 10, 14, 15, 14, 38)}]
        )

    def test_parse_dn(self):
        serialNumber = "le début de la fin"
        serialNumberASN1 = UTF8String(serialNumber).dump().hex()
        self.assertEqual(
            parse_dn(f"CN=L. Eagle,O=Sue\\, Grabbit and Runn,C=GB,2.5.4.5=#{serialNumberASN1}"),
            {"CN": "L. Eagle",
             "O": "Sue, Grabbit and Runn",
             "C": "GB",
             "serialNumber": serialNumber}
        )

    def test_parse_text_dn(self):
        self.assertEqual(
            parse_text_dn("/DC=com/DC=dhl/CN=Kundenkonto, Noreply, BN/emailAddress=noreply.kundenkonto@dhl.de"),
            {"DC": ["com", "dhl"],
             "CN": ["Kundenkonto, Noreply, BN"],
             "emailAddress": ["noreply.kundenkonto@dhl.de"]}
        )
