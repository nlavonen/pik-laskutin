# -*- coding: utf-8
from pik.flights import Flight
from pik.rules import FlightRule, AircraftFilter, PeriodFilter, CappedRule, AllRules, FirstRule, SetDateRule, SimpleRule, SinceDateFilter, ItemFilter, PurposeFilter, InvoicingChargeFilter, TransferTowFilter, NegationFilter, DebugRule, flightFilter, eventFilter, SetLedgerYearRule
from pik.util import Period, format_invoice, parse_iso8601_date
from pik.billing import BillingContext, Invoice
from pik.event import SimpleEvent
from pik.hansa import SimpleHansaTransaction, SimpleHansaRow
from pik import nda
import datetime as dt
import csv
import sys
from collections import defaultdict
from itertools import chain, groupby
import json
import os
from itertools import izip, count
import unicodedata
import math

def make_rules(ctx=BillingContext()):
    ACCT_PURSI_KEIKKA = 3220
    ACCT_TOW = 3130
    ACCT_DDS = 3101
    ACCT_CAO = 3100
    ACCT_TOWING = 3170 # Muut lentotoiminnan tulot
    ACCT_PURSI_INSTRUCTION = 3470 # Muut tulot koulutustoiminnasta
    ACCT_KALUSTO = 3010
    ACCT_LASKUTUSLISA = 3610 # Hallinnon tulot

    ID_KM_2014 = u"kausimaksu_tot_2014"
    ID_KM_P_2014 = u"kausimaksu_pursi_2014"
    ID_KM_M_2014 = u"kausimaksu_motti_2014"

    ID_KM_2015 = u"kausimaksu_tot_2015"
    ID_KM_P_2015 = u"kausimaksu_pursi_2015"
    ID_KM_M_2015 = u"kausimaksu_motti_2015"

    ID_KM_2016 = u"kausimaksu_tot_2016"
    ID_KM_P_2016 = u"kausimaksu_pursi_2016"
    ID_KM_M_2016 = u"kausimaksu_motti_2016"

    # Added 2017-10-09:
    ID_KM_2017 = u"kausimaksu_tot_2017"
    ID_KM_P_2017 = u"kausimaksu_pursi_2017"
    ID_KM_M_2017 = u"kausimaksu_motti_2017"

    # Added 2018-11-07:
    ID_KM_2018 = u"kausimaksu_tot_2018"
    ID_KM_P_2018 = u"kausimaksu_pursi_2018"
    ID_KM_M_2018 = u"kausimaksu_motti_2018"
    
    # Added 2019-10-08:
    ID_KM_2019 = u"kausimaksu_tot_2019"
    ID_KM_P_2019 = u"kausimaksu_pursi_2019"
    ID_KM_M_2019 = u"kausimaksu_motti_2019"
    
    ID_PK_2014 = u"pursikönttä_2014"
    ID_PK_2015 = u"pursikönttä_2015"
    ID_PK_2016 = u"pursikönttä_2016"
    ID_PK_2017 = u"pursikönttä_2017" # Added 2017-10-09
    ID_PK_2018 = u"pursikönttä_2018" # Added 2018-11-07
    ID_PK_2019 = u"pursikönttä_2019" # Added 2019-10-08

    ID_KK_2014 = u"kurssikönttä_2014"
    ID_KK_2015 = u"kurssikönttä_2015"
    ID_KK_2016 = u"kurssikönttä_2016"
    ID_KK_2017 = u"kurssikönttä_2017" # Added 2017-10-09
    ID_KK_2018 = u"kurssikönttä_2018" # Added 2018-11-07
    ID_KK_2019 = u"kurssikönttä_2019" # Added 2019-10-08

    F_PAST = [PeriodFilter(Period(dt.date(2010,1,1), dt.date(2013,12,31)))]

    F_2014 = [PeriodFilter(Period.full_year(2014))]
    F_FK = [AircraftFilter("650")]
    F_FM = [AircraftFilter("787")]
    F_FQ = [AircraftFilter("733")]
    F_FY = [AircraftFilter("883")]
    F_FI = [AircraftFilter("1035")]
    F_DG = [AircraftFilter("952")]
    F_TK = [AircraftFilter("TK")]
    F_HB = [AircraftFilter("755")]
    F_DDS = [AircraftFilter("DDS")]
    F_CAO = [AircraftFilter("CAO")]
    F_TOW = [AircraftFilter("TOW")]
    F_MOTTI = [AircraftFilter("DDS","CAO","TOW")]
    F_PURTSIKKA = [AircraftFilter("650","787","733","883","952")]
    F_KAIKKI_KONEET = [AircraftFilter("DDS","CAO","TOW","650","787","733","883","952")]
    F_PURSIK = [SinceDateFilter(ctx, ID_PK_2014)]
    F_KURSSIK = [SinceDateFilter(ctx, ID_KK_2014)]
    F_LASKUTUSLISA = [InvoicingChargeFilter()]

    F_2015 = [PeriodFilter(Period.full_year(2015))]
    F_PURTSIKKA_2015 = [AircraftFilter("650","787","733","883","952","TK")]
    F_KAIKKI_KONEET_2015 = [AircraftFilter("DDS","CAO","TOW","650","787","733","883","952","TK")]
    F_PURSIK_2015 = [SinceDateFilter(ctx, ID_PK_2015)]
    F_KURSSIK_2015 = [SinceDateFilter(ctx, ID_KK_2015)]

    F_2016 = [PeriodFilter(Period.full_year(2016))]
    F_PURTSIKKA_2016 = [AircraftFilter("650","787","733","883","952","755")]
    F_KAIKKI_KONEET_2016 = [AircraftFilter("TOW","650","787","733","883","952","755")]
    F_PURSIK_2016 = [SinceDateFilter(ctx, ID_PK_2016)]
    F_KURSSIK_2016 = [SinceDateFilter(ctx, ID_KK_2016)]
    
     # Added 2017-10-09:
    F_2017 = [PeriodFilter(Period.full_year(2017))]
    F_PURTSIKKA_2017 = [AircraftFilter("650","787","733","883","952")]
    F_KAIKKI_KONEET_2017 = [AircraftFilter("TOW","650","787","733","883","952")]
    F_PURSIK_2017 = [SinceDateFilter(ctx, ID_PK_2017)]
    F_KURSSIK_2017 = [SinceDateFilter(ctx, ID_KK_2017)]

    # Added 2018-11-07:
    F_2018 = [PeriodFilter(Period.full_year(2018))]
    F_PURTSIKKA_2018 = [AircraftFilter("650","787","733","883","952")]
    F_KAIKKI_KONEET_2018 = [AircraftFilter("TOW","650","787","733","883","952")]
    F_PURSIK_2018 = [SinceDateFilter(ctx, ID_PK_2018)]
    F_KURSSIK_2018 = [SinceDateFilter(ctx, ID_KK_2018)]
    
    # Added 2019-10-08:
    F_2019 = [PeriodFilter(Period.full_year(2019))]
    F_PURTSIKKA_2019 = [AircraftFilter("650","787","733","883","952","1035")]
    F_KAIKKI_KONEET_2019 = [AircraftFilter("TOW","650","787","733","883","952","1035")]
    F_PURSIK_2019 = [SinceDateFilter(ctx, ID_PK_2019)]
    F_KURSSIK_2019 = [SinceDateFilter(ctx, ID_KK_2019)]


    def pursi_rule(base_filters, price, kurssi_price = 0, package_price = 0):
        return FirstRule([FlightRule(package_price, ACCT_PURSI_KEIKKA, base_filters + F_PURSIK, u"Lento, pursiköntällä, %(aircraft)s, %(duration)d min"),
                          FlightRule(kurssi_price, ACCT_PURSI_KEIKKA, base_filters + F_KURSSIK, u"Lento, kurssiköntällä, %(aircraft)s, %(duration)d min, %(purpose)s"),
                          FlightRule(price, ACCT_PURSI_KEIKKA, base_filters)])

    def pursi_rule_2015(base_filters, price, kurssi_price = 0, package_price = 0):
        return FirstRule([FlightRule(package_price, ACCT_PURSI_KEIKKA, base_filters + F_PURSIK_2015, u"Lento, pursiköntällä, %(aircraft)s, %(duration)d min"),
                          FlightRule(kurssi_price, ACCT_PURSI_KEIKKA, base_filters + F_KURSSIK_2015, u"Lento, kurssiköntällä, %(aircraft)s, %(duration)d min, %(purpose)s"),
                          FlightRule(price, ACCT_PURSI_KEIKKA, base_filters)])

    def pursi_rule_2016(base_filters, price, kurssi_price = 0, package_price = 0):
        return FirstRule([FlightRule(package_price, ACCT_PURSI_KEIKKA, base_filters + F_PURSIK_2016, u"Lento, pursiköntällä, %(aircraft)s, %(duration)d min"),
                          FlightRule(kurssi_price, ACCT_PURSI_KEIKKA, base_filters + F_KURSSIK_2016, u"Lento, kurssiköntällä, %(aircraft)s, %(duration)d min, %(purpose)s"),
                          FlightRule(price, ACCT_PURSI_KEIKKA, base_filters)])

    # Added 2017-10-09:
    def pursi_rule_2017(base_filters, price, kurssi_price = 0, package_price = 0):
        return FirstRule([FlightRule(package_price, ACCT_PURSI_KEIKKA, base_filters + F_PURSIK_2017, u"Lento, pursiköntällä, %(aircraft)s, %(duration)d min"),
                          FlightRule(kurssi_price, ACCT_PURSI_KEIKKA, base_filters + F_KURSSIK_2017, u"Lento, kurssiköntällä, %(aircraft)s, %(duration)d min, %(purpose)s"),
                          FlightRule(price, ACCT_PURSI_KEIKKA, base_filters)])

    # Added 2018-11-07:
    def pursi_rule_2018(base_filters, price, kurssi_price = 0, package_price = 0):
        return FirstRule([FlightRule(package_price, ACCT_PURSI_KEIKKA, base_filters + F_PURSIK_2018, u"Lento, pursiköntällä, %(aircraft)s, %(duration)d min"),
                          FlightRule(kurssi_price, ACCT_PURSI_KEIKKA, base_filters + F_KURSSIK_2018, u"Lento, kurssiköntällä, %(aircraft)s, %(duration)d min, %(purpose)s"),
                          FlightRule(price, ACCT_PURSI_KEIKKA, base_filters)])
                          
    # Added 2019-10-08:
    def pursi_rule_2019(base_filters, price, kurssi_price = 0, package_price = 0):
        return FirstRule([FlightRule(package_price, ACCT_PURSI_KEIKKA, base_filters + F_PURSIK_2019, u"Lento, pursiköntällä, %(aircraft)s, %(duration)d min"),
                          FlightRule(kurssi_price, ACCT_PURSI_KEIKKA, base_filters + F_KURSSIK_2019, u"Lento, kurssiköntällä, %(aircraft)s, %(duration)d min, %(purpose)s"),
                          FlightRule(price, ACCT_PURSI_KEIKKA, base_filters)])

    rules_past = [
        # Normal simple events from the past are OK
        SimpleRule(F_PAST)
    ]

    rules_2014 = [
        FlightRule(171, ACCT_DDS, F_DDS + F_2014),
        FlightRule(134, ACCT_CAO, F_CAO + F_2014),
        FlightRule(146, ACCT_TOW, F_TOW + [PeriodFilter(Period(dt.date(2014, 1, 1), dt.date(2014, 3, 31)))]),
        # Variable price for TOW in the second period, based on purpose of flight
        FirstRule([FlightRule(124, ACCT_TOWING, F_TOW + [PeriodFilter(Period(dt.date(2013, 4, 1), dt.date(2014, 12, 31))), TransferTowFilter()], u"Siirtohinaus, %(duration)d min"),
                   FlightRule(104, ACCT_TOW, F_TOW + [PeriodFilter(Period(dt.date(2013, 4, 1), dt.date(2014, 12, 31)))])
               ]),

        pursi_rule(F_2014 + F_FK, 15),
        pursi_rule(F_2014 + F_FM, 25, 10),
        pursi_rule(F_2014 + F_FQ, 25),
        pursi_rule(F_2014 + F_FY, 32, 17),
        pursi_rule(F_2014 + F_DG, 40),

        # Koululentomaksu
        FlightRule(lambda ev: 5, ACCT_PURSI_INSTRUCTION, F_PURTSIKKA + F_2014 + [PurposeFilter("KOU")], "Koululentomaksu, %(aircraft)s"),

        CappedRule(ID_KM_2014, 90, ctx,
                   AllRules([CappedRule(ID_KM_P_2014, 70, ctx,
                                         FlightRule(10, ACCT_KALUSTO, [PeriodFilter(Period.full_year(2014)),
                                                              AircraftFilter("650", "733", "787", "883", "952")],
                                                         u"Kalustomaksu, %(aircraft)s, %(duration)d min")),
                              CappedRule(ID_KM_M_2014, 70, ctx,
                                         FlightRule(10, ACCT_KALUSTO, [PeriodFilter(Period.full_year(2014)),
                                                         AircraftFilter("DDS", "CAO", "TOW"),
                                                         NegationFilter(TransferTowFilter())], # No kalustomaksu for transfer tows
                                                         u"Kalustomaksu, %(aircraft)s, %(duration)d min"))])),

        # Normal simple events
        FirstRule([SetDateRule(ID_PK_2014, ctx, SimpleRule(F_2014 + [ItemFilter(u".*[pP]ursikönttä.*")])),
                   SetDateRule(ID_KK_2014, ctx, SimpleRule(F_2014 + [ItemFilter(u".*[kK]urssikönttä.*")])),
                   SimpleRule(F_2014)]),

        FlightRule(lambda ev: 2, ACCT_LASKUTUSLISA, F_KAIKKI_KONEET + F_2014 + F_LASKUTUSLISA, u"Laskutuslisä, %(aircraft)s, %(invoicing_comment)s"),
    ]

    rules_2015 = [
        FlightRule(171, ACCT_DDS, F_DDS + F_2015),
        # Variable price for TOW in the second period, based on purpose of flight
        FirstRule([FlightRule(124, ACCT_TOWING, F_TOW + F_2015 + [TransferTowFilter()], u"Siirtohinaus, %(duration)d min"),
                   FlightRule(104, ACCT_TOW, F_TOW + F_2015)
               ]),

        pursi_rule_2015(F_2015 + F_FK, 15),
        pursi_rule_2015(F_2015 + F_FM, 25, 10),
        pursi_rule_2015(F_2015 + F_FQ, 25),
        pursi_rule_2015(F_2015 + F_FY, 32, 32, 10),
        pursi_rule_2015(F_2015 + F_DG, 40, 10, 10),
        pursi_rule_2015(F_2015 + F_TK, 25, 10, 0),

        # Koululentomaksu
        FlightRule(lambda ev: 5, ACCT_PURSI_INSTRUCTION, F_PURTSIKKA + F_2015 + [PurposeFilter("KOU")], "Koululentomaksu, %(aircraft)s"),

        CappedRule(ID_KM_2015, 90, ctx,
                   AllRules([CappedRule(ID_KM_P_2015, 70, ctx,
                                         FlightRule(10, ACCT_KALUSTO, F_2015 + F_PURTSIKKA_2015,
                                                         u"Kalustomaksu, %(aircraft)s, %(duration)d min")),
                              CappedRule(ID_KM_M_2015, 70, ctx,
                                         FlightRule(10, ACCT_KALUSTO, F_2015 + F_MOTTI,
                                                         u"Kalustomaksu, %(aircraft)s, %(duration)d min"))])),

        # Normal simple events
        FirstRule([SetDateRule(ID_PK_2015, ctx, SimpleRule(F_2015 + [ItemFilter(u".*[pP]ursikönttä.*")])),
                   SetDateRule(ID_KK_2015, ctx, SimpleRule(F_2015 + [ItemFilter(u".*[kK]urssikönttä.*")])),
                   SimpleRule(F_2015)]),

        FlightRule(lambda ev: 2, ACCT_LASKUTUSLISA, F_KAIKKI_KONEET + F_2015 + F_LASKUTUSLISA, u"Laskutuslisä, %(aircraft)s, %(invoicing_comment)s")
    ]

    rules_2016 = [
        FlightRule(171, ACCT_DDS, F_DDS + F_2016),
        # Variable price for TOW in the second period, based on purpose of flight
        FirstRule([FlightRule(124, ACCT_TOWING, F_TOW + F_2016 + [TransferTowFilter()], u"Siirtohinaus, %(duration)d min"),
                   FlightRule(104, ACCT_TOW, F_TOW + F_2016)
               ]),

        pursi_rule_2016(F_2016 + F_FK, 15),
        pursi_rule_2016(F_2016 + F_FM, 25, 10),
        pursi_rule_2016(F_2016 + F_FQ, 25),
        pursi_rule_2016(F_2016 + F_FY, 32, 32, 10),
        pursi_rule_2016(F_2016 + F_DG, 40, 10, 10),
        pursi_rule_2016(F_2016 + F_HB, 25, 10, 0),

        # Koululentomaksu
        FlightRule(lambda ev: 5, ACCT_PURSI_INSTRUCTION, F_PURTSIKKA_2016 + F_2016 + [PurposeFilter("KOU")], "Koululentomaksu, %(aircraft)s"),

        CappedRule(ID_KM_2016, 90, ctx,
                   AllRules([CappedRule(ID_KM_P_2016, 70, ctx,
                                         FlightRule(10, ACCT_KALUSTO, F_2016 + F_PURTSIKKA_2016,
                                                         u"Kalustomaksu, %(aircraft)s, %(duration)d min")),
                              CappedRule(ID_KM_M_2016, 70, ctx,
                                         FlightRule(10, ACCT_KALUSTO, F_2016 + F_MOTTI,
                                                         u"Kalustomaksu, %(aircraft)s, %(duration)d min"))])),

        # Normal simple events
        FirstRule([SetDateRule(ID_PK_2016, ctx, SimpleRule(F_2016 + [ItemFilter(u".*[pP]ursikönttä.*")])),
                   SetDateRule(ID_KK_2016, ctx, SimpleRule(F_2016 + [ItemFilter(u".*[kK]urssikönttä.*")])),
                   SimpleRule(F_2016)]),

        FlightRule(lambda ev: 2, ACCT_LASKUTUSLISA, F_KAIKKI_KONEET + F_2016 + F_LASKUTUSLISA, u"Laskutuslisä, %(aircraft)s, %(invoicing_comment)s")
    ]

    rules_2017 = [
        FlightRule(171, ACCT_DDS, F_DDS + F_2017),
        # Variable price for TOW in the second period, based on purpose of flight
        FirstRule([FlightRule(124, ACCT_TOWING, F_TOW + F_2017 + [TransferTowFilter()], u"Siirtohinaus, %(duration)d min"),
                   FlightRule(104, ACCT_TOW, F_TOW + F_2017)
               ]),

        pursi_rule_2017(F_2017 + F_FK, 15),
        pursi_rule_2017(F_2017 + F_FM, 25, 10),
        pursi_rule_2017(F_2017 + F_FQ, 25),
        pursi_rule_2017(F_2017 + F_FY, 32, 32, 10),
        pursi_rule_2017(F_2017 + F_DG, 40, 10, 10),

        # Koululentomaksu
        FlightRule(lambda ev: 5, ACCT_PURSI_INSTRUCTION, F_PURTSIKKA_2017 + F_2017 + [PurposeFilter("KOU")], "Koululentomaksu, %(aircraft)s"),

        CappedRule(ID_KM_2017, 90, ctx,
                   AllRules([CappedRule(ID_KM_P_2017, 70, ctx,
                                         FlightRule(10, ACCT_KALUSTO, F_2017 + F_PURTSIKKA_2017,
                                                         u"Kalustomaksu, %(aircraft)s, %(duration)d min")),
                              CappedRule(ID_KM_M_2017, 70, ctx,
                                         FlightRule(10, ACCT_KALUSTO, F_2017 + F_MOTTI,
                                                         u"Kalustomaksu, %(aircraft)s, %(duration)d min"))])),

        # Normal simple events
        FirstRule([SetDateRule(ID_PK_2017, ctx, SimpleRule(F_2017 + [ItemFilter(u".*[pP]ursikönttä.*")])),
                   SetDateRule(ID_KK_2017, ctx, SimpleRule(F_2017 + [ItemFilter(u".*[kK]urssikönttä.*")])),
                   SimpleRule(F_2017)]),

        FlightRule(lambda ev: 2, ACCT_LASKUTUSLISA, F_KAIKKI_KONEET + F_2017 + F_LASKUTUSLISA, u"Laskutuslisä, %(aircraft)s, %(invoicing_comment)s")
    ]
    
    # Added 2018-11-07:
    rules_2018 = [
        FlightRule(171, ACCT_DDS, F_DDS + F_2018),
        # Variable price for TOW in the second period, based on purpose of flight
        FirstRule([FlightRule(129, ACCT_TOWING, F_TOW + F_2018 + [TransferTowFilter()], u"Siirtohinaus, %(duration)d min"),
                   FlightRule(129, ACCT_TOW, F_TOW + F_2018)
               ]),

        pursi_rule_2018(F_2018 + F_FK, 15),
        pursi_rule_2018(F_2018 + F_FM, 25, 10),
        pursi_rule_2018(F_2018 + F_FQ, 25),
        pursi_rule_2018(F_2018 + F_FY, 32, 32, 10),
        pursi_rule_2018(F_2018 + F_DG, 40, 10, 10),

        # Koululentomaksu
        FlightRule(lambda ev: 5, ACCT_PURSI_INSTRUCTION, F_PURTSIKKA_2018 + F_2018 + [PurposeFilter("KOU")], "Koululentomaksu, %(aircraft)s"),

        CappedRule(ID_KM_2018, 90, ctx,
                   AllRules([CappedRule(ID_KM_P_2018, 70, ctx,
                                         FlightRule(10, ACCT_KALUSTO, F_2018 + F_PURTSIKKA_2018,
                                                         u"Kalustomaksu, %(aircraft)s, %(duration)d min")),
                              CappedRule(ID_KM_M_2018, 70, ctx,
                                         FlightRule(10, ACCT_KALUSTO, F_2018 + F_MOTTI,
                                                         u"Kalustomaksu, %(aircraft)s, %(duration)d min"))])),

        # Normal simple events
        FirstRule([SetDateRule(ID_PK_2018, ctx, SimpleRule(F_2018 + [ItemFilter(u".*[pP]ursikönttä.*")])),
                   SetDateRule(ID_KK_2018, ctx, SimpleRule(F_2018 + [ItemFilter(u".*[kK]urssikönttä.*")])),
                   SimpleRule(F_2018)]),

        FlightRule(lambda ev: 2, ACCT_LASKUTUSLISA, F_KAIKKI_KONEET + F_2018 + F_LASKUTUSLISA, u"Laskutuslisä, %(aircraft)s, %(invoicing_comment)s")
    ]
    
    # Added 2019-10-08:
    rules_2019 = [
        FlightRule(171, ACCT_DDS, F_DDS + F_2019),
        # Variable price for TOW in the second period, based on purpose of flight
        FirstRule([FlightRule(129, ACCT_TOWING, F_TOW + F_2019), # + [TransferTowFilter()], u"Siirtohinaus, %(duration)d min"
                   FlightRule(129, ACCT_TOW, F_TOW + F_2019)
               ]),

        pursi_rule_2019(F_2019 + F_FK, 15),
        pursi_rule_2019(F_2019 + F_FM, 25, 10),
        pursi_rule_2019(F_2019 + F_FQ, 25),
        pursi_rule_2019(F_2019 + F_FY, 32, 32, 10),
        pursi_rule_2019(F_2019 + F_FI, 28, 28),
        pursi_rule_2019(F_2019 + F_DG, 40, 10, 10),

        # Koululentomaksu
        FlightRule(lambda ev: 5, ACCT_PURSI_INSTRUCTION, F_PURTSIKKA_2019 + F_2019 + [PurposeFilter("KOU")], "Koululentomaksu, %(aircraft)s"),

        CappedRule(ID_KM_2019, 90, ctx,
                   AllRules([CappedRule(ID_KM_P_2019, 70, ctx,
                                         FlightRule(10, ACCT_KALUSTO, F_2019 + F_PURTSIKKA_2019,
                                                         u"Kalustomaksu, %(aircraft)s, %(duration)d min")),
                              CappedRule(ID_KM_M_2019, 70, ctx,
                                         FlightRule(10, ACCT_KALUSTO, F_2019 + F_MOTTI,
                                                         u"Kalustomaksu, %(aircraft)s, %(duration)d min"))])),

        # Normal simple events
        FirstRule([SetDateRule(ID_PK_2019, ctx, SimpleRule(F_2019 + [ItemFilter(u".*[pP]ursikönttä.*")])),
                   SetDateRule(ID_KK_2019, ctx, SimpleRule(F_2019 + [ItemFilter(u".*[kK]urssikönttä.*")])),
                   SimpleRule(F_2019)]),

        FlightRule(lambda ev: 2, ACCT_LASKUTUSLISA, F_KAIKKI_KONEET + F_2019 + F_LASKUTUSLISA, u"Laskutuslisä, %(aircraft)s, %(invoicing_comment)s")
    ]
    
    return rules_past + [SetLedgerYearRule(AllRules(rules_2014), 2014),
                         SetLedgerYearRule(AllRules(rules_2015), 2015),
                         SetLedgerYearRule(AllRules(rules_2016), 2016),
                         SetLedgerYearRule(AllRules(rules_2017), 2017),
                         SetLedgerYearRule(AllRules(rules_2018), 2018),
                         SetLedgerYearRule(AllRules(rules_2019), 2019)]


