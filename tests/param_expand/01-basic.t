#!/bin/bash
# THIS FILE IS PART OF THE CYLC SUITE ENGINE.
# Copyright (C) 2008-2017 NIWA
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------
# Check tasks and graph generated by parameter expansion.
. "$(dirname "$0")/test_header"
set_test_number 20

cat >'suite.rc' <<'__SUITE__'
[cylc]
    [[parameters]]
        i = cat, dog, fish
        j = 1..5
        k = 1..10..4
[scheduling]
    [[dependencies]]
        graph = """
foo<i> => bar<j>
qux<j> => waz<k>
"""
[runtime]
    [[root]]
        script = true
    [[foo<i>]]
    [[bar<j>]]
    [[qux<j>]]
    [[waz<k>]]
__SUITE__

run_ok "${TEST_NAME_BASE}-1" cylc validate "suite.rc"
cylc graph --reference 'suite.rc' >'1.graph'
cmp_ok "${TEST_SOURCE_DIR}/${TEST_NAME_BASE}/1.graph.ref" '1.graph'

cat >'suite.rc' <<'__SUITE__'
[cylc]
    [[parameters]]
        i = 25, 30..35, 1..5, 110
[scheduling]
    [[dependencies]]
        graph = """
foo<i> => bar<i>
"""
[runtime]
    [[root]]
        script = true
    [[foo<i>]]
    [[bar<i>]]
__SUITE__

run_ok "${TEST_NAME_BASE}-2" cylc validate "suite.rc"
cylc graph --reference 'suite.rc' >'2.graph'
cmp_ok "${TEST_SOURCE_DIR}/${TEST_NAME_BASE}/2.graph.ref" '2.graph'

cat >'suite.rc' <<'__SUITE__'
[cylc]
    [[parameters]]
        i = a-t, c-g
[scheduling]
    [[dependencies]]
        graph = """
foo<i> => bar<i>
"""
[runtime]
    [[root]]
        script = true
    [[foo<i>]]
    [[bar<i>]]
__SUITE__

run_ok "${TEST_NAME_BASE}-3" cylc validate "suite.rc"
cylc graph --reference 'suite.rc' >'3.graph'
cmp_ok "${TEST_SOURCE_DIR}/${TEST_NAME_BASE}/3.graph.ref" '3.graph'

cat >'suite.rc' <<'__SUITE__'
[cylc]
    [[parameters]]
        i = 100, hundred, one-hundred, 99+1
[scheduling]
    [[dependencies]]
        graph = """
foo<i> => bar<i>
"""
[runtime]
    [[root]]
        script = true
    [[foo<i>]]
    [[bar<i>]]
__SUITE__

run_ok "${TEST_NAME_BASE}-4" cylc validate "suite.rc"
cylc graph --reference 'suite.rc' >'4.graph'
cmp_ok "${TEST_SOURCE_DIR}/${TEST_NAME_BASE}/4.graph.ref" '4.graph'

cat >'suite.rc' <<'__SUITE__'
[cylc]
    [[parameters]]
        i = space is dangerous
[scheduling]
    [[dependencies]]
        graph = """
foo<i> => bar<i>
"""
[runtime]
    [[root]]
        script = true
    [[foo<i>]]
    [[bar<i>]]
__SUITE__

run_fail "${TEST_NAME_BASE}-5" cylc validate "suite.rc"
cmp_ok "${TEST_NAME_BASE}-5.stderr" <<'__ERR__'
Illegal parameter value: [cylc][parameters]i = space is dangerous: space is dangerous: bad value
__ERR__

cat >'suite.rc' <<'__SUITE__'
[cylc]
    [[parameters]]
        i = mix, 1..10
[scheduling]
    [[dependencies]]
        graph = """
foo<i> => bar<i>
"""
[runtime]
    [[root]]
        script = true
    [[foo<i>]]
    [[bar<i>]]
__SUITE__

run_fail "${TEST_NAME_BASE}-6" cylc validate "suite.rc"
cmp_ok "${TEST_NAME_BASE}-6.stderr" <<'__ERR__'
Illegal parameter value: [cylc][parameters]i = mix, 1..10: mixing int range and str
__ERR__

cat >'suite.rc' <<'__SUITE__'
[cylc]
    [[parameters]]
        i = a, b #, c, d, e  # comment
[scheduling]
    [[dependencies]]
        graph = """
foo<i> => bar<i>
"""
[runtime]
    [[root]]
        script = true
    [[foo<i>]]
    [[bar<i>]]
__SUITE__

run_ok "${TEST_NAME_BASE}-7" cylc validate "suite.rc"
cylc graph --reference 'suite.rc' >'7.graph'
cmp_ok "${TEST_SOURCE_DIR}/${TEST_NAME_BASE}/7.graph.ref" '7.graph'

cat >'suite.rc' <<'__SUITE__'
[cylc]
    [[parameters]]
        i = 1..2 3..4
[scheduling]
    [[dependencies]]
        graph = """
foo<i> => bar<i>
"""
[runtime]
    [[root]]
        script = true
    [[foo<i>]]
    [[bar<i>]]
__SUITE__

run_fail "${TEST_NAME_BASE}-8" cylc validate "suite.rc"
cmp_ok "${TEST_NAME_BASE}-8.stderr" <<'__ERR__'
Illegal parameter value: [cylc][parameters]i = 1..2 3..4: 1..2 3..4: bad value
__ERR__

cat >'suite.rc' <<'__SUITE__'
[cylc]
    [[parameters]]
        i =
[scheduling]
    [[dependencies]]
        graph = """
foo<i> => bar<i>
"""
[runtime]
    [[root]]
        script = true
    [[foo<i>]]
    [[bar<i>]]
__SUITE__

run_fail "${TEST_NAME_BASE}-9" cylc validate "suite.rc"
cmp_ok "${TEST_NAME_BASE}-9.stderr" <<'__ERR__'
ERROR, parameter i is not defined in foo<i>
__ERR__

cat >'suite.rc' <<'__SUITE__'
[scheduling]
    [[dependencies]]
        graph = """
foo<i> => bar<i>
"""
[runtime]
    [[root]]
        script = true
    [[foo<i>]]
    [[bar<i>]]
__SUITE__

run_fail "${TEST_NAME_BASE}-9" cylc validate "suite.rc"
cmp_ok "${TEST_NAME_BASE}-9.stderr" <<'__ERR__'
ERROR, parameter i is not defined in <i>: foo<i>=>bar<i>
__ERR__

exit
