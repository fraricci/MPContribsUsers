# -*- coding: utf-8 -*-
import os, urllib, ase.db
from mpcontribs.io.core.recdict import RecursiveDict
from mpcontribs.io.core.utils import nest_dict
from mpcontribs.users.utils import clean_value, duplicate_check

@duplicate_check
def run(mpfile, **kwargs):

    url = mpfile.hdata.general['url']
    dbfile = os.path.join(os.environ['HOME'], 'work', url.rsplit('/')[-1])

    if not os.path.exists(dbfile):
        data = urllib.URLopener()
        data.retrieve(url, dbfile)

    con = ase.db.connect(dbfile)
    nr_mpids = con.count(selection='mpid')

    for idx, row in enumerate(con.select('mpid')):
        if idx and not idx%10:
            print 'added', idx, '/', nr_mpids, 'materials'
        mpid = 'mp-' + str(row.mpid)
        d = RecursiveDict()

        # kohn-sham band gap
        d[u'ΔE-KS'] = RecursiveDict([
            ('indirect', clean_value(
                row.gllbsc_ind_gap - row.gllbsc_disc, 'eV'
            )), ('direct', clean_value(
                row.gllbsc_dir_gap - row.gllbsc_disc, 'eV'
            ))
        ])

        # derivative discontinuity
        d['C'] = clean_value(row.gllbsc_disc, 'eV')

        # quasi particle band gap
        d[u'ΔE-QP'] = RecursiveDict([
            ('indirect', clean_value(row.gllbsc_ind_gap, 'eV')),
            ('direct', clean_value(row.gllbsc_dir_gap, 'eV'))
        ])

        mpfile.add_hierarchical_data(
            nest_dict(d, ['data']), identifier=mpid
        )
