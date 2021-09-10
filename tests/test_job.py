from feaflow.computes import SqlCompute, SqlComputeConfig
from feaflow.job import Job, JobConfig, scan_jobs_from_project
from feaflow.sinks import TableSink, TableSinkConfig
from feaflow.sources import QuerySource, QuerySourceConfig


def test_scan_jobs(example_project):
    job_confs = scan_jobs_from_project(example_project)
    assert len(job_confs) == 1

    test_job1: JobConfig = next(filter(lambda j: j.name == "test_job1", job_confs))
    assert test_job1.scheduler.schedule_interval == "0 6 * * *"
    assert test_job1.engine == "default_spark"
    assert type(test_job1.sources[0]) == QuerySourceConfig
    assert test_job1.sources[0].alias == "daily_events"
    assert type(test_job1.computes[0]) == SqlComputeConfig
    assert type(test_job1.sinks[0]) == TableSinkConfig
    assert test_job1.sinks[0].name == "feaflow_table_sink_test"


def test_construct_job(example_project):
    job_confs = scan_jobs_from_project(example_project)
    test_job1_conf: JobConfig = next(filter(lambda j: j.name == "test_job1", job_confs))

    job = Job(example_project, test_job1_conf)
    assert job.config.name == "test_job1"

    assert len(job.sources) == 1
    assert isinstance(job.sources[0], QuerySource)
    assert job.sources[0].alias == "daily_events"

    assert len(job.computes) == 1
    assert isinstance(job.computes[0], SqlCompute)
    assert "daily_amount" in job.computes[0].sql

    assert len(job.sinks) == 1
    assert isinstance(job.sinks[0], TableSink)
    assert job.sinks[0].config.name == "feaflow_table_sink_test"
