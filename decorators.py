"""Decorators for social media political analysis"""
from timer import Timer
import functools

#  check speed of database uploads
# def function_timer():
#     # @functools.wraps(func)
#     def timer_wrapper():
#         pass


# def check_sent(word, sentences):
#     """Check if word is present in sentence list for calculating IDF (Inverse Document Frequency)"""

#     # @functools.wraps(func)
#     final = [all([w in x for w in word]) for x in sentences]
#     sent_len = [sentences[i] for i in range(0, len(final)) if final[i]]
#     return int(len(sent_len))


def debug(func):
    """Decorator for function debugging: shows process of *args and **kwargs to function completion.

    Args:
        func(*args),
        func(**kwargs)

    Returns:
        function name: func.__name__,
        arguments: *args,
        keyword arguments: **kwargs
        result: function outcome
    """
    @functools.wraps(func)
    def _debug(*args, **kwargs):
        result = func(*args, **kwargs)
        print(
            f"{func.__name__}(args: {args}, kwargs: {kwargs}) -> {result}"
        )
        return result
    return _debug



