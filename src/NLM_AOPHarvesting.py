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

from datetime import datetime
from Harvesting import Harvesting
from MongoDb import MyMongo
from NLM_AheadOfPrint import NLM_AheadOfPrint
from NLM_AOPFactory import NLM_AOPFactory

__date__ = 20160418


class NLM_AOPHarvesting(Harvesting):
    def __init__(self,
                 factory,
                 verbose):
        """
        Constructor.

        factory - a NLM_AOPFactory object
        verbose - if True debug messages are printed at scream
        """
        self.factory = factory
        self.verbose = verbose
        super().__init__(factory.myMongoId, factory.myMongoDoc)

    def harvest(self):
        """Do the harvesting of the documents."""
        ahead = NLM_AheadOfPrint(self.factory)

        print("--------------------------------------------------------------")
        print("Step 1 - Downloads and saves NLM Pubmed ahead of print " +
              "documents")
        print("--------------------------------------------------------------")

        ahead.process(self.verbose)

        print("\n------------------------------------------------------------")
        print("Step 2 - Copy unique docs to the standard Medline download " +
              "dir")
        print("--------------------------------------------------------------")

        ahead.syncWorkDir(self.verbose)


if __name__ == "__main__":
    # execute only if run as a script

    verbose_ = True

    now = datetime.now()
    date = datetime.strftime(now, "%Y-%m-%d")
    hour = datetime.strftime(now, "%H:%M:%S")

    mongoHost = "ts01vm.bireme.br"
    dbName = "db_AheadOfPrint"
    idColName = "col_Id"
    docColName = "col_Doc"
    mid = MyMongo(dbName, idColName, mongoHost)
    mdoc = MyMongo(dbName, docColName, mongoHost)

    factory_ = NLM_AOPFactory()
    factory_.setMyMongoId(mid)
    factory_.setMyMongoDoc(mdoc)
    factory_.setXmlOutDir("../xml")
    factory_.setXmlProcDir("")
    factory_.setDate(date)
    factory_.setHour(hour)

    harvesting = NLM_AOPHarvesting(factory_, verbose_)
    harvesting.harvest()