def events_to_lines(events, rules):
    for event in events:
        match = False
        for rule in rules:
            for line in rule.invoice(event):
                match = True
                yield line
        if not match:
            print >> sys.stderr, "No match for event", event.__repr__()

def grouped_lines(lines):
    by_account = defaultdict(lambda: [])
    for line in lines:
        k = line.account_id.upper()
        if any(k.startswith(prefix) for prefix in conf['no_invoicing_prefix']):
            continue
        by_account[line.account_id].append(line)
    return by_account

def events_to_invoices(events, rules, invoice_date=dt.date.today()):
    by_account = grouped_lines(events_to_lines(events, rules))
    for account in sorted(by_account.keys()):
        lines = sorted(by_account[account], key=lambda line: line.date)
        yield Invoice(account, invoice_date, lines)


def write_invoices_to_files(invoices, conf):
    out_dir = conf["out_dir"]
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    invoice_format_id = conf.get("invoice_format", "2015")
    for invoice in invoices:
        account = invoice.account_id
        with open(os.path.join(out_dir, account + ".txt"), "wb") as f:
            f.write(format_invoice(invoice, conf["description"], invoice_format_id).encode("utf-8"))

def write_hansa_export_file(valid_invoices, invalid_invoices, conf):
    out_dir = conf["out_dir"]
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    dates = map(parse_iso8601_date, conf['hansa_txn_dates'])
    hansa_txn_date_filter = PeriodFilter(Period(*dates))

    hansa_txns = []
    hansa_txn_id_gen = count(conf["hansa_first_txn_id"])
    for invoice in invoices:
        lines_by_rule = defaultdict(lambda: [])
        for line in invoice.lines:
            if hansa_txn_date_filter(line):
                lines_by_rule[line.rule].append(line)

        for (rule, lineset) in lines_by_rule.iteritems():
            # Check all lines have same sign
            signs = [math.copysign(line.price, 1) for line in lineset]
            
            if not (all(sign >= 0 for sign in signs) or all(sign <= 0 for sign in signs)):
                print >> sys.stderr, "Inconsistent signs:", lineset, signs, all(sign >= 0 for sign in signs), all(sign <= 0 for sign in signs)

            # Check all lines have same ledger account, excluding lines that don't go
            # into ledger via this process (they have None as ledger_account_id)
            ledger_accounts = set(line.ledger_account_id for line in lineset) - set([None])
            if len(ledger_accounts) > 1 and not rule.allow_multiple_ledger_categories:
                print >> sys.stderr, u"Inconsistent ledger accounts:", u", ".join(unicode(l) for l in lineset), ledger_accounts
                
        hansa_rows = []
        for lineset in lines_by_rule.values():
            extract_lai = lambda x: x.ledger_account_id
            for (ledger_account_id, lines) in groupby(sorted(lineset, key=extract_lai), key=extract_lai):
                lines = list(lines)
                if not ledger_account_id:
                    continue
            
                total_price = sum(line.price for line in lines if line.ledger_account_id)
                if total_price == 0:
                    continue
            
                title = os.path.commonprefix([line.item for line in lines])
                if total_price > 0:
                    member_line = SimpleHansaRow(1422, title, debit=total_price)
                    club_line = SimpleHansaRow(ledger_account_id, title, credit=total_price)
                else:
                    member_line = SimpleHansaRow(1422, title, credit=total_price)
                    club_line = SimpleHansaRow(ledger_account_id, title, debit=total_price)
                hansa_rows.append(club_line)
                hansa_rows.append(member_line)

        hansa_rows.sort()

        if hansa_rows:
            hansa_id = hansa_txn_id_gen.next()
            hansa_txn = SimpleHansaTransaction(hansa_id, conf["hansa_year"], conf["hansa_entry_date"], conf["hansa_txn_date"], "Lentolasku, " + invoice.account_id, invoice.account_id, hansa_rows)
            hansa_txns.append(hansa_txn)

    with open(os.path.join(out_dir, "hansa-export-" + conf["invoice_date"] + ".txt"), "wb") as f:
        for txn in hansa_txns:
            f.write(unicodedata.normalize("NFC", txn.hansaformat()).encode("iso-8859-1"))

