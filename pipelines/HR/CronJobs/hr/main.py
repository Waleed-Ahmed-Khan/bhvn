from pipelines import HRtoDWH, HealthcareDatatoDWH

hrDataJob = HRtoDWH()
healthcareDataJob = HealthcareDatatoDWH()

if __name__ == '__main__':
    try:
        hrDataJob.run_pipeline()
        healthcareDataJob.run_pipeline()
    except Exception as e:
        raise e