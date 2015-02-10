#!/usr/bin/env python

from __future__ import print_function
from __future__ import unicode_literals

import datetime
import dateutil.tz
try:
    from unittest import mock
except ImportError:
    import mock
import pytest

from tdclient import model
from tdclient.test.test_helper import *

def setup_function(function):
    unset_environ()

def test_account():
    client = mock.MagicMock()
    account = model.Account(client, 1, 2, storage_size=3456, guaranteed_cores=7, maximum_cores=8, created_at="created_at")
    assert account.account_id == 1
    assert account.plan == 2
    assert account.storage_size == 3456
    assert account.guaranteed_cores == 7
    assert account.maximum_cores == 8
    assert account.created_at == "created_at"

def test_account_storage_size_string():
    client = mock.MagicMock()
    account1 = model.Account(client, 1, 1, storage_size=0)
    assert account1.storage_size_string == "0.0 GB"
    account2 = model.Account(client, 1, 1, storage_size=50*1024*1024)
    assert account2.storage_size_string == "0.01 GB"
    account3 = model.Account(client, 1, 1, storage_size=50*1024*1024*1024)
    assert account3.storage_size_string == "50.0 GB"
    account4 = model.Account(client, 1, 1, storage_size=300*1024*1024*1024)
    assert account4.storage_size_string == "300 GB"

def test_database():
    client = mock.MagicMock()
    database = model.Database(client, "sample_datasets", tables=["nasdaq", "www_access"], count=12345, created_at="created_at", updated_at="updated_at", org_name="org_name", permission="administrator")
    assert database.org_name == "org_name"
    assert database.permission == "administrator"
    assert database.count == 12345
    assert database.name == "sample_datasets"
    assert database.tables() == ["nasdaq", "www_access"]
    assert database.created_at == "created_at"
    assert database.updated_at == "updated_at"

def test_database_update_tables():
    client = mock.MagicMock()
    client.tables = mock.MagicMock(return_value=[
        model.Table(client, "sample_datasets", "foo", "type", "schema", "count"),
        model.Table(client, "sample_datasets", "bar", "type", "schema", "count"),
        model.Table(client, "sample_datasets", "baz", "type", "schema", "count"),
    ])
    database = model.Database(client, "sample_datasets", tables=None, count=12345, created_at="created_at", updated_at="updated_at", org_name="org_name", permission="administrator")
    tables = database.tables()
    assert [ table.name for table in tables ] == ["foo", "bar", "baz"]
    client.tables.assert_called_with("sample_datasets")

def test_table():
    client = mock.MagicMock()
    table = model.Table(client, "db_name", "table_name", "type", "schema", 12345, created_at="created_at", updated_at="updated_at", estimated_storage_size=67890, last_import="last_import", last_log_timestamp="last_log_timestamp", expire_days="expire_days", primary_key="primary_key", primary_key_type="primary_key_type")
    assert table.type == "type"
    assert table.db_name == "db_name"
    assert table.table_name == "table_name"
    assert table.schema == "schema"
    assert table.count == 12345
    assert table.estimated_storage_size == 67890
    assert table.primary_key == "primary_key"
    assert table.primary_key_type == "primary_key_type"
    assert table.database_name == "db_name"
    assert table.name == "table_name"
    assert table.created_at == "created_at"
    assert table.updated_at == "updated_at"
    assert table.last_import == "last_import"
    assert table.last_log_timestamp == "last_log_timestamp"
    assert table.expire_days == "expire_days"
    assert table.identifier == "db_name.table_name"

def test_table_permission():
    client = mock.MagicMock()
    table = model.Table(client, "sample_datasets", "nasdaq", "log", "schema", 12345)
    client.database().permission = "permission"
    assert table.permission == "permission"
    client.database.assert_called_with("sample_datasets")

def test_table_estimated_storage_size_string():
    client = mock.MagicMock()
    table1 = model.Table(client, "db_name", "table_name", "type", "schema", 12345, estimated_storage_size=1)
    assert table1.estimated_storage_size_string == "0.0 GB"
    table2 = model.Table(client, "db_name", "table_name", "type", "schema", 12345, estimated_storage_size=50*1024*1024)
    assert table2.estimated_storage_size_string == "0.01 GB"
    table3 = model.Table(client, "db_name", "table_name", "type", "schema", 12345, estimated_storage_size=50*1024*1024*1024)
    assert table3.estimated_storage_size_string == "50.0 GB"
    table4 = model.Table(client, "db_name", "table_name", "type", "schema", 12345, estimated_storage_size=300*1024*1024*1024)
    assert table4.estimated_storage_size_string == "300 GB"

def test_schema():
    client = mock.MagicMock()
    job = model.Job(client, "job_id", "type", "query", status="status", url="url", debug="debug", start_at="start_at", end_at="end_at", cpu_time="cpu_time", result_size="result_size", result="result", result_url="result_url", hive_result_schema="hive_result_schema", priority="priority", retry_limit="retry_limit", org_name="org_name", db_name="db_name")
    assert job.id == "job_id"
    assert job.job_id == "job_id"
    assert job.type == "type"
    assert job.result_url == "result_url"
    assert job.priority == "priority"
    assert job.retry_limit == "retry_limit"
    assert job.org_name == "org_name"
    assert job.db_name == "db_name"

