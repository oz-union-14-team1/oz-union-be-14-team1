import functools
import time
from django.db import connection, reset_queries


def query_debugger(func):
    """
    함수 실행 시 발생한 SQL 쿼리 개수와 실행 시간을 출력하는 데코레이터
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        reset_queries()  # 쿼리 로그 초기화
        start_time = time.time()
        start_queries = len(connection.queries)

        result = func(*args, **kwargs)

        end_queries = len(connection.queries)
        end_time = time.time()

        print(f"\n[Query Debugger] '{func.__name__}'")
        print(f" - Execution Time: {(end_time - start_time):.4f}s")
        print(f" - Number of Queries: {end_queries - start_queries}")

        # 실제 발생한 쿼리문 출력 (필요 시 주석 해제)
        # for i, query in enumerate(connection.queries[start_queries:], 1):
        #     print(f" {i}. {query['sql']}")
        print("=" * 30 + "\n")

        return result

    return wrapper
