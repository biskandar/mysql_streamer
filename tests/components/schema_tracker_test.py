# -*- coding: utf-8 -*-
# Copyright 2016 Yelp Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from __future__ import absolute_import
from __future__ import unicode_literals

import mock
import pytest
from MySQLdb.cursors import Cursor

from replication_handler.components.base_event_handler import Table
from replication_handler.components.schema_tracker import SchemaTracker


class TestSchemaTracker(object):

    @pytest.fixture
    def base_schema_tracker(self, mock_db_connections):
        return SchemaTracker(mock_db_connections)

    @pytest.fixture
    def test_table(self):
        return "fake_table"

    @pytest.fixture
    def test_schema(self):
        return "fake_schema"

    @pytest.fixture
    def test_cluster(self):
        return "yelp_main"

    @pytest.fixture
    def show_create_query(self, test_table, test_schema):
        return "SHOW CREATE TABLE `{0}`.`{1}`".format(test_schema, test_table)

    @pytest.fixture
    def table_with_schema_changes(self, test_cluster, test_schema, test_table):
        return Table(
            cluster_name=test_cluster,
            database_name=test_schema,
            table_name=test_table
        )

    @pytest.fixture
    def mock_tracker_cursor(self, test_table, show_create_query):
        m = mock.Mock(spec=Cursor)
        m.fetchone.return_value = [test_table, show_create_query]
        return m

    def test_get_show_create_table_statement(
        self,
        mock_tracker_cursor,
        base_schema_tracker,
        show_create_query,
        test_table,
        table_with_schema_changes,
    ):
        base_schema_tracker.get_show_create_statement(table_with_schema_changes)
        assert mock_tracker_cursor.execute.call_count == 3
        assert mock_tracker_cursor.execute.call_args_list == [
            mock.call("USE {0}".format(table_with_schema_changes.database_name)),
            mock.call("SHOW TABLES LIKE \'{0}\'".format(table_with_schema_changes.table_name)),
            mock.call(show_create_query)
        ]
        assert mock_tracker_cursor.fetchone.call_count == 2
