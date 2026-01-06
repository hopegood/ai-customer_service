import logging
import traceback

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    try:
        i = 10 / 0
    except Exception as e:
        #logger.error(f"执行出错!{e}")
        logger.error(f"执行出错! {e}\n{traceback.format_exc()}")
    logger.info("这是一个测试日志")