def write_total_csv(invoices, fname):
    import csv
    writer = csv.writer(open(fname, 'wb'))
    writer.writerows(invoice.to_csvrow_total() for invoice in invoices)

def write_row_csv(invoices, fname_template):
    import unicodecsv
    by_year = defaultdict(lambda: [])
    for invoice in invoices:
        for line in invoice.lines:
            if not line.rollup:
                row = line.to_csvrow()
                by_year[row.ledger_year].append(row)
    for year, yearly_rowset in by_year.iteritems():
        writer = unicodecsv.writer(open(fname_template%year, 'wb'), encoding='utf-8')
        writer.writerows(yearly_rowset)

def is_invoice_zero(invoice):
    return abs(invoice.total()) < 0.01

def make_event_validator(pik_ids, external_ids):
    def event_validator(event):
        if not isinstance(event.account_id, str):
            raise ValueError(u"Account id must be string, was: " + repr(event.account_id) + u" in " + unicode(event))
        if not ((event.account_id in pik_ids and len(event.account_id) in (4,6)) or
                event.account_id in external_ids):
            raise ValueError("Invalid id was: " + repr(event.account_id) + " in " + unicode(event).encode("utf-8"))
        return event
    return event_validator

def read_pik_ids(fnames):
    result = []
    for fname in fnames:
        result.extend(x.strip() for x in open(fname, 'rb').readlines() if x.strip())
    return result

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Usage: invoice-flights.py <conf-file>"
        sys.exit(1)
    conf = json.load(open(sys.argv[1], 'rb'))

    sources = []

    ctx = BillingContext()
    if "context_file_in" in conf:
        context_file = conf["context_file_in"]
        if os.path.isfile(context_file):
            ctx = BillingContext.from_json(json.load(open(context_file, "r")))
    rules = make_rules(ctx)

    for fname in conf['event_files']:
        reader = csv.reader(open(fname, 'rb'))
        sources.append(SimpleEvent.generate_from_csv(reader))

    for fname in conf['flight_files']:
        reader = csv.reader(open(fname, "rb"))
        sources.append(Flight.generate_from_csv(reader))

    for fname in conf['nda_files']:
        bank_txn_date_filter = lambda txn_date: True
        if 'bank_txn_dates' in conf:
            dates = map(parse_iso8601_date, conf['bank_txn_dates'])
            bank_txn_date_filter = PeriodFilter(Period(*dates))

        reader = nda.transactions(open(fname, 'rb'))
        # Only PIK references and incoming transactions - note that the conversion reverses the sign of the sum, since incoming money reduces the account's debt
        sources.append(SimpleEvent.generate_from_nda(reader, ["FI2413093000112458"], lambda event: bank_txn_date_filter(event) and event.cents > 0 and event.ref and (len(event.ref) == 4 or len(event.ref) == 6)))

    invoice_date = parse_iso8601_date(conf['invoice_date'])
    event_validator = make_event_validator(read_pik_ids(conf['valid_id_files']), conf['no_invoicing_prefix'])
    events = list(sorted(chain(*sources), key=lambda event: event.date))
    for event in events:
        try:
            event_validator(event)
        except ValueError, e:
            print >> sys.stderr, "Invalid account id", event.account_id, unicode(event)

    invoices = list(events_to_invoices(events, rules, invoice_date=invoice_date))

    valid_invoices = [i for i in invoices if not is_invoice_zero(i)]
    invalid_invoices = [i for i in invoices if is_invoice_zero(i)]

    out_dir = conf["out_dir"]
    if os.path.exists(out_dir):
        raise ValueError("out_dir already exists: " + out_dir)

    total_csv_fname = conf.get("total_csv_name", os.path.join(out_dir, "totals.csv"))
    row_csv_fname_template = conf.get("row_csv_name_template", os.path.join(out_dir, "rows_%s.csv"))

    write_invoices_to_files(valid_invoices, conf)
    write_invoices_to_files(invalid_invoices, conf)
    write_hansa_export_file(valid_invoices, invalid_invoices, conf)
    write_total_csv(invoices, total_csv_fname)
    write_row_csv(invoices, row_csv_fname_template)
    if "context_file_out" in conf:
        json.dump(ctx.to_json(), open(conf["context_file_out"], "w"))

    machine_readable_invoices = [invoice.to_json() for invoice in invoices]

    #print json.dumps(machine_readable_invoices)

    invalid_account = []
    invalid_sum = []

    print >> sys.stderr, "Difference, valid invoices, total", sum(i.total() for i in valid_invoices)
    print >> sys.stderr, "Owed to club, invoices, total", sum(i.total() for i in valid_invoices if i.total() > 0)
    print >> sys.stderr, "Owed by club, invoices, total", sum(i.total() for i in valid_invoices if i.total() < 0)

    print >> sys.stderr, "Zero invoices, count ", len(invalid_invoices)

