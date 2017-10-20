#!/usr/bin/env python3.6

import unittest

import cryptoparser

# * Add a test to handle importing httplib2 if it doesn't exist.
# * More testing with regexes?
# * Get a known url with target, and one without and run the whole
#   script as a test.

class RegexTestCase(unittest.TestCase):

    def test_spliturl(self):
        self.assertEqual(cryptoparser.splitdomain('http://www.alluc.ee/'), 'www.alluc.ee/')

    def test_contentparser(self):
        # 'oZFH0SLOx5v0DuQug1dqDykUWYnfbEgq'
        self.assertEqual(cryptoparser.parsecontent(
"""window.miner = new CoinHive.Anonymous('oZFH0SLOx5v0DuQug1dqDykUWYnfbEgq');"""),
            'oZFH0SLOx5v0DuQug1dqDykUWYnfbEgq')
        thehash = cryptoparser.parsecontent(None) if cryptoparser.parsecontent(None) else 0
        self.assertEqual(thehash, 0)

    def test_qualifyurl(self):
        self.assertEqual(
            [url for url in cryptoparser.qualifyurl('www.alluc.ee/')],
            ['http://www.alluc.ee/', 'https://www.alluc.ee/'])
        self.assertEqual(
            [url for url in cryptoparser.qualifyurl('badpackets.net')],
            ['http://badpackets.net', 'https://badpackets.net'])
        self.assertNotEqual(
            [url for url in cryptoparser.qualifyurl('dailystormer.ph')],
            ['https://dailystormer.com',])

    # Testing.
    #domains = ['badpackets.net'] * 3
    #prefixes = ['', 'http://', 'https://']
    #for url in map(lambda x: ''.join(x), zip(prefixes, domains)):
    #    print(url)
    #    thedomain = splitdomain(url)
    #    for qualifiedurl in qualifyurl(thedomain):
    #        print(qualifiedurl)


if __name__ == '__main__':
    regex = RegexTestCase()
    regex.test_spliturl()
    regex.test_contentparser()

# ----------------------------------------------------------------------
# Ran 2 tests in 0.000s
#
# OK
