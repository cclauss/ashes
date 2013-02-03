from __future__ import unicode_literals

from ashes import AshesEnv, Template
from tests import dust_site_tests
from tests.core import OPS

DEFAULT_WIDTH = 70


def get_test_results(test_cases, env=None):
    env = env or AshesEnv()
    by_op = defaultdict(dict)
    by_test = defaultdict(dict)
    failed_memo = set()
    for op_name, op_func in OPS.items():
        for tc in test_cases:
            try:
                if tc.name in failed_memo:
                    raise SkipTest()
                elif op_func(tc, env):
                    res = 'passed'
                else:
                    res = 'failed'
            except SkipTest:
                res = 'skipped'
            except Exception as e:
                res = 'error'
                failed_memo.add(tc.name)
            by_op[op_name][tc.name] = res
            by_test[tc.name][op_name] = res

    return by_op, by_test


def get_line(title, items, twidth=20, talign='>', width=DEFAULT_WIDTH):
    if len(title) > twidth:
        title = title[:twidth - 3] + '...'
    rwidth = width - twidth
    items = items or []
    pw = rwidth / len(items)
    tmpl = '{title:{talign}{twidth}}' + ('{:^{pw}}' * len(items))
    return tmpl.format(title=title,
                       talign=talign,
                       twidth=twidth,
                       pw=pw,
                       *items)


def main(width=DEFAULT_WIDTH):
    lines = []
    headings = get_line('Dust.js site refs', OPS.keys(), talign='^')
    lines.append(headings)
    rstripped_width = len(headings.rstrip())
    lines.append('-' * (rstripped_width + 1))

    env = AshesEnv()
    for tc in dust_site_tests:
        env.register(Template(tc.name, tc.template, env=env, lazy=True))

    for tc in dust_site_tests:
        tres = tc.get_test_result(env)
        lines.append(get_line(tres.name, tres.symbols))
    print
    print '\n'.join(lines)
    print


if __name__ == '__main__':
    main()
