from src.textSummarizer.pipeline.stage_01_data_ingestion import DataIngestionTrainingPipeline
from src.textSummarizer.logging import logger
from src.textSummarizer.pipeline.stage_02_data_validation import DataValidationTrainingPipeline

STAGE_NAME = "Data Ingestion stage"
try:
    logger.info(f">>>>>> {STAGE_NAME} started <<<<<<")
    data_ingestion = DataIngestionTrainingPipeline()
    data_ingestion.main()
    logger.info(f">>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
except Exception as e:
    logger.exception(e)
    raise e 


STAGE_NAME2 = "Data Validation stage"
try:
    logger.info(f">>>>>> {STAGE_NAME2} started <<<<<<")
    data_validation = DataValidationTrainingPipeline()
    data_validation.main()
    logger.info(f">>>>> stage {STAGE_NAME2} completed <<<<<<\n\nx==========x")
except Exception as e:
    logger.exception(e)
    raise e