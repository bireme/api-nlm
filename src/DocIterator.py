#!/usr/bin/python3
# -*- coding: utf-8 -*-

# =========================================================================
#
#    Copyright © 2016 BIREME/PAHO/WHO
#
#    This file is part of API-NLM.
#
#    API-NLM is free software: you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 2.1 of
#    the License, or (at your option) any later version.
#
#    API-NLM is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with API-NLM. If not, see <http://www.gnu.org/licenses/>.
#
# =========================================================================

import time
from LoadUrl import loadUrl
from XML import MyXML

__date__ = 20160418


class DocIterator:

    def __init__(self,
                 ids,
                 dbName="pubmed",
                 retType="MEDLINE",
                 retMode="XML",
                 xpathSplit="PubmedArticleSet/PubmedArticle",
                 verbose=True):
        """

        ids - list of xml document ids to be downloaded
        dbName - database  name
        retType - see efetch 'rettype' documentation
        retMode - see efetch 'retmode' documentation
        xpathSplit - the xpath expression used to extract the desired xml
                     documents from the big one downloaded with efetch
        verbose - if True print a dot in the standard output when a block
                  is loaded
        """
        base = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        size = 50  # 100

        self.ids = ids
        self.total = len(ids)
        if self.total == 0:
            raise Exception("Empty id list")

        self.blockSize = size if self.total > size else self.total
        self.lastBlock = (self.total / self.blockSize) - 1
        self.curBlock = 0
        self.curBlkPos = 0
        self.xmlBlock = []
        self.xpath = xpathSplit
        self.url = base
        self.postParam = {"db": dbName, "retmax": str(self.blockSize),
                          "rettype": retType, "retmode": retMode}
        self.verbose = verbose
        self.__loadBlock(0)

    def __iter__(self):
        """Turn this class iterable"""
        return self

    def __next__(self):
        """Return the next pair (<id>,<downloaded xml document>)"""
        xml = None
        if self.curBlkPos <= len(self.xmlBlock) - 1:
            xml = self.xmlBlock[self.curBlkPos]
            self.curBlkPos += 1
        else:
            if self.curBlock < self.lastBlock:
                self.__loadBlock(self.curBlock + 1)
                xml = self.__next__()
            else:
                raise StopIteration()
        return xml

    def __loadBlock(self,
                    blkNumber,
                    waitSeconds=30):
        """
        Load the document buffer with the next documents.

        blkNumber - the block number to be downloaded (initial block is 0)
        waitSeconds - number of seconds the program will sleep it download
                      fails
        """
        if self.verbose:
            if waitSeconds == 30:
                print('.', end="", flush=True)

        block = []
        retStart = blkNumber * self.blockSize
        if retStart < self.total:
            pair = self.__getIds(retStart)
            self.postParam["id"] = pair[1]
            xmlRes = loadUrl(self.url, post_values=self.postParam)
            del self.postParam["id"]
            if xmlRes[0] == 200:
                # print("res=" + str(xmlRes[1]))
                block = self.__splitBlock(pair[0], xmlRes[1])
                self.curBlock = blkNumber
                self.curBlkPos = 0
            else:
                if waitSeconds <= 3600:  # waits up to 1 hour and try again
                    if self.verbose:
                        print("(" + str(waitSeconds) + "s)", end="",
                              flush=True)
                    time.sleep(waitSeconds)
                    self.__loadBlock(blkNumber, waitSeconds * 2)
                else:
                    raise Exception("ErrCode:" + str(xmlRes[0]) + " reason:" +
                                    xmlRes[1] + " url:" + self.url)
        else:
            raise StopIteration()

        self.xmlBlock = block

    def __splitBlock(self,
                     ids,
                     xml):
        """
        Extract from the downloaded content the desired documents using the
        xpathSplit xpath expression.

        ids = list of document ids
        xml - the downloaded xml to be splited
        Returns a list of pairs (<id>, <xml document>)
        """
        ret = []
        idx = 0
        mxml = MyXML(xml)
        elems = mxml.getXPathElements(self.xpath)
        for elem in elems:
            ret.append((ids[idx], mxml.getTreeString(elem).strip()))
            idx += 1

        return ret

    def __getIds(self,
                 retStart):
        """
        Retrieve the next ids to be used to download the xml documents
        retStart - the initial id position
        Returns a pair (<list of ids>, <string with next ids>)
        """
        ids_ = []
        strg = ""
        last = min(retStart + self.blockSize, self.total)
        first = True

        for idx in range(retStart, last):
            if first:
                first = False
            else:
                strg += ","
            id_ = self.ids[idx]
            ids_.append(id_)
            strg += str(id_)

        return (ids_, strg)