def test_job_wait_success():
    client = mock.MagicMock()
    job = model.Job(client, "12345", "presto", "SELECT COUNT(1) FROM nasdaq")
    job.finished = mock.MagicMock(side_effect=[
        False,
        True,
    ])
    with mock.patch("time.time") as t_time:
        t_time.side_effect = [
            1423570800.0,
            1423570860.0,
            1423570920.0,
            1423570980.0,
        ]
        with mock.patch("time.sleep") as t_sleep:
            job.wait(timeout=120)
            assert t_sleep.called
        assert t_time.called
    assert job.finished.called

def test_job_wait_failure():
    client = mock.MagicMock()
    job = model.Job(client, "12345", "presto", "SELECT COUNT(1) FROM nasdaq")
    job.finished = mock.MagicMock(return_value=False)
    with mock.patch("time.time") as t_time:
        t_time.side_effect = [
            1423570800.0,
            1423570860.0,
            1423570920.0,
            1423570980.0,
        ]
        with mock.patch("time.sleep") as t_sleep:
            with pytest.raises(RuntimeError) as error:
                job.wait(timeout=120)
                assert t_sleep.called
        assert t_time.called
    assert job.finished.called

def test_job_update_progress():
    client = mock.MagicMock()
    responses = [
        "queued",
        "booting",
        "running",
        "success",
    ]
    client.job_status = mock.MagicMock()
    client.job_status.side_effect = responses
    job = model.Job(client, "12345", "presto", "SELECT COUNT(1) FROM nasdaq")
    assert not job.finished()
    assert not job.finished()
    assert not job.finished()
    assert job.finished()
    client.job_status.assert_called_with("12345")

def test_job_update_status():
    client = mock.MagicMock()
    client.api.show_job = mock.MagicMock(return_value={
        "job_id": "67890",
        "type": "hive",
        "url": "http://console.example.com/jobs/67890",
        "query": "SELECT COUNT(1) FROM nasdaq",
        "status": "success",
        "debug": None,
        "start_at": datetime.datetime(2015, 2, 10, 0, 2, 14, tzinfo=dateutil.tz.tzutc()),
        "end_at": datetime.datetime(2015, 2, 10, 0, 2, 27, tzinfo=dateutil.tz.tzutc()),
        "cpu_time": None,
        "result_size": 22,
        "result": None,
        "result_url": None,
        "hive_result_schema": [["cnt", "bigint"]],
        "priority": 1,
        "retry_limit": 0,
        "org_name": None,
        "database": "sample_datasets",
    })
    job = model.Job(client, "67890", "hive", "SELECT COUNT(1) FROM nasdaq")
    job.finished = mock.MagicMock(return_value=False)
    assert job.status() == "success"
    client.api.show_job.assert_called_with("67890")

def test_scheduled_job():
    client = mock.MagicMock()
    schedule = model.Schedule(client, "name", "cron", "query", database="database", result_url="result_url", timezone="timezone", delay="delay", next_time="next_time", priority="priority", retry_limit="retry_limit", org_name="org_name")
    assert schedule.name == "name"
    assert schedule.cron == "cron"
    assert schedule.query == "query"
    assert schedule.database == "database"
    assert schedule.result_url == "result_url"
    assert schedule.timezone == "timezone"
    assert schedule.delay == "delay"
    assert schedule.priority == "priority"
    assert schedule.retry_limit == "retry_limit"
    assert schedule.org_name == "org_name"

def test_result():
    client = mock.MagicMock()
    result = model.Result(client, "name", "url", "org_name")
    assert result.name == "name"
    assert result.url == "url"
    assert result.org_name == "org_name"

def test_bulk_import():
    client = mock.MagicMock()
    bulk_import = model.BulkImport(client, name="name", database="database", table="table", status="status", upload_frozen="upload_frozen", job_id="job_id", valid_records="valid_records", error_records="error_records", valid_parts="valid_parts", error_parts="error_parts")
    assert bulk_import.name == "name"
    assert bulk_import.database == "database"
    assert bulk_import.table == "table"
    assert bulk_import.status == "status"
    assert bulk_import.job_id == "job_id"
    assert bulk_import.valid_records == "valid_records"
    assert bulk_import.error_records == "error_records"
    assert bulk_import.valid_parts == "valid_parts"
    assert bulk_import.error_parts == "error_parts"
    assert bulk_import.upload_frozen == "upload_frozen"

def test_user():
    client = mock.MagicMock()
    user = model.User(client, "name", "org_name", ["role1", "role2"], "email")
    assert user.name == "name"
    assert user.org_name == "org_name"
    assert user.role_names == ["role1", "role2"]
    assert user.email == "email"

def test_access_control():
    client = mock.MagicMock()
    access_control = model.AccessControl(client, "subject", "action", "scope", "grant_option")
    assert access_control.subject == "subject"
    assert access_control.action == "action"
    assert access_control.scope == "scope"
    assert access_control.grant_option == "grant_option"
