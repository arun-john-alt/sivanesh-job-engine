import copy
import datetime as dt
import unittest
from scripts import opening_pool as pool, daily_scan

NOW = dt.datetime.fromisoformat('2026-10-22T10:00:00+00:00')


def vacancy(ident=1, **changes):
    return {'applyUrl': f'https://jobs.example.com/{ident}',
            'analysisStatus': 'reviewed', 'score': [1]*5,
            'lastConfirmedOpenAt': NOW.isoformat(), **changes}


class OpeningPoolTests(unittest.TestCase):
    def setUp(self):
        self.cfg = {'minimumTargetLpa': 25, 'openingPool': {'minimum': 20, 'buffer': 25},
                    'employerBoards': [{'kind': 'workday', 'slug': 'example', 'searchTerms': ['Chennai']}],
                    'reserveEmployerBoards': [{'kind': 'smart', 'slug': str(i)} for i in range(20)],
                    'maxDiscoveryQueries': 4}

    def test_only_eligible_fresh_scored_vacancies_count(self):
        old = (NOW-dt.timedelta(hours=48)).isoformat()
        future = (NOW+dt.timedelta(seconds=1)).isoformat()
        data = {'jobs': [vacancy(1), vacancy(2, verification='closed'),
                        vacancy(3, discoveryEligible=False), vacancy(4, availabilityHold=True),
                        vacancy(5, lastConfirmedOpenAt=old), vacancy(6, lastConfirmedOpenAt=future),
                        vacancy(7, closesOn='2026-10-21'), vacancy(8, analysisStatus='needs-review', score=[]),
                        vacancy(9, salary={'kind': 'employer-disclosed', 'basis': 'Annual CTC', 'maxLpa': 24}),
                        vacancy(10, salary={'kind': 'employer-disclosed', 'basis': 'Base salary', 'maxLpa': 24}),
                        vacancy(1)]}
        counts = pool.inventory(data, self.cfg, NOW)
        self.assertEqual((counts['reviewedOpen'], counts['pendingOpen'], counts['shortfall']), (2, 1, 18))

    def test_deadline_uses_india_date_not_utc(self):
        after_midnight = dt.datetime.fromisoformat('2026-10-22T19:00:00+00:00')
        self.assertEqual(pool.inventory({'jobs': [vacancy(closesOn='2026-10-22')]}, self.cfg, after_midnight)['reviewedOpen'], 0)

    def test_expands_sources_and_region_queries_without_changing_eligibility_or_credits(self):
        original = copy.deepcopy(self.cfg)
        selected, plan = pool.plan({'jobs': []}, self.cfg, NOW)
        self.assertEqual(plan['expansionLevel'], 2)
        self.assertEqual(len(selected['employerBoards']), 21)
        self.assertIn('Oragadam', selected['employerBoards'][0]['searchTerms'])
        self.assertEqual(selected['maxDiscoveryQueries'], 4)
        self.assertEqual(selected['minimumTargetLpa'], 25)
        self.assertEqual(self.cfg, original)

    def test_buffer_causes_early_topup_and_repeated_shortfalls_escalate(self):
        data = {'jobs': [vacancy(i) for i in range(20)]}
        self.assertEqual(pool.plan(data, self.cfg, NOW)[1]['expansionLevel'], 1)
        data['jobs'].pop()
        data['run'] = {'openingPool': {'consecutiveShortfalls': 2}}
        self.assertEqual(pool.plan(data, self.cfg, NOW)[1]['expansionLevel'], 2)
        data['jobs'] = [vacancy(i) for i in range(25)]
        self.assertEqual(pool.plan(data, self.cfg, NOW)[1]['expansionLevel'], 0)

    def test_hourly_topup_does_not_repeat_paid_daily_search(self):
        data = {'jobs': [], 'run': {'scanDateIst': '2026-10-22'}}
        self.assertFalse(daily_scan.decision(data, 'schedule', now=NOW)[0])
        self.assertTrue(daily_scan.replenishment_due(data, self.cfg, 'schedule', now=NOW))
        data['run']['openingPool'] = {'lastReplenishedAt': (NOW-dt.timedelta(minutes=44)).isoformat()}
        self.assertFalse(daily_scan.replenishment_due(data, self.cfg, 'schedule', now=NOW))
        self.assertTrue(daily_scan.replenishment_due(data, self.cfg, 'schedule', now=NOW+dt.timedelta(minutes=1)))
        self.assertFalse(daily_scan.replenishment_due(data, self.cfg, 'push', now=NOW))
        self.assertTrue(daily_scan.replenishment_due(data, self.cfg, 'workflow_dispatch', requested=True, now=NOW))

    def test_healthy_pool_refreshes_six_hourly_and_overnight_shortfall_runs(self):
        data = {'jobs': [vacancy(i) for i in range(25)], 'run': {'openingPool': {'lastReplenishedAt': NOW.isoformat()}}}
        self.assertFalse(daily_scan.replenishment_due(data, self.cfg, 'schedule', now=NOW+dt.timedelta(hours=1)))
        self.assertTrue(daily_scan.replenishment_due(data, self.cfg, 'schedule', now=NOW+dt.timedelta(hours=6)))
        data['jobs'] = []
        overnight = NOW+dt.timedelta(hours=10)
        self.assertFalse(daily_scan.decision(data, 'schedule', now=overnight)[0])
        self.assertTrue(daily_scan.replenishment_due(data, self.cfg, 'schedule', now=overnight))

    def test_report_does_not_claim_pending_roles_satisfy_minimum(self):
        data = {'jobs': [vacancy(i, analysisStatus='needs-review', score=[]) for i in range(30)]}
        report = pool.record(data, self.cfg, {'expansionLevel': 2, 'boardsPlanned': 21}, NOW)
        self.assertEqual((report['status'], report['shortfall'], report['pendingOpen']), ('shortfall', 20, 30))
        self.assertEqual(report['consecutiveShortfalls'], 1)
        report = pool.record(data, self.cfg, {}, NOW)
        self.assertEqual(report['consecutiveShortfalls'], 2)